import json
from pathlib import Path

from .schemas import *


def load_config_json():
    project_path = Path(__file__).resolve().parents[1]
    config_path = project_path / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"未在 {project_path} 里找到配置文件")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 路径
    path = PathConfig(scan_path=data["path_config"]["scan_path"])
    # 筛选器
    type_filter_options: List[BaseOption] = []
    for option in data.get("filter_config").get("type").get("options"):
        type_filter_options.append(
            BaseOption(label=option.get("label"), value=option.get("value"))
        )

    age_filter_options: List[BaseOption] = []
    for option in data.get("filter_config").get("age").get("options"):
        age_filter_options.append(
            BaseOption(label=option.get("label"), value=option.get("value"))
        )

    type_filter: BaseFilter = BaseFilter(
        label=data.get("filter_config").get("type").get("label"),
        default=data.get("filter_config").get("type").get("default"),
        options=type_filter_options,
    )
    age_filter: BaseFilter = BaseFilter(
        label=data.get("filter_config").get("age").get("label"),
        default=data.get("filter_config").get("age").get("default"),
        options=age_filter_options,
    )

    filter = FilterConfig(
        type_filter=type_filter,
        age_filter=age_filter,
    )
    # 表格
    cols: List[BaseColumn] = []
    for col in data.get("table_config").get("columns"):
        base_col = {
            "key": col.get("key"),
            "label": col.get("label"),
            "mode": col.get("mode"),
            "formatter": col.get("formatter"),
            "width": 0,
        }
        width = col.get("width")
        if type(width) is int:
            base_col["width"] = width
        else:
            base_col["width"] = None
        cols.append(BaseColumn(**base_col))

    table = TableConfig(columns=cols)

    return AppConfig(path=path, filter=filter, table=table)
