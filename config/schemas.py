from dataclasses import dataclass
from typing import List


@dataclass
class PathConfig:
    scan_path: str


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


@dataclass
class AppConfig:
    path: PathConfig
    filter: FilterConfig
    table: TableConfig
