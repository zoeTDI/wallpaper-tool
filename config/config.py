import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


def load_config_json():
    project_path = Path(__file__).resolve().parents[1]
    config_path = project_path / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"未在 {project_path} 里找到配置文件")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


default_config = load_config_json()


@dataclass
class PathConfig:
    scan_path: str


path_config = PathConfig(scan_path=default_config.get("path_config").get("scan_path"))


@dataclass
class BaseOption:
    label: str
    value: str


@dataclass
class BaseFilter:
    label: str
    default: str
    options: List[BaseOption]


@dataclass
class FilterConfig:
    type_filter: BaseFilter
    age_filter: BaseFilter


type_filter_options: List[BaseOption] = []
for option in default_config.get("filter_config").get("type").get("options"):
    type_filter_options.append(
        BaseOption(label=option.get("label"), value=option.get("value"))
    )

age_filter_options: List[BaseOption] = []
for option in default_config.get("filter_config").get("age").get("options"):
    age_filter_options.append(
        BaseOption(label=option.get("label"), value=option.get("value"))
    )

type_filter: BaseFilter = BaseFilter(
    label=default_config.get("filter_config").get("type").get("label"),
    default=default_config.get("filter_config").get("type").get("default"),
    options=type_filter_options,
)
age_filter: BaseFilter = BaseFilter(
    label=default_config.get("filter_config").get("age").get("label"),
    default=default_config.get("filter_config").get("age").get("default"),
    options=age_filter_options,
)

filter_config = FilterConfig(
    type_filter=type_filter,
    age_filter=age_filter,
)


@dataclass
class BaseColumn:
    key: str
    label: str
    mode: str
    formatter: str
    width: int | None = None


@dataclass
class TableConfig:
    columns: List[BaseColumn]


cols: List[BaseColumn] = []
for col in default_config.get("table_config").get("columns"):
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

table_config = TableConfig(columns=cols)


@dataclass
class AppConfig:
    path: PathConfig
    filter: FilterConfig
    column: TableConfig


app_config = AppConfig(path=path_config, filter=filter_config, column=table_config)
