import os.path

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QLineEdit, \
    QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from db.generateDb import init
from db.db_utils import write_config, read_config

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        key = 'wallpaper_dir_path'
        wallpaper_dir_path = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\431960'
        init()
        result = read_config(key)
        if (result[0] == None):
            QMessageBox.warning(None, '提示', '未找到 Wallpaper Engine，请手动指定')
        else:
            self.path_input.setText(result[0])

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
        middle_layout = QVBoxLayout(middle_region)
        middle_layout.addWidget(QLabel("【中间区域】这里可以放内容主体、List、Grid等", alignment=Qt.AlignCenter))

        # 下方区域
        bottom_region = QFrame()
        bottom_region.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QVBoxLayout(bottom_region)
        bottom_layout.addWidget(QLabel("【下方区域】这里可以放‘开始运行’、‘取消’等按钮", alignment=Qt.AlignCenter))

        main_layout.addWidget(top_region, stretch=1)
        main_layout.addWidget(middle_region, stretch=3)
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
        # 扫描按钮
        scan_btn = QPushButton('扫描', self)
        scan_btn.clicked.connect(self.scan_wallpaper_dir)

        layout.addWidget(path_label)
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)
        layout.addWidget(scan_btn)

    def select_folder(self):
        selected_dir = QFileDialog.getExistingDirectory(self, '选择 Wallpaper Engine 文件夹', os.path.expanduser('~'))
        if selected_dir:
            normalized_path = os.path.normpath(selected_dir)
            self.path_input.setText(normalized_path)
            print(f"用户选择了路径: {normalized_path}")
            write_config('wallpaper_dir_path', normalized_path)

    def scan_wallpaper_dir(self):
        QMessageBox.information(None, '提示', '方法成功执行')