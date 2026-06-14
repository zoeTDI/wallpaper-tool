import json
import sys
from pathlib import Path

from .schemas import *


def get_project_path():
    """统一获取当前程序所在目录的路径"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parents[1]


def before_load():
    """检查配置文件是否存在，若不存在则创建默认配置"""

    project_path = get_project_path()
    config_path = project_path / "config.json"

    if not config_path.exists():
        default_data = {"path_config": {"scan_path": None, "out_path": None}}
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        print(f"已在 {config_path} 创建默认配置文件。")


def load_config_json():
    before_load()
    project_path = get_project_path()
    config_path = project_path / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 路径
    path: PathConfig = PathConfig(
        scan_path=data["path_config"]["scan_path"],
        out_path=data["path_config"]["out_path"],
    )
    # 筛选器
    filter: FilterConfig = FilterConfig(
        type_filter=BaseFilter(
            label="文件类型",
            default=4,
            options=[
                BaseOption(label="全部", value="all"),
                BaseOption(label="网页", value="web"),
                BaseOption(label="应用", value="application"),
                BaseOption(label="场景", value="scene"),
                BaseOption(label="视频", value="video"),
            ],
        ),
        age_filter=BaseFilter(
            label="年龄限制",
            default=3,
            options=[
                BaseOption(label="全部", value="all"),
                BaseOption(label="全年龄", value="everyone"),
                BaseOption(label="指导级", value="questionable"),
                BaseOption(label="限制级", value="mature"),
            ],
        ),
    )
    # 表格
    table: TableConfig = TableConfig(
        columns=[
            BaseColumn(
                key="preview",
                label="预览图",
                mode="interactive",
                formatter="preview",
                width=140,
            ),
            BaseColumn(
                key="title", label="名称", mode="stretch", formatter="title", width=None
            ),
            BaseColumn(
                key="type", label="类型", mode="interactive", formatter="type", width=70
            ),
            BaseColumn(
                key="contentrating",
                label="年龄限制",
                mode="interactive",
                formatter="age",
                width=90,
            ),
            BaseColumn(
                key="create_time",
                label="创建时间",
                mode="interactive",
                formatter="datetime",
                width=200,
            ),
            BaseColumn(
                key="modify_time",
                label="修改时间",
                mode="interactive",
                formatter="datetime",
                width=200,
            ),
            BaseColumn(
                key="access_time",
                label="访问时间",
                mode="interactive",
                formatter="datetime",
                width=200,
            ),
            BaseColumn(
                key="file_size_bytes",
                label="文件大小",
                mode="interactive",
                formatter="size",
                width=90,
            ),
            BaseColumn(
                key="file",
                label="文件路径",
                mode="stretch",
                formatter="title",
                width=None,
            ),
            BaseColumn(
                key="actions",
                label="操作",
                mode="interactive",
                formatter="actions",
                width=260,
            ),
        ]
    )

    return AppConfig(path=path, filter=filter, table=table)
