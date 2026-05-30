import copy
import os.path
import time
from typing import List, Dict

from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QLineEdit, \
    QPushButton, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QProgressDialog, QApplication, \
    QMessageBox
from PyQt5.QtCore import Qt
from utils.files import get_direct_subfolders_pathlib, find_file_case_insensitive, build_complete_path, \
    get_downloads_folder, get_original_folder, copy_file_to_folder, rename_file_keep_ext, sanitize_filename, \
    limit_filename_length
from utils.parse import parse_json_to_dict
from utils.service import WallpaperService

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.service = WallpaperService()
        self.displayed_data: List[Dict] = []

        self.config = self.service.get_config()

        self.initUI()

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
        self.path_input.textChanged.connect(self.check_input_content)
        # 浏览按钮
        browse_btn = QPushButton('浏览', self)
        browse_btn.clicked.connect(self.select_folder)

        # 扫描按钮
        self.scan_btn = QPushButton('扫描', self)
        self.scan_btn.clicked.connect(self.scan_wallpaper_dir)
        self.scan_btn.setEnabled(False)

        layout.addWidget(path_label)
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)
        layout.addWidget(self.scan_btn)

    def select_folder(self):
        default_path = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\431960'
        selected_dir = QFileDialog.getExistingDirectory(self, '选择 Wallpaper Engine 文件夹', default_path)
        if selected_dir:
            self.path_input.setText(os.path.normpath(selected_dir))

    def check_input_content(self):
        self.scan_btn.setEnabled(bool(self.path_input.text().strip()))

    def scan_wallpaper_dir(self):
        dir_path = self.path_input.text().strip()
        self.displayed_data = self.service.scan_directory(dir_path)
        self.filter_wallpapers()

    def filter_wallpapers(self):
        selected_type = self.type_filter_combo.currentText()
        selected_age = self.age_filter_combo.currentText()
        self.displayed_data = self.service.filter_data(selected_type, selected_age)
        self.update_table_display()

    def update_table_display(self):
        self.table_widget.setRowCount(0)
        if not self.displayed_data:
            return
        self.table_widget.setRowCount(len(self.displayed_data))
        for row_idx, data in enumerate(self.displayed_data):
            self.add_table_row(
                row_idx,
                data.get('preview', ''),
                data.get('title', 'Unknown'),
                data.get('type', 'Unknown'),
                data.get('contentrating', 'everyone'),
                data.get('file', '')
            )

    def init_middle_region(self, region_widget):
        """
        构建中烟的筛选区域和表格区域
        """
        mid_layout = QVBoxLayout(region_widget)
        # 筛选区域
        filter_layout = QHBoxLayout()

        type_cfg = self.config['filters']['type']
        type_filter_label = QLabel(type_cfg['label'], self)
        self.type_filter_combo = QComboBox(self)
        self.type_filter_combo.addItems(type_cfg["options"])
        self.type_filter_combo.setCurrentText(type_cfg["default"])

        age_cfg = self.config["filters"]["age"]
        age_filter_label = QLabel(age_cfg["label"], self)
        self.age_filter_combo = QComboBox(self)
        self.age_filter_combo.addItems(age_cfg["options"])
        self.age_filter_combo.setCurrentText(age_cfg["default"])

        filter_btn = QPushButton('筛选', self)
        filter_btn.clicked.connect(self.filter_wallpapers)

        filter_layout.addWidget(type_filter_label)
        filter_layout.addWidget(self.type_filter_combo)
        filter_layout.addWidget(age_filter_label)
        filter_layout.addWidget(self.age_filter_combo)
        filter_layout.addWidget(filter_btn)

        columns_config = self.config["table_columns"]
        table_labels = [col["label"] for col in columns_config]

        self.table_widget = QTableWidget(self)
        self.table_widget.verticalHeader().setDefaultSectionSize(55)
        self.table_widget.setColumnCount(len(table_labels))
        self.table_widget.setHorizontalHeaderLabels(table_labels)
        self.table_widget.cellClicked.connect(self.on_table_cell_clicked)
        self.table_widget.itemChanged.connect(self.on_table_item_changed)
        # 最后一列自适应
        header = self.table_widget.horizontalHeader()

        header.setStretchLastSection(False)

        for idx, col in enumerate(columns_config):
            mode = col["mode"]
            if mode == "stretch":
                header.setSectionResizeMode(idx, QHeaderView.Stretch)
            elif mode == "contents":
                header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
            elif mode == "interactive":
                header.setSectionResizeMode(idx, QHeaderView.Interactive)
                if col["width"]:
                    self.table_widget.setColumnWidth(idx, col["width"])

        mid_layout.addLayout(filter_layout)
        mid_layout.addWidget(self.table_widget)

    def add_table_row(self, row_idx, preview_path, title, data_type, contentrating, file):
        """
        向表格中动态插入一行的工具函数
        """
        if self.table_widget.rowCount() <= row_idx:
            self.table_widget.setRowCount(row_idx + 1)

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignHCenter)
        img_label.setStyleSheet("padding: 4px")

        pixmap = QPixmap()
        if preview_path and os.path.exists(preview_path) and pixmap.load(preview_path):
            # 动态获取你在 config 中为第 0 列设置的宽度
            column_width = self.table_widget.columnWidth(0)

            # 预留内边距后的实际图片宽度（例如左右各预留 4px 内边距，总共减去 8）
            padding_total = 8
            side_length = column_width - padding_total

            # 确保边长大于 0，防止极端情况下报错
            if side_length > 0:
                # 核心：为了实现 1/1 的长宽比，并且填满宽度，
                # 我们将目标宽高都设为 side_length (正方形)
                # 使用 Qt.IgnoreAspectRatio 强制拉伸填满 1:1 正方形
                # 如果你希望图片不失真地裁剪或居中，建议使用 SmoothTransformation
                scaled_pixmap = pixmap.scaled(
                    side_length,
                    side_length,
                    Qt.IgnoreAspectRatio,  # 强制 1:1 比例
                    Qt.SmoothTransformation
                )
                img_label.setPixmap(scaled_pixmap)

                # 同步调整行高：为了完美呈现 1:1 的正方形，这一行的高度应该与列宽一致（加上上下内边距）
                self.table_widget.setRowHeight(row_idx, column_width)
        else:
            # 错误处理：渲染占位文字
            img_label.setText("无预览")
            img_label.setStyleSheet("color: #999999; font-size: 11px; padding: 4px;")

        self.table_widget.setCellWidget(row_idx, 0, img_label)

        name_item = QTableWidgetItem(title)
        name_item.setCheckState(Qt.Unchecked)
        self.table_widget.setItem(row_idx, 1, name_item)
        self.table_widget.setItem(row_idx, 2, QTableWidgetItem(data_type))
        self.table_widget.setItem(row_idx, 3, QTableWidgetItem(contentrating))
        self.table_widget.setItem(row_idx, 4, QTableWidgetItem(file))

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(5, 2, 5, 2)

        action_btn = QPushButton('导出', self)
        action_btn.clicked.connect(lambda: self.on_row_btn_clicked(title, file))

        btn_layout.addWidget(action_btn)
        self.table_widget.setCellWidget(row_idx, 5, btn_container)

    def on_table_item_changed(self, item):
        """
        当单元格内容或状态改变时触发。如果是名称列（第1列）的勾选状态变了，同步改变背景色。
        """
        # 确保是名称列（第 1 列）
        if item.column() == 1:
            row = item.row()
            is_checked = (item.checkState() == Qt.Checked)
            self._set_row_background_color(row, is_checked)

    def on_table_cell_clicked(self, row: int, column: int):
        """
        当用户点击表格的任意单元格时触发，实现点击整行即可切换勾选状态。
        """
        actions_col_idx = self.table_widget.columnCount() - 1
        if column == actions_col_idx:
            return
        name_item = self.table_widget.item(row, 1)
        if name_item:
            if name_item.checkState() == Qt.Checked:
                name_item.setCheckState(Qt.Unchecked)
                is_checked = False
            else:
                name_item.setCheckState(Qt.Checked)
                is_checked = True
            self._set_row_background_color(row, is_checked)

    def on_row_btn_clicked(self, title, file):
        """
        点击行内按钮后的触发事件
        """
        progress = QProgressDialog("正在导出...", None, 0, 100, self)
        progress.setWindowTitle("导出中")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        try:
            progress.setValue(30)
            QApplication.processEvents()
            target_folder = self.service.export_single_wallpaper(title, file)
            progress.setValue(100)
            QMessageBox.information(self, '成功', f'壁纸【{title}】已成功导出')
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
        for row_idx in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row_idx, 1)
            if item and item.checkState() == Qt.Checked:
                selected_list.append(self.displayed_data[row_idx])
        return selected_list

    def batch_export(self):
        selected_wallpapers = self.get_selected_wallpapers()
        if not selected_wallpapers:
            QMessageBox.warning(self, '提示', '请先在表格中勾选需要导出的壁纸！')
            return

        total_files = len(selected_wallpapers)

        progress = QProgressDialog("正在批量导出壁纸...", None, 0, total_files, self)
        progress.setWindowTitle("批量导出中")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        success_count = 0
        error_msgs = []
        target_folder = None

        for idx, wallpaper in enumerate(selected_wallpapers):
            title = wallpaper.get('title', '未命名壁纸')
            file = wallpaper.get('file')
            progress.setLabelText(f"正在导出 ({idx + 1}/{total_files}):\n{title}")
            QApplication.processEvents()
            try:
                target_folder = self.service.export_single_wallpaper(title, file)
                success_count += 1
            except Exception as row_error:
                error_msgs.append(f"【{title}】导出失败: {str(row_error)}")

        progress.close()
        error_count = len(error_msgs)

        if error_count == 0:
            reply = QMessageBox.question(
                self,
                '成功',
                f"全部壁纸已成功导出！\n共成功导出 {success_count} 个文件。\n\n是否立刻打开目标文件夹？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes and target_folder:
                os.startfile(target_folder)
        else:
            detailed_error = "\n".join(error_msgs[:5]) + ("\n...等多项错误" if error_count > 5 else "")
            reply = QMessageBox.question(
                self, '批量导出完成', f"批量导出结束（存在部分失败）：\n成功: {success_count} 个\n失败: {error_count} 个\n\n是否打开目标文件夹查看已成功的文件？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes and target_folder:
                os.startfile(target_folder)

    def _set_row_background_color(self, row: int, is_checked: bool):
        """
        根据勾选状态，动态改变整行的背景颜色
        :param row: 行号
        :param is_checked: 是否被勾选
        :return: None
        """
        color_hex = "#E6F3FF" if is_checked else "#FFFFFF"
        qcolor = Qt.GlobalColor.white if not is_checked else QColor("#E6F3FF")  # 如果报错QColor未引入，可以用下面的样式表方案，更稳妥

        # 遍历该行的所有列
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.item(row, col)
            if item:
                item.setBackground(QColor(color_hex))

            widget = self.table_widget.cellWidget(row, col)
            if widget:
                widget.setStyleSheet(f"background-color: {color_hex};")