import os
from pathlib import Path
from typing import List, Dict, Any

from utils.files import (
    get_direct_subfolders_pathlib,
    find_file_case_insensitive,
    get_file_metadata,
)
from utils.parse import parse_json_to_dict


class BaseService:
    def __init__(self):
        self._raw_wallpapers: List[Dict[str, Any]] = []

    def _insertFolderPath(self, item_data: Dict[str, Any], folder_path: str) -> None:
        item_data["_path"] = folder_path

    def _build_file_path(self, folder_path: str, filename: str) -> str:
        return str(Path(folder_path) / filename)

    def _insert_metadata(self, item_data: Dict[str, Any]) -> None:
        metadata = get_file_metadata(item_data["file"])
        item_data.update(metadata)

    def _process_wallpaper(self, data_item: Dict[str, Any], folder_path: str) -> None:
        if data_item:
            self._insertFolderPath(data_item, folder_path)
            data_item["preview"] = self._build_file_path(
                folder_path, data_item["preview"]
            )
            data_item["file"] = self._build_file_path(folder_path, data_item["file"])
            self._insert_metadata(data_item)

    def scan(self, dir_path: str) -> List[Dict[str, Any]]:
        self._raw_wallpapers = []
        if not dir_path or not os.path.exists(dir_path):
            return self._raw_wallpapers

        folders = get_direct_subfolders_pathlib(dir_path)
        for folder in folders:
            json_path = find_file_case_insensitive("project.json", folder)
            if type(json_path) is str and json_path != "":
                data = parse_json_to_dict(json_path)
                if data:
                    # 注入物理路径，方便后续定位
                    self._process_wallpaper(data, folder)
                    self._raw_wallpapers.append(data)
                    print(f"data: {data}")
        return self._raw_wallpapers

    @property
    def data(self):
        return self._raw_wallpapers
