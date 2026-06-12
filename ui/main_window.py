import math
import os.path
from typing import List, Dict, Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFrame,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressDialog,
    QApplication,
    QMessageBox,
)

from config.schemas import AppConfig, BaseFilter
from utils.service import WallpaperService


def create_filter(combo, config: BaseFilter, minimun_width: int = 80) -> None:
    if (combo is None) or (config is None):
        print(f"[error] 缺少必要信息，无法创建筛选器组件")
        return
    for option in config.options:
        combo.addItem(option.label, option.value)
    combo.setCurrentText(config.default)
    combo.setMinimumWidth(minimun_width)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.table_widget = None
        self.service = WallpaperService()
        self.displayed_data: List[Dict] = []

        self.config: AppConfig = self.service.get_config()
        # top
        self.path_input = QLineEdit(self)
        self.scan_btn = QPushButton("扫描", self)
        # middle
        self.type_filter_combo = None
        self.age_filter_combo = None
        # bottom
        self.select_all_btn = None
        self.clear_all_btn = None
        self.batch_export_btn = None

        self.current_sort_key = None  # 当前排序的字段 key
        self.is_ascending = True  # True 为升序(正序)，False 为降序(倒序)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Wallpaper Tool")
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

        # 下方区域
        bottom_region = QFrame()
        bottom_region.setFrameShape(QFrame.StyledPanel)
        self.init_bottom_region(bottom_region)  # <-- 替换为新函数

        # 将三大区域添加到主布局中
        main_layout.addWidget(top_region, stretch=1)
        main_layout.addWidget(middle_region, stretch=6)
        main_layout.addWidget(bottom_region, stretch=1)

    def init_top_region(self, region_widget):
        layout = QHBoxLayout(region_widget)
        # label 文件
        path_label = QLabel("Wallpaper Engine 文件夹路径：", self)
        # 只读输入框
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("请选择或指定 Wallpaper Engine 文件夹...")
        self.path_input.textChanged.connect(self.check_input_content)
        # 浏览按钮
        browse_btn = QPushButton("浏览", self)
        browse_btn.clicked.connect(self.select_folder)

        # 扫描按钮
        self.scan_btn.clicked.connect(self.scan_wallpaper_dir)
        self.scan_btn.setEnabled(False)

        layout.addWidget(path_label)
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)
        layout.addWidget(self.scan_btn)

    def select_folder(self):
        selected_dir = QFileDialog.getExistingDirectory(
            self, "选择 Wallpaper Engine 文件夹", self.config.path.scan_path
        )
        if selected_dir:
            self.path_input.setText(os.path.normpath(selected_dir))

    def check_input_content(self):
        self.scan_btn.setEnabled(bool(self.path_input.text().strip()))

    def scan_wallpaper_dir(self):
        dir_path = self.path_input.text().strip()
        self.displayed_data = self.service.scan_directory(dir_path)
        self.filter_wallpapers()

    def filter_wallpapers(self):
        selected_type = self.type_filter_combo.currentData()
        selected_age = self.age_filter_combo.currentData()
        self.displayed_data = self.service.filter_data(selected_type, selected_age)
        self.update_table_display()

    def update_table_display(self):
        self.table_widget.setRowCount(0)
        if not self.displayed_data:
            return

        self.table_widget.setRowCount(len(self.displayed_data))
        for row_idx, data in enumerate(self.displayed_data):
            self.add_table_row(row_idx, data)

        title_idx = self._get_column_index_by_key("title")
        for row_idx in range(self.table_widget.rowCount()):
            title_item = self.table_widget.item(row_idx, title_idx)
            if title_item:
                is_checked = title_item.data(Qt.UserRole) is True
                self._set_row_background_color(row_idx, is_checked)

    def init_middle_region(self, region_widget):
        """
        构建中烟的筛选区域和表格区域
        """
        mid_layout = QVBoxLayout(region_widget)
        # 筛选区域
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        # todo 3
        self.type_filter_combo = QComboBox(self)
        type_cfg = self.config.filter.type_filter
        type_filter_label = QLabel(type_cfg.label, self)
        create_filter(self.type_filter_combo, type_cfg)

        self.age_filter_combo = QComboBox(self)
        age_cfg = self.config.filter.age_filter
        age_filter_label = QLabel(age_cfg.label, self)
        create_filter(self.age_filter_combo, age_cfg)

        filter_btn = QPushButton("筛选", self)
        filter_btn.setFixedSize(70, 26)
        filter_btn.clicked.connect(self.filter_wallpapers)

        filter_layout.addWidget(type_filter_label)
        filter_layout.addWidget(self.type_filter_combo)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(age_filter_label)
        filter_layout.addWidget(self.age_filter_combo)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()

        columns_config = self.config.table.columns
        table_labels = [col.label for col in columns_config]

        self.table_widget = QTableWidget(self)
        self.table_widget.verticalHeader().setDefaultSectionSize(55)
        self.table_widget.setColumnCount(len(table_labels))
        self.table_widget.setHorizontalHeaderLabels(table_labels)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.horizontalHeader().sectionClicked.connect(
            self.on_header_clicked
        )
        self.table_widget.cellClicked.connect(self.on_table_cell_clicked)
        # 最后一列自适应
        header = self.table_widget.horizontalHeader()

        header.setStretchLastSection(False)

        for idx, col in enumerate(columns_config):
            mode = col.mode
            if mode == "stretch":
                header.setSectionResizeMode(idx, QHeaderView.Stretch)
            elif mode == "contents":
                header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
            elif mode == "interactive":
                header.setSectionResizeMode(idx, QHeaderView.Interactive)
                if (type(col.width) is int) and (col.width > 0):
                    self.table_widget.setColumnWidth(idx, col.width)

        mid_layout.addLayout(filter_layout)
        mid_layout.addWidget(self.table_widget)

    def init_bottom_region(self, region_widget):
        """
        构建下方的批量操作区域
        """
        bottom_layout = QHBoxLayout(region_widget)
        bottom_layout.setContentsMargins(10, 5, 10, 5)

        # 新增：全选按钮
        self.select_all_btn = QPushButton("全选", self)
        self.select_all_btn.setFixedSize(80, 35)
        self.select_all_btn.clicked.connect(lambda: self.set_all_rows_selection(True))
        bottom_layout.addWidget(self.select_all_btn)

        # 新增：清空全选按钮
        self.clear_all_btn = QPushButton("清空全选", self)
        self.clear_all_btn.setFixedSize(80, 35)
        self.clear_all_btn.clicked.connect(lambda: self.set_all_rows_selection(False))
        bottom_layout.addWidget(self.clear_all_btn)

        bottom_layout.addStretch()

        self.batch_export_btn = QPushButton("批量导出", self)
        self.batch_export_btn.setFixedSize(120, 35)
        self.batch_export_btn.clicked.connect(self.batch_export)
        bottom_layout.addWidget(self.batch_export_btn)

    def set_all_rows_selection(self, is_selected: bool):
        """
        统一设置所有行的选中状态与背景色
        :param is_selected: True 为全选，False 为清空全选
        """
        if not self.table_widget or self.table_widget.rowCount() == 0:
            return

        title_col_idx = self._get_column_index_by_key("title")

        for row in range(self.table_widget.rowCount()):
            name_item = self.table_widget.item(row, title_col_idx)
            if name_item:
                # 更新绑定的选中数据状态
                name_item.setData(Qt.UserRole, is_selected)
                # 联动改变该行背景色
                self._set_row_background_color(row, is_selected)

    def add_table_row(self, row_idx, data_item: dict):
        """
        根据列配置，向表格中动态插入一行的工具函数
        """
        if self.table_widget.rowCount() <= row_idx:
            self.table_widget.setRowCount(row_idx + 1)

            # 动态遍历来自 config.py 的配置
        for index, col in enumerate(self.config.table.columns):
            # todo 2
            key = col.key
            formatter = col.formatter
            raw_val = data_item.get(key, "")

            # ====== 1. 预览图特殊控件渲染 ======
            if formatter == "preview":
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setStyleSheet("padding: 4px;")
                pixmap = QPixmap()
                if raw_val and os.path.exists(raw_val) and pixmap.load(raw_val):
                    column_width = self.table_widget.columnWidth(index)
                    side_length = column_width - 8
                    if side_length > 0:
                        scaled_pixmap = pixmap.scaled(
                            side_length,
                            side_length,
                            Qt.IgnoreAspectRatio,
                            Qt.SmoothTransformation,
                        )
                        img_label.setPixmap(scaled_pixmap)
                        self.table_widget.setRowHeight(row_idx, column_width)
                else:
                    img_label.setText("无预览")
                    img_label.setStyleSheet(
                        "color: #999999; font-size: 11px; padding: 4px;"
                    )
                self.table_widget.setCellWidget(row_idx, index, img_label)

            # ====== 2. 操作按钮特殊控件渲染 ======
            elif formatter == "actions":
                btn_container = QWidget()
                btn_layout = QHBoxLayout(btn_container)
                btn_layout.setContentsMargins(5, 2, 5, 2)
                btn_layout.setSpacing(6)  # 按钮之间的间距

                title = data_item.get("title", "Unknown")
                file_path = data_item.get("file", "")
                wallpaper_type = str(data_item.get("type", "")).lower()

                # 按钮 1：导出
                export_btn = QPushButton("导出", self)
                export_btn.clicked.connect(
                    lambda checked, t=title, f=file_path: self.on_row_btn_clicked(t, f)
                )
                btn_layout.addWidget(export_btn)

                # 按钮 2：打开文件位置 (默认选中文件)
                locate_btn = QPushButton("打开位置", self)
                locate_btn.clicked.connect(
                    lambda checked, f=file_path: self.on_locate_btn_clicked(f)
                )
                btn_layout.addWidget(locate_btn)

                # 按钮 3：打开文件 (仅限视频和网页)
                open_btn = QPushButton("打开文件", self)
                open_btn.clicked.connect(
                    lambda checked, f=file_path: self.on_open_file_btn_clicked(f)
                )

                # 核心控制：根据文件类型启用/禁用
                if wallpaper_type in ["video", "web"]:
                    open_btn.setEnabled(True)
                    open_btn.setToolTip("调用系统默认应用打开该壁纸")
                else:
                    open_btn.setEnabled(False)
                    open_btn.setToolTip("该类型壁纸不支持直接打开")

                btn_layout.addWidget(open_btn)

                self.table_widget.setCellWidget(row_idx, index, btn_container)

            # ====== 3. 统一处理所有标准文本（含各种常规元数据、时间、文件路径） ======
            else:
                display_text = self._get_display_text(formatter, raw_val)
                table_item = QTableWidgetItem(display_text)

                # 联动旧有逻辑：如果是名称列，初始化多选状态
                if formatter == "title":
                    table_item.setData(Qt.UserRole, False)

                self.table_widget.setItem(row_idx, index, table_item)

    def on_table_cell_clicked(self, row: int, column: int):
        """点击整行隐藏式切换选中状态，并联动变色"""
        actions_col_idx = self.table_widget.columnCount() - 1
        if column == actions_col_idx:
            return

        # 动态获取名称列的实际位置索引
        title_col_idx = self._get_column_index_by_key("title")
        name_item = self.table_widget.item(row, title_col_idx)

        if name_item:
            current_state = name_item.data(Qt.UserRole)
            if current_state is None:
                current_state = False

            new_state = not current_state
            name_item.setData(Qt.UserRole, new_state)
            self._set_row_background_color(row, new_state)

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
            QMessageBox.information(self, "成功", f"壁纸【{title}】已成功导出")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")
        finally:
            progress.close()

    def on_locate_btn_clicked(self, file_path: str):
        """
        槽函数：打开文件所在系统目录，并默认高亮选中该文件
        """
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "提示", "壁纸文件路径不存在，无法定位！")
            return

        import subprocess

        # Windows 标准安全路径转换，将斜杠转为反斜杠
        norm_path = os.path.normpath(file_path)
        try:
            # 使用 explorer.exe /select, 可以在打开文件夹的同时高亮对应的文件
            subprocess.run(["explorer", "/select,", norm_path], check=False)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件位置: {str(e)}")

    def on_open_file_btn_clicked(self, file_path: str):
        """
        槽函数：调用系统默认关联程序打开对应的视频或网页文件
        """
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "提示", "壁纸文件不存在，无法打开！")
            return

        try:
            # os.startfile 是 Windows 专属的强力 API，效果等同于双击该文件
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"调用外部程序打开文件失败: {str(e)}")

    def get_selected_wallpapers(self) -> List[dict]:
        """
        批量收集已被用户隐藏勾选的数据
        """
        selected_list = []
        title_col_idx = self._get_column_index_by_key("title")

        for row_idx in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row_idx, title_col_idx)
            if item and item.data(Qt.UserRole) is True:
                selected_list.append(self.displayed_data[row_idx])
        return selected_list

    def batch_export(self):
        selected_wallpapers = self.get_selected_wallpapers()
        if not selected_wallpapers:
            QMessageBox.warning(self, "提示", "请先在表格中勾选需要导出的壁纸！")
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
            title = wallpaper.get("title", "未命名壁纸")
            file = wallpaper.get("file")
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
                "成功",
                f"全部壁纸已成功导出！\n共成功导出 {success_count} 个文件。\n\n是否立刻打开目标文件夹？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes and target_folder:
                os.startfile(target_folder)
        else:
            detailed_error = "\n".join(error_msgs[:5]) + (
                "\n...等多项错误" if error_count > 5 else ""
            )
            reply = QMessageBox.question(
                self,
                "批量导出完成",
                f"批量导出结束（存在部分失败）：\n成功: {success_count} 个\n失败: {error_count} 个\n\n是否打开目标文件夹查看已成功的文件？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes and target_folder:
                os.startfile(target_folder)

    def on_header_clicked(self, logical_index: int):
        """
        排序预留功能函数：当用户点击某一列的表头时触发
        :param logical_index: 被点击列的索引
        """
        columns_config = self.config.table.columns
        if logical_index >= len(columns_config):
            return

        # todo 4
        clicked_column = columns_config[logical_index]
        column_key = clicked_column.key
        column_label = clicked_column.label
        formatter = clicked_column.formatter

        # 1. 过滤掉不支持排序的列
        if formatter in ["preview", "actions"]:
            print(f"列【{column_label}】不支持排序。")
            return

        # 2. 决定排序方向 (如果点击的是当前列，反转方向；如果是新列，默认降序)
        if self.current_sort_key == column_key:
            self.is_ascending = not self.is_ascending
        else:
            self.current_sort_key = column_key
            self.is_ascending = False

        # 3. 核心排序算法
        def sort_key_provider(item: dict):
            val = item.get(column_key, "")
            if column_key == "file_size_bytes":
                try:
                    return int(val) if val else 0
                except (ValueError, TypeError):
                    return 0
            return str(val).lower()

        # 对数据源进行排序
        self.displayed_data.sort(key=sort_key_provider, reverse=not self.is_ascending)

        # 4. ====== 核心优化：动态更新表头箭头提示 ======
        header = self.table_widget.horizontalHeader()
        for idx, col_cfg in enumerate(columns_config):
            original_label = col_cfg.label
            # 如果是当前排序的列，根据正倒序添加对应的箭头后缀
            if col_cfg.key == self.current_sort_key:
                arrow = " ▲" if self.is_ascending else " ▼"
                self.table_widget.setHorizontalHeaderItem(
                    idx, QTableWidgetItem(original_label + arrow)
                )
            else:
                # 其他列一律还原为最原始的无箭头标签
                self.table_widget.setHorizontalHeaderItem(
                    idx, QTableWidgetItem(original_label)
                )

        # 5. 重新刷新界面表格渲染
        self.update_table_display()

    def _set_row_background_color(self, row: int, is_checked: bool):
        """
        根据勾选状态，动态改变整行的背景颜色
        :param row: 行号
        :param is_checked: 是否被勾选
        :return: None
        """
        color_hex = "#E6F3FF" if is_checked else "#FFFFFF"
        # qcolor = (
        #     Qt.GlobalColor.white if not is_checked else QColor("#E6F3FF")
        # )  # 如果报错QColor未引入，可以用下面的样式表方案，更稳妥

        # 遍历该行的所有列
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.item(row, col)
            if item:
                item.setBackground(QColor(color_hex))

            widget = self.table_widget.cellWidget(row, col)
            if widget:
                widget.setStyleSheet(f"background-color: {color_hex};")

    def _format_size(self, size_bytes: int) -> str:
        """
        将字节大小转换为更加人性化的单位展示
        :param size_bytes: 字节大小
        :return: 转换后的展示
        """
        if not size_bytes or size_bytes <= 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB")

        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def _get_display_text(self, formatter_type: str, raw_val: Any) -> str:
        """
        核心解耦：统一管理各种标准文本的格式化映射
        """
        if not raw_val and raw_val != 0:
            return "未知" if formatter_type == "datetime" else ""

        if formatter_type == "size":
            return self._format_size(int(raw_val))

        elif formatter_type == "age":
            age_dict = {
                "everyone": "全年龄",
                "questionable": "指导级",
                "mature": "限制级",
            }
            return age_dict.get(str(raw_val).lower(), str(raw_val))

        elif formatter_type == "type":
            type_dict = {
                "web": "网页",
                "application": "应用",
                "scene": "场景",
                "video": "视频",
            }
            return type_dict.get(str(raw_val).lower(), str(raw_val))

        elif formatter_type == "datetime":
            return str(raw_val)

        return str(raw_val)

    def _get_column_index_by_key(self, target_key: str) -> int:
        """辅助方法：根据配置文件的 key 动态获取表格当前的列索引"""

        for index, col in enumerate(self.config.table.columns):
            # todo 1
            if col.key == target_key:
                return index
        return 1
