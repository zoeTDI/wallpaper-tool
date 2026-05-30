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
        {"key": "preview", "label": "预览图", "mode": "interactive", "width": 140},
        {"key": "title", "label": "名称", "mode": "stretch", "width": None},
        {"key": "type", "label": "类型", "mode": "contents", "width": None},
        {"key": "contentrating", "label": "年龄限制", "mode": "contents", "width": None},
        {"key": "file", "label": "文件", "mode": "stretch", "width": None},
        {"key": "actions", "label": "操作", "mode": "interactive", "width": 100}  # 固定操作列
    ]
}