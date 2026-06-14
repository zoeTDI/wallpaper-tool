import os
from pathlib import Path

from config import app_config
from config.schemas import PathConfig
from config.updater import update_config_file
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

    def export(
        self, title: str, source_path: str, out_path: str = app_config.path.out_path
    ) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"找不到文件: {source_path}")
        # 存在自定义输出路径时，采用自定义输出路径
        if out_path is not None and Path(out_path).is_dir():
            if not Path(out_path).exists():
                try:
                    Path(out_path).mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    out_path = self._build_target_dir(
                        get_downloads_folder(), "wallpaper"
                    )
        else:
            out_path = self._build_target_dir(get_downloads_folder(), "wallpaper")

        safe_title = sanitize_filename(title)
        safe_title = limit_filename_length(safe_title)

        copy_file_path = copy_file_to_folder(source_path, out_path)
        rename_file_keep_ext(copy_file_path, safe_title)
        update_config_file(PathConfig(out_path=out_path))
        return out_path
