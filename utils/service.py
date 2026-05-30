import copy
import os.path
from typing import List, Dict, Any

from utils.files import get_direct_subfolders_pathlib, find_file_case_insensitive, build_complete_path, \
    get_original_folder, copy_file_to_folder, sanitize_filename, limit_filename_length, rename_file_keep_ext
from utils.parse import parse_json_to_dict
from utils.config import WALLPAPER_TOOL_CONFIG

class WallpaperService:
    """
    专门处理壁纸数据的业务逻辑类
    """
    def __init__(self):
        self.raw_wallpapers: List[Dict[str, Any]] = []
        self.config = WALLPAPER_TOOL_CONFIG

    def get_config(self)->Dict[str, Any]:
        """
        为UI层提供配置数据
        :return: 配置数据
        """
        return self.config

    def scan_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """
        核心业务：扫描文件夹并解析 project.json
        :param dir_path: 根目录路径
        :return: json解析值的数组
        """
        self._raw_wallpapers = []
        if not dir_path or not os.path.exists(dir_path):
            return self._raw_wallpapers
        sub_folders = get_direct_subfolders_pathlib(dir_path)
        for folder in sub_folders:
            json_path = find_file_case_insensitive('project.json', folder)
            if not json_path:
                continue

            wallpaper_obj = parse_json_to_dict(json_path)
            if not wallpaper_obj:
                continue

            build_file_path = build_complete_path(json_path, wallpaper_obj.get('file'))
            wallpaper_obj['file'] = build_file_path
            self._raw_wallpapers.append(wallpaper_obj)
        return copy.deepcopy(self._raw_wallpapers)

    def filter_data(self, selected_type: str, selected_age: str) -> List[Dict[str, Any]]:
        """
        数据筛选
        :param selected_type: 选择的类型的值
        :param selected_age: 选择的年龄限制的值
        :return: 筛选结果
        """
        if not self._raw_wallpapers:
            return []
        if selected_type == '全部' and selected_age == '全部':
            return copy.deepcopy(self._raw_wallpapers)

        type_dict = {'web': '网页', 'application': '应用', 'scene': '场景', 'video': '视频'}
        age_dict = {'everyone': '全年龄', 'questionable': '指导级', 'mature': '限制级'}

        filter_result = []
        for item in self._raw_wallpapers:
            item_type = str(item.get('type', '')).lower()
            item_age = str(item.get('contentrating', '')).lower()

            match_type = (selected_type == '全部' or type_dict.get(item_type) == selected_type)
            match_age = (selected_age == '全部' or age_dict.get(item_age) == selected_age)

            if match_type and match_age:
                filter_result.append(item)

        return filter_result

    def export_single_wallpaper(self, title: str, file_path: str) -> str:
        """
        单个壁纸的复制与命名
        :param title: 新命名
        :param file_path: 目标文件夹路径
        :return: 导出目标的根目录
        """
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到壁纸文件： {file_path}")
        target_folder = get_original_folder()
        copy_file_path = copy_file_to_folder(file_path, target_folder)

        safe_title = sanitize_filename(title)
        safe_title = limit_filename_length(safe_title)
        rename_file_keep_ext(copy_file_path, safe_title)

        return target_folder