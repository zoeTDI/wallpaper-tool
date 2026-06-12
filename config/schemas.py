from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PathConfig:
    """
    配置壁纸扫描的路径信息。
    """

    # 扫描壁纸的绝对路径
    scan_path: str


@dataclass
class BaseOption:
    """
    表示筛选器中的单个可选配置项。
    """

    # 界面显示的标签名称
    label: str
    # 实际对应的配置值
    value: str


@dataclass
class BaseFilter:
    """
    定义筛选器的配置结构，包含标签、默认项索引及可选列表。
    """

    # 筛选器在界面上的显示名称
    label: str
    # 默认选中的选项在 options 列表中的索引值（从0开始）
    default: int
    # 该筛选器支持的所有选项列表
    options: List[BaseOption]


@dataclass
class FilterConfig:
    """
    汇总所有筛选器配置。
    """

    # 壁纸类型筛选器配置
    type_filter: BaseFilter
    # 内容分级筛选器配置
    age_filter: BaseFilter


@dataclass
class BaseColumn:
    """
    定义数据表格的列属性。
    """

    # 列的唯一标识符
    key: str
    # 表头显示的文字
    label: str
    # 显示模式（如文本、图片等）
    mode: str
    # 数据格式化函数名称
    formatter: str
    # 列的宽度（可选，默认为None）
    width: Optional[int] = None


@dataclass
class TableConfig:
    """
    定义数据表格的列配置集合。
    """

    # 表格所有列的配置列表
    columns: List[BaseColumn]


@dataclass
class AppConfig:
    """
    应用程序的全局配置结构。
    """

    # 路径相关的配置
    path: PathConfig
    # 筛选器相关的配置
    filter: FilterConfig
    # 表格展示相关的配置
    table: TableConfig
