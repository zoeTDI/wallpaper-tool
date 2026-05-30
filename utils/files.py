from pathlib import Path
import platform
import shutil
import re

def get_direct_subfolders_pathlib(folder_path):
    """
    扫描指定文件夹下的所有直接子文件夹，并返回路径数组（字符串格式）
    """
    path = Path(folder_path)

    # 确保传入的路径存在且是一个文件夹
    if not path.is_dir():
        raise ValueError(f"提供的路径不存在或不是一个文件夹: {folder_path}")

    # iterdir() 迭代直接子项，is_dir() 过滤出文件夹，as_posix() 统一转换为正斜杠字符串
    return [str(sub.resolve()) for sub in path.iterdir() if sub.is_dir()]


def find_file_case_insensitive(filename: str, folder_path: str) -> str:
    """
    在指定文件夹中查找文件（不区分大小写）。
    如果找不到，则在控制台打印目标文件夹的名称。

    :param filename: 要查找的文件名（含扩展名）
    :param folder_path: 目标文件夹路径
    :return: 找到的文件绝对路径字符串，若未找到则返回空字符串 ""
    """
    target_path = Path(folder_path)

    if not target_path.exists() or not target_path.is_dir():
        raise ValueError(f"提供的路径不存在或不是一个文件夹: {folder_path}")

    # 将待查找的目标文件名转换为小写
    target_filename_lower = filename.lower()

    # 递归遍历文件夹下的所有文件（如果只需查找第一层，可将 rglob 改为 glob）
    for file in target_path.rglob("*"):
        if file.is_file():
            # 统一转为小写进行不区分大小写的比对
            if file.name.lower() == target_filename_lower:
                return str(file.resolve())

    print(f"未找到文件 '{filename}'，当前扫描的文件夹名称为: {target_path.name}")

    return ""


def build_complete_path(existing_file_path: str, new_file_name: str) -> str:
    """
    根据一个已知文件的路径和同级目录下的新文件名，构建新文件的完整路径。

    :param existing_file_path: 已知文件的完整路径
    :param new_file_name: 同级目录下的新文件名
    :return: 新文件的完整路径字符串
    """
    # 1. 将输入路径转换为 Path 对象
    path_obj = Path(existing_file_path)

    # 2. 获取该文件所在的父目录，并拼接上新的文件名
    # path_obj.parent 获取父目录，/ 运算符在 pathlib 中用于拼接路径
    new_path = path_obj.parent / new_file_name

    # 3. 将 Path 对象转换回字符串返回
    return str(new_path)


def copy_file_to_folder(source_file_path: str, target_folder_path: str) -> str:
    """
    将文件复制到指定的文件夹下。

    :param source_file_path: 源文件的完整路径
    :param target_folder_path: 目标文件夹的路径
    :return: 复制后的新文件完整路径
    """
    # 使用 pathlib 处理路径，兼容 Windows 和 Linux/Mac 系统
    source = Path(source_file_path)
    target_dir = Path(target_folder_path)

    # 1. 检查源文件是否存在，不存在则抛出错误
    if not source.exists():
        raise FileNotFoundError(f"找不到源文件: {source_file_path}")

    # 2. 如果目标文件夹不存在，则自动创建它（包括所有必要的父级目录）
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"目标文件夹不存在，已自动创建: {target_dir}")

    # 3. 构建复制后的完整目标路径
    # target_dir / source.name 相当于：目标文件夹 + / + 原文件名
    destination = target_dir / source.name

    # 4. 执行复制操作
    # shutil.copy 会复制文件内容和权限
    shutil.copy(str(source), str(destination))

    return str(destination)


def rename_file_keep_ext(file_path: str, new_name_without_ext: str) -> str:
    """
    修改指定文件的文件名，同时保留其原有的扩展名。
    如果新文件名已存在，则自动在文件名后添加 (1), (2), (3)... 序号直至成功。

    :param file_path: 原文件的完整路径
    :param new_name_without_ext: 新的文件名（不包含扩展名，例如 'my_video'）
    :return: 修改后的新文件完整路径
    """
    old_path = Path(file_path)

    # 1. 安全检查：确保原文件确实存在
    if not old_path.exists():
        raise FileNotFoundError(f"找不到要重命名的文件: {file_path}")

    # 2. 获取原文件的扩展名（例如 '.mp4'）
    file_extension = old_path.suffix

    # 3. 基础尝试：构建初始目标路径
    full_new_name = f"{new_name_without_ext}{file_extension}"
    new_path = old_path.parent / full_new_name

    # 4. 冲突处理循环：仿照 Windows 命名规则，如果目标文件已存在，则添加序号
    counter = 1
    while new_path.exists():
        # 如果新路径正好就是旧路径本身（比如大小写不敏感系统上的同名重命名），则不视为冲突，直接跳出
        if new_path.resolve() == old_path.resolve():
            break

        # 仿照 Windows 格式： 文件名 (1).mp4
        numbered_name = f"{new_name_without_ext} ({counter}){file_extension}"
        new_path = old_path.parent / numbered_name
        counter += 1

    # 5. 执行重命名操作
    try:
        old_path.rename(new_path)
    except FileExistsError:
        # 防御性容错：如果在高并发或极端情况下循环未挡住，捕获后继续递增重试
        while True:
            numbered_name = f"{new_name_without_ext} ({counter}){file_extension}"
            new_path = old_path.parent / numbered_name
            if not new_path.exists():
                old_path.rename(new_path)
                break
            counter += 1

    return str(new_path)

