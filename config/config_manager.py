import json
import os
import sys
from typing import Callable, List

from dacite import from_dict

from config.schemas import (
    AppConfig,
    PathConfig,
    FilterConfig,
    BaseFilter,
    BaseOption,
    TableConfig,
    BaseColumn,
)


class ConfigManager:
    """
    用户配置维护类，负责配置的加载、保存及响应式通知。
    """

    def __init__(self):
        # 1. 初始化路径
        if getattr(sys, "frozen", False):
            # 程序打包后的路径
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # 项目开发环境路径
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(self.base_dir, "config.json")

        # 2. 预置硬编码配置 (FilterConfig, TableConfig)
        # 这里模拟加载项目中的基础配置
        self._filter_config = self._load_default_filter_config()
        self._table_config = self._load_default_table_config()

        # 3. 加载 PathConfig
        path_config = self._load_path_config()

        # 4. 组合 AppConfig
        self.app_config = AppConfig(
            path=path_config, filter=self._filter_config, table=self._table_config
        )

        # 5. 响应式观察者列表
        self._subscribers: List[Callable[[AppConfig], None]] = []

    def subscribe(self, callback: Callable[[AppConfig], None]):
        """注册配置更新回调"""
        self._subscribers.append(callback)

    def _notify(self):
        """通知所有订阅者"""
        for callback in self._subscribers:
            callback(self.app_config)

    def _load_path_config(self) -> PathConfig:
        """防御性载入：检查文件，不存在则创建默认值"""
        default_path = PathConfig(scan_path="", out_path="")

        if not os.path.exists(self.config_path):
            self._save_to_disk(default_path)
            return default_path

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return from_dict(data_class=PathConfig, data=data)
        except (json.JSONDecodeError, KeyError, Exception):
            # 校验失败时重置
            self._save_to_disk(default_path)
            return default_path

    def update_path(self, scan_path: str = None, out_path: str = None):
        """更新路径配置并触发通知"""
        if scan_path is not None:
            self.app_config.path.scan_path = scan_path
        if out_path is not None:
            self.app_config.path.out_path = out_path

        # 持久化
        self._save_to_disk(self.app_config.path)
        # 响应通知
        self._notify()

    def _save_to_disk(self, path_config: PathConfig):
        """将 PathConfig 保存到 JSON"""
        data = {"scan_path": path_config.scan_path, "out_path": path_config.out_path}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load_default_filter_config(self) -> FilterConfig:
        return FilterConfig(
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

    def _load_default_table_config(self) -> TableConfig:
        return TableConfig(
            columns=[
                BaseColumn(
                    key="preview",
                    label="预览图",
                    mode="interactive",
                    formatter="preview",
                    width=140,
                ),
                BaseColumn(
                    key="title",
                    label="名称",
                    mode="stretch",
                    formatter="title",
                    width=None,
                ),
                BaseColumn(
                    key="type",
                    label="类型",
                    mode="interactive",
                    formatter="type",
                    width=70,
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
