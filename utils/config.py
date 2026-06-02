# utils/config.py

WALLPAPER_TOOL_CONFIG = {
    # 1. 筛选项内容及其与业务字段的映射关系
    "filters": {
        "type": {
            "label": "文件类型",
            "default": "视频",
            "options": ["全部", "视频", "应用", "网页", "场景"]
        },
        "age": {
            "label": "年龄限制",
            "default": "限制级",
            "options": ["全部", "全年龄", "指导级", "限制级"]
        }
    },

    # 2. 表格的列配置
    # key: 数据字典中的键名, label: 界面显示的列名, mode: 缩放模式 (stretch=自适应, contents=根据内容, interactive=可手动微调)
    "table_columns": [
        {"key": "preview", "label": "预览图", "mode": "interactive", "width": 140, "formatter": "preview"},

        # 唯一的 Stretch 列：名称列。它将动态吞噬或释放界面上所有的剩余空间
        {"key": "title", "label": "名称", "mode": "stretch", "width": None, "formatter": "title"},

        # 固定或微调模式：给字数固定的列分配合理的像素宽度（摆脱 contents 缓存）
        {"key": "type", "label": "类型", "mode": "interactive", "width": 70, "formatter": "type"},
        {"key": "contentrating", "label": "年龄限制", "mode": "interactive", "width": 90, "formatter": "age"},

        # 时间列：固定 19 位字符，150 像素极其完美且整齐
        {"key": "create_time", "label": "创建时间", "mode": "interactive", "width": 200, "formatter": "datetime"},
        {"key": "modify_time", "label": "修改时间", "mode": "interactive", "width": 200, "formatter": "datetime"},
        {"key": "access_time", "label": "访问时间", "mode": "interactive", "width": 200, "formatter": "datetime"},

        # 文件大小：一般在 100 像素内
        {"key": "file_size_bytes", "label": "文件大小", "mode": "interactive", "width": 90, "formatter": "size"},

        # 文件路径列：原先也是 stretch，现改为固定大宽度（如 300 或 400），或者允许手动拉伸
        {"key": "file", "label": "文件路径", "mode": "stretch", "width": None, "formatter": "title"},

        {"key": "actions", "label": "操作", "mode": "interactive", "width": 260, "formatter": "actions"}
    ]
}