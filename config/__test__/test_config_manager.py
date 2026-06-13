import json
import unittest
from unittest.mock import patch, mock_open

from config.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # 初始化时模拟的合法 JSON 内容
        self.mock_config_content = json.dumps(
            {"scan_path": "/test/scan", "out_path": "/test/out"}
        )

    def _print_test_info(
        self, target: str, expected: str, actual: str = "正在验证中..."
    ):
        """辅助方法：统一控制台打印格式"""
        print(f"\n==================================================")
        print(f"【测试目的】: {target}")
        print(f"【预期结果】: {expected}")
        print(f"【实际结果】: {actual}")
        print(f"==================================================")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_initialization_success(self, mock_file, mock_exists):
        """测试：合法配置文件存在时的加载"""
        target = "当 config.json 文件存在且内容合法时，ConfigManager 初始化的加载情况。"
        expected = "成功读取 JSON 内容，并正确解析转化为内存中的 AppConfig 对象（scan_path='/test/scan', out_path='/test/out'）。"
        self._print_test_info(target, expected)

        # 执行被测逻辑
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.mock_config_content
        cm = ConfigManager()

        # 获取实际结果并更新打印
        actual = f"成功加载！内存值 -> scan_path='{cm.app_config.path.scan_path}', out_path='{cm.app_config.path.out_path}'"
        print(f"【实际状态】: {actual}")

        # 断言
        self.assertEqual(
            cm.app_config.path.scan_path,
            "/test/scan",
            msg=f"❌ scan_path 实际值为 {cm.app_config.path.scan_path}，未成功加载预设值",
        )
        self.assertEqual(
            cm.app_config.path.out_path,
            "/test/out",
            msg=f"❌ out_path 实际值为 {cm.app_config.path.out_path}，未成功加载预设值",
        )

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_file_not_found_init(self, mock_file, mock_exists):
        """测试：配置文件不存在时的防御性载入"""
        target = "当 🛠️ 配置文件 config.json 不存在时的防御性载入逻辑。"
        expected = "自动触发保存逻辑创建新文件，并使用默认的空路径（scan_path='', out_path=''）进行初始化。"
        self._print_test_info(target, expected)

        # 执行被测逻辑
        mock_exists.return_value = False
        cm = ConfigManager()

        actual = f"触发防御机制！文件打开状态: {mock_file.called}, 初始化内存值 -> scan_path='{cm.app_config.path.scan_path}'"
        print(f"【实际状态】: {actual}")

        # 断言
        self.assertTrue(
            mock_file.called, msg="❌ 文件不存在时，系统未调用创建并写入新文件的操作"
        )
        self.assertEqual(
            cm.app_config.path.scan_path,
            "",
            msg="❌ 重新创建的默认配置 scan_path 预期应为空字符串",
        )

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_json_corrupted_defensive_load(self, mock_file, mock_exists):
        """测试：配置文件损坏时的防御性重置"""
        target = "当 config.json 存在但 💥 JSON 格式损坏（不可解析）时的防御性载入。"
        expected = (
            "系统捕获 JSON 解析异常，重置并覆盖写入默认的空路径，保证程序不崩溃。"
        )
        self._print_test_info(target, expected)

        # 执行被测逻辑
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "{invalid_json: color_blue}"
        cm = ConfigManager()

        last_open_args = mock_file.call_args_list[-1]
        actual = f"成功捕获异常并重置内存配置！最后一次文件打开模式: '{last_open_args[0][1]}', 内存值 scan_path='{cm.app_config.path.scan_path}'"
        print(f"【实际状态】: {actual}")

        # 断言
        self.assertEqual(
            cm.app_config.path.scan_path,
            "",
            msg="❌ 配置文件损坏时，未能触发重置机制恢复为默认空路径",
        )
        self.assertEqual(
            last_open_args[0][1],
            "w",
            msg="❌ 配置文件损坏时，未以写入('w')模式重新格式化文件",
        )

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_reactive_update_and_persistence(self, mock_file, mock_exists):
        """测试：修改配置时的响应式通知与磁盘持久化"""
        target = "用户修改路径配置时的 🔄 响应式订阅通知与 💾 磁盘持久化同步。"
        expected = (
            "注册的订阅者回调能实时收到新配置，且修改后的数据成功回写到 config.json。"
        )
        self._print_test_info(target, expected)

        # 执行被测逻辑
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.mock_config_content
        cm = ConfigManager()

        callback_triggered = False
        received_config = None

        def mock_callback(updated_config):
            nonlocal callback_triggered, received_config
            callback_triggered = True
            received_config = updated_config

        cm.subscribe(mock_callback)

        new_scan_path = "/new/scan/path"
        new_out_path = "/new/out/path"
        cm.update_path(scan_path=new_scan_path, out_path=new_out_path)

        last_open_args = mock_file.call_args_list[-1]
        actual = f"订阅触发状态: {callback_triggered}, 接收到的新 scan_path='{received_config.path.scan_path if received_config else None}', 文件持久化模式: '{last_open_args[0][1]}'"
        print(f"【实际状态】: {actual}")

        # 断言
        self.assertTrue(
            callback_triggered, msg="❌ 调用 update_path 后，订阅者回调函数未被触发"
        )
        self.assertEqual(
            received_config.path.scan_path,
            new_scan_path,
            msg="❌ 订阅者接收到的新值未同步",
        )
        self.assertEqual(
            last_open_args[0][1],
            "w",
            msg="❌ 路径更新后，文件未以 'w' 模式打开执行持久化",
        )

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_partial_update_keeps_other_values(self, mock_file, mock_exists):
        """测试：单项增量修改时保持已有值"""
        target = "用户仅修改单个路径项（如仅修改 scan_path）时的 🎯 增量补全逻辑。"
        expected = "被修改的项（scan_path）成功变更，未被修改的项（out_path）维持原读取值不被覆盖。"
        self._print_test_info(target, expected)

        # 执行被测逻辑
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.mock_config_content
        cm = ConfigManager()

        cm.update_path(scan_path="/only/new/scan")

        actual = f"增量更新完毕！内存值 -> scan_path='{cm.app_config.path.scan_path}', out_path='{cm.app_config.path.out_path}'"
        print(f"【实际状态】: {actual}")

        # 断言
        self.assertEqual(
            cm.app_config.path.scan_path,
            "/only/new/scan",
            msg="❌ 增量更新时，目标 scan_path 未成功变更",
        )
        self.assertEqual(
            cm.app_config.path.out_path,
            "/test/out",
            msg="❌ 增量更新时，未传参的 out_path 被错误覆盖或抹除",
        )


if __name__ == "__main__":
    # 使用 -v 参数运行以确保能更清晰地查看每个用例的打印
    unittest.main()
