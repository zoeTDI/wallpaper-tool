import os
from pathlib import Path

from utils.files import (
    sanitize_filename,
    limit_filename_length,
    get_downloads_folder,
    copy_file_to_folder,
    rename_file_keep_ext,
)


class ExportService:
    def _build_target_dir(self, target_dir: str, *dirs: str) -> str:
        """
        拼接路径并创建文件夹。
        :param target_dir: 基础绝对路径
        :param dirs: 不定长的子文件夹路径序列
        :return: 拼接后的完整绝对路径字符串
        """
        full_path = Path(target_dir).joinpath(*dirs)
        full_path.mkdir(parents=True, exist_ok=True)
        return str(full_path)

    def export(self, title: str, source_path: str) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"找不到文件: {source_path}")
        download_dir = get_downloads_folder()
        target_dir = self._build_target_dir(download_dir, "wallpaper")

        safe_title = sanitize_filename(title)
        safe_title = limit_filename_length(safe_title)

        copy_file_path = copy_file_to_folder(source_path, target_dir)
        rename_file_keep_ext(copy_file_path, safe_title)
        return target_dir
