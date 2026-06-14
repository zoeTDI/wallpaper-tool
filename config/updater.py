import json

from utils.isDef import is_valid
from config.loader import get_project_path

from config.schemas import PathConfig


def update_config_file(new_path_config: PathConfig):
    """
    更新 config.json：直接使用传入的 PathConfig 对象覆盖 json 文件中的对应属性。
    """
    config_path = get_project_path() / "config.json"

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"path_config": {"scan_path": None, "out_path": None}}
    if "path_config" not in data:
        data["path_config"] = {"scan_path": None, "out_path": None}

    if is_valid(new_path_config.scan_path):
        data["path_config"]["scan_path"] = new_path_config.scan_path

    if is_valid(new_path_config.out_path):
        data["path_config"]["out_path"] = new_path_config.out_path

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
