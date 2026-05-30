from pathlib import Path
import json

def parse_json_to_dict(file_path: str) -> dict:
    """
    接受一个 JSON 文件路径，将其解析为字典对象并返回。

    :param file_path: JSON 文件的路径（可能为空字符串）
    :return: 解析后的字典。如果路径为空、文件不存在或解析失败，返回空字典 {}
    """
    # 1. 检查路径是否为空字符串或 None
    if not file_path or file_path.strip() == "":
        print("错误: 提供的文件路径为空。")
        return {}

    path = Path(file_path)

    # 2. 检查文件是否存在
    if not path.exists():
        print(f"错误: 文件不存在 -> {file_path}")
        return {}

    # 3. 检查是否为文件而不是文件夹
    if not path.is_file():
        print(f"错误: 指定的路径不是一个文件 -> {file_path}")
        return {}

    # 4. 读取并解析 JSON
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 确保解析出来的是字典（防止 JSON 文件根节点是列表或单值）
            if isinstance(data, dict):
                return data
            else:
                print(f"警告: JSON 文件的根节点不是字典对象（当前是 {type(data).__name__}）。")
                return {}

    except json.JSONDecodeError as e:
        print(f"错误: JSON 文件格式不正确，解析失败。原因: {e}")
        return {}
    except Exception as e:
        print(f"错误: 读取文件时发生未知异常: {e}")
        return {}