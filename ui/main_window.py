import copy
import os.path
import time
from typing import List

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QLineEdit, \
    QPushButton, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QProgressDialog, QApplication, \
    QMessageBox
from PyQt5.QtCore import Qt
from utils.files import get_direct_subfolders_pathlib, find_file_case_insensitive, build_complete_path, \
    get_downloads_folder, get_original_folder, copy_file_to_folder, rename_file_keep_ext, sanitize_filename, \
    limit_filename_length
from utils.parse import parse_json_to_dict


class MainWindow(QMainWindow):
    wallpaper_data: []
    original_data: []

    def __init__(self):
        super().__init__()
        self.initUI()
        self.wallpaper_data = []
        self.original_data = []

    def initUI(self):
        self.setWindowTitle('Wallpaper Tool')
        self.resize(1000, 800)
        # 最小窗口大小
        self.setMinimumSize(400, 300)
        # 在屏幕居中显示
        self.move(400, 100)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 上方区域
        top_region = QFrame()
        top_region.setFrameShape(QFrame.StyledPanel)  # 给区域加个边框方便观察
        self.init_top_region(top_region)

        # 中间区域
        middle_region = QFrame()
        middle_region.setFrameShape(QFrame.StyledPanel)
        self.init_middle_region(middle_region)
        main_layout.addWidget(middle_region, stretch=6)

        # 下方区域
        bottom_region = QFrame()
        bottom_region.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_region)
        bottom_layout.setContentsMargins(10, 5, 10, 5)

        bottom_layout.addStretch()
        self.batch_export_btn = QPushButton('批量导出', self)
        self.batch_export_btn.setFixedSize(120, 35)
        self.batch_export_btn.clicked.connect(self.batch_export)
        bottom_layout.addWidget(self.batch_export_btn)

        main_layout.addWidget(top_region, stretch=1)
        main_layout.addWidget(middle_region, stretch=6)
        main_layout.addWidget(bottom_region, stretch=1)

    def init_top_region(self, region_widget):
        layout = QHBoxLayout(region_widget)
        # label 文件
        path_label = QLabel('Wallpaper Engine 文件夹路径：', self)
        # 只读输入框
        self.path_input = QLineEdit(self)
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText('请选择或指定 Wallpaper Engine 文件夹...')
        # 浏览按钮
        browse_btn = QPushButton('浏览...', self)
        browse_btn.clicked.connect(self.select_folder)
        self.path_input.textChanged.connect(self.check_input_content)
        # 扫描按钮
        self.scan_btn = QPushButton('扫描', self)
        self.scan_btn.clicked.connect(self.scan_wallpaper_dir)
        self.scan_btn.setEnabled(False)

        layout.addWidget(path_label)
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)
        layout.addWidget(self.scan_btn)

    def select_folder(self):
        selected_dir = QFileDialog.getExistingDirectory(self, '选择 Wallpaper Engine 文件夹', r'C:\Program Files (x86)\Steam\steamapps\workshop\content\431960')
        if selected_dir:
            normalized_path = os.path.normpath(selected_dir)
            self.path_input.setText(normalized_path)

    def check_input_content(self):
        content = self.path_input.text().strip()
        if content == "":
            self.scan_btn.setEnabled(False)
        else:
            self.scan_btn.setEnabled(True)

    def scan_wallpaper_dir(self):
        dir_path = self.path_input.text().strip()
        dir_path_list = get_direct_subfolders_pathlib(dir_path)

        for dir_path in dir_path_list:
            json_path = find_file_case_insensitive('project.json', dir_path)
            wallpaper_obj = parse_json_to_dict(json_path)
            build_file_path =  build_complete_path(json_path, wallpaper_obj.get('file'))
            wallpaper_obj['file'] = build_file_path
            if len(wallpaper_obj.keys()) > 0:
                self.wallpaper_data.append(wallpaper_obj)

        self.update_table_display()

    def update_table_display(self):
        self.table_widget.setRowCount(0)
        total_row = len(self.wallpaper_data)
        if total_row == 0:
            return
        self.table_widget.setRowCount(total_row)

        for row_idx, data in enumerate(self.wallpaper_data):
            contentrating = data.get('contentrating')
            file = data.get('file')
            title = data.get('title')
            type = data.get('type')
            self.add_table_row(row_idx, title, type, contentrating, file)

    def init_middle_region(self, region_widget):
        """
        构建中烟的筛选区域和表格区域
        """
        mid_layout = QVBoxLayout(region_widget)
        # 筛选区域
        filter_layout = QHBoxLayout()
        type_filter_label = QLabel('文件类型', self)
        self.type_filter_combo = QComboBox(self)
        self.type_filter_combo.addItems(['全部', '视频', '应用', '网页', '场景'])

        age_filter_label = QLabel('年龄限制', self)
        self.age_filter_combo = QComboBox(self)
        self.age_filter_combo.addItems(['全部', '全年龄', '指导级', '限制级'])

        filter_btn = QPushButton('筛选', self)
        filter_btn.clicked.connect(self.filter_wallpapers)

        filter_layout.addWidget(type_filter_label)
        filter_layout.addWidget(self.type_filter_combo)
        filter_layout.addWidget(age_filter_label)
        filter_layout.addWidget(self.age_filter_combo)
        filter_layout.addWidget(filter_btn)

        table_options = ['名称', '类型', '年龄限制', '文件', '操作']

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(len(table_options))
        self.table_widget.setHorizontalHeaderLabels(table_options)
        # 最后一列自适应
        header = self.table_widget.horizontalHeader()

        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(3, QHeaderView.Stretch)

        header.setSectionResizeMode(4, QHeaderView.Interactive)  # 允许用户手动微调
        self.table_widget.setColumnWidth(4, 100)

        mid_layout.addLayout(filter_layout)
        mid_layout.addWidget(self.table_widget)

    def filter_wallpapers(self):
        """
        点击“筛选”按钮后触发的逻辑接口
        :return:
        """
        if len(self.original_data) < 1:
            # 将数据复制一份到self.original_data
            self.original_data = copy.deepcopy(self.wallpaper_data)
        else:
            self.wallpaper_data = copy.deepcopy(self.original_data)
        selected_type = self.type_filter_combo.currentText()
        selected_age = self.age_filter_combo.currentText()

        print(f"开始筛选 -> 目标类型: {selected_type}, 目标年龄限制: {selected_age}")

        if selected_type == '全部' and selected_age == '全部':
            self.update_table_display()
            return

        type_dict = {
            'web': '网页',
            'application': '应用',
            'scene': '场景',
            'video': '视频'
        }
        age_dict = {
            'everyone': '全年龄',
            'questionable': '指导级',
            'mature': '限制级'
        }
        filter_result = []
        for item in self.wallpaper_data:
            item_type = item.get('type')
            if isinstance(item_type, str):
                item_type = item_type.lower()
            else:
                continue
            item_age = item.get('contentrating')
            if isinstance(item_age, str):
                item_age = item_age.lower()
            else:
                continue
            if selected_type != '全部' and selected_age != '全部':
                if type_dict.get(item_type) == selected_type and age_dict.get(item_age) == selected_age:
                    filter_result.append(item)
            elif selected_type == '全部' and selected_age != '全部':
                if age_dict.get(item_age) == selected_age:
                    filter_result.append(item)
            elif selected_type != '全部' and selected_age == '全部':
                if type_dict.get(item_type) == selected_type:
                    filter_result.append(item)
        self.wallpaper_data = filter_result
        self.update_table_display()

    def add_table_row(self, row_idx, title, data_type, contentrating, file):
        """向表格中动态插入一行的工具函数"""
        if self.table_widget.rowCount() <= row_idx:
            self.table_widget.setRowCount(row_idx + 1)

        name_item = QTableWidgetItem(title)
        name_item.setCheckState(Qt.Unchecked)
        self.table_widget.setItem(row_idx, 0, name_item)

        self.table_widget.setItem(row_idx, 1, QTableWidgetItem(data_type))
        self.table_widget.setItem(row_idx, 2, QTableWidgetItem(contentrating))
        self.table_widget.setItem(row_idx, 3, QTableWidgetItem(file))

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(5, 2, 5, 2)

        action_btn = QPushButton('导出', self)
        action_btn.clicked.connect(lambda: self.on_row_btn_clicked(title, file))

        btn_layout.addWidget(action_btn)
        self.table_widget.setCellWidget(row_idx, 4, btn_container)

    def on_row_btn_clicked(self, title, file):
        """点击行内按钮后的触发事件"""
        progress = QProgressDialog("正在导出...", None, 0, 100, self)
        progress.setWindowTitle("导出中")

        progress.setWindowModality(Qt.WindowModality.WindowModal)

        progress.setValue(0)
        progress.show()

        for i in range(1, 21):
            time.sleep(0.005)
            progress.setValue(i)
            QApplication.processEvents()

        progress.setValue(35)
        QApplication.processEvents()
        try:
            # 获取目标文件夹
            original_folder = get_original_folder()

            progress.setValue(75)
            QApplication.processEvents()

            # 复制文件到目标文件夹
            copy_file_path = copy_file_to_folder(file, original_folder)
            # 移除title中不能用于文件名的特殊字符
            safe_title = sanitize_filename(title)
            # 限制safe_title的最大长度
            safe_title = limit_filename_length(safe_title)
            # 将复制后的文件重命名为safe_title
            rename_file_keep_ext(copy_file_path, safe_title)

            progress.setValue(100)
            QApplication.processEvents()

            QMessageBox.information(self, '成功', f"壁纸【{title}】已成功导出！")
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败：{str(e)}')
        finally:
            progress.close()

    def get_selected_wallpapers(self) -> List[dict]:
        """
        便利表格，获取所有被用户勾选的数据
        :return: 包含被勾选数据的列表
        """
        selected_list = []
        row_count = self.table_widget.rowCount()
        for row_idx in range(row_count):
            item = self.table_widget.item(row_idx, 0)
            if item is None:
                continue
            if item.checkState() != Qt.Checked:
                continue
            wallpaper_info = self.wallpaper_data[row_idx]
            selected_list.append(wallpaper_info)
        return selected_list

    def batch_export(self):
        selected_wallpapers = self.get_selected_wallpapers()
        if not selected_wallpapers:
            QMessageBox.warning(self, '提示', '请先在表格中勾选需要导出的壁纸！')
            return

        total_files = len(selected_wallpapers)

        # 1. 创建总进度条
        progress = QProgressDialog("正在批量导出壁纸...", None, 0, total_files, self)
        progress.setWindowTitle("批量导出中")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()

        success_count = 0
        error_count = 0
        error_msgs = []
        original_folder = None

        try:
            # 获取目标文件夹
            original_folder = get_original_folder()

            # 2. 开始循环处理
            for idx, wallpaper in enumerate(selected_wallpapers):
                title = wallpaper.get('title', '未命名壁纸')
                file = wallpaper.get('file')

                progress.setLabelText(f"正在导出 ({idx + 1}/{total_files}):\n{title}")
                QApplication.processEvents()

                try:
                    if not file or not os.path.exists(file):
                        raise FileNotFoundError(f"找不到壁纸源文件: {file}")

                    copy_file_path = copy_file_to_folder(file, original_folder)
                    safe_title = sanitize_filename(title)
                    safe_title = limit_filename_length(safe_title)
                    rename_file_keep_ext(copy_file_path, safe_title)

                    success_count += 1

                except Exception as row_error:
                    error_count += 1
                    error_msgs.append(f"【{title}】导出失败: {str(row_error)}")

                progress.setValue(idx + 1)
                QApplication.processEvents()

            # 3. 循环全部结束后，进度条拉满并关闭
            progress.setValue(total_files)
            progress.close()

            # 4. 🌟 导出完成，准备弹窗和打开文件夹
            if error_count == 0:
                # 创建一个带有自定义按钮的问答弹窗
                reply = QMessageBox.question(
                    self,
                    '成功',
                    f"全部壁纸已成功导出！\n共成功导出 {success_count} 个文件。\n\n是否立刻打开目标文件夹？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes  # 默认聚焦在“是”上
                )

                # 🌟 如果用户点击了“是”，则打开文件夹
                if reply == QMessageBox.Yes and original_folder and os.path.exists(original_folder):
                    os.startfile(original_folder)

            else:
                detailed_error = "\n".join(error_msgs[:5])
                if len(error_msgs) > 5:
                    detailed_error += "\n...等多项错误"

                reply = QMessageBox.question(
                    self,
                    '批量导出完成',
                    f"批量导出结束（存在部分失败）：\n成功: {success_count} 个\n失败: {error_count} 个\n\n是否打开目标文件夹查看已成功的文件？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes and original_folder and os.path.exists(original_folder):
                    os.startfile(original_folder)

        except Exception as e:
            progress.close()
            QMessageBox.critical(self, '错误', f'批量导出初始化失败：{str(e)}')