def sanitize_filename(filename: str) -> str:
    """
    将字符串中不能用于文件名的字符替换为下划线。

    :param filename: 原始可能包含非法字符的字符串
    :return: 替换后的安全文件名字符串
    """
    # 定义 Windows 和类 Unix 系统中最常见的非法字符集:
    # \ / : * ? " < > |
    # 另外，我们通常也会把换行符 \n、回车符 \r 和制表符 \t 一并处理
    illegal_chars_regex = r'[\\/:*?"<>|\r\n\t]'

    # 使用 re.sub 将匹配到的非法字符替换为下划线
    sanitized = re.sub(illegal_chars_regex, '_', filename)

    # 附加优化（可选）：有些系统不允许文件名以空格或点结尾，这里顺便帮处理掉
    # sanitized = sanitized.strip('. ')

    return sanitized


def limit_filename_length(filename: str, max_length: int = 255) -> str:
    """
    限制文件名字符串的长度，防止超过系统限制，同时确保扩展名不被破坏。

    :param filename: 已经剔除特殊字符的文件名（可以带路径，也可以只是文件名）
    :param max_length: 允许的最大长度（默认 255）
    :return: 截断后的安全文件名
    """
    # 如果本身就没超限，直接返回
    if len(filename) <= max_length:
        return filename

    # 使用 pathlib 分离文件名主体和扩展名
    path_obj = Path(filename)

    # suffix 获取的是最后一个点及之后的后缀（例如 '.mp4'）
    # 如果是复合后缀（如 '.tar.gz'），建议改用: ext = "".join(path_obj.suffixes)
    ext = path_obj.suffix
    stem = path_obj.stem  # 获取不带后缀的文件名主体

    # 计算留给文件名主体（stem）的最大可用长度
    allowed_stem_length = max_length - len(ext)

    # 如果扩展名本身已经长得离谱，导致没有空间留给主体，则强行从末尾截断整个字符串
    if allowed_stem_length <= 0:
        return filename[:max_length]

    # 截断主体，并拼接回原本的扩展名
    truncated_stem = stem[:allowed_stem_length]

    # 如果输入带有父级路径，保持路径结构不变；如果只是纯文件名，则直接返回文件名
    if path_obj.parent and path_obj.parent != Path('.'):
        return str(path_obj.parent / f"{truncated_stem}{ext}")
    else:
        return f"{truncated_stem}{ext}"


def get_downloads_folder() -> str:
    """
    获取当前操作系统用户“下载”（Downloads）文件夹的完整路径。
    支持 Windows、macOS 和 Linux，并能识别 Windows 用户自定义的下载路径。

    :return: 下载文件夹的路径字符串
    """
    current_os = platform.system()
    home = Path.home()  # 获取当前用户的主目录 (例如 C:\Users\Username 或 /home/username)

    # 1. Windows 系统处理逻辑
    if current_os == "Windows":
        try:
            # 引入 Windows 特有的注册表控制模块
            import winreg

            # Windows 核心文件夹路径在注册表中的固定键值
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            # {374DE290-123F-4565-9164-39C4925E467B} 是 Windows 系统中“下载”文件夹的 GUID
            guid_downloads = "{374DE290-123F-4565-9164-39C4925E467B}"

            # 打开注册表并读取
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                raw_path, _ = winreg.QueryValueEx(key, guid_downloads)

            # 注册表里可能包含环境变量（如 %USERPROFILE%\Downloads），需要解析它
            expanded_path = os.path.expandvars(raw_path)
            return str(Path(expanded_path))

        except Exception:
            # 如果读取注册表因权限等极特殊原因失败，则降级使用默认路径
            return str(home / "Downloads")

    # 2. macOS 系统处理逻辑
    elif current_os == "Darwin":
        return str(home / "Downloads")

    # 3. Linux / 类 Unix 系统处理逻辑
    else:
        # Linux 遵循 XDG 目录标准，首选读取配置文件
        xdg_config = home / ".config" / "user-dirs.dirs"
        if xdg_config.exists():
            try:
                with open(xdg_config, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("XDG_DOWNLOAD_DIR"):
                            # 解析出类似 "XDG_DOWNLOAD_DIR="$HOME/Downloads"" 中的路径
                            path_part = line.split("=")[1].strip().strip('"')
                            path_part = path_part.replace("$HOME", str(home))
                            return str(Path(path_part))
            except Exception:
                pass
        # 降级备用方案
        return str(home / "Downloads")

def get_original_folder() -> str:
    downloads_path_str = get_downloads_folder()
    wallpaper_dir = Path(downloads_path_str) / 'wallpaper'
    if not wallpaper_dir.exists():
        wallpaper_dir.mkdir(parents=True, exist_ok=True)
    return str(wallpaper_dir)