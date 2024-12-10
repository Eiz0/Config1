import unittest
import os
from emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator("config.ini")

    def test_ls(self):
        # Assuming there is a file or directory in the root
        self.emulator.execute_command("ls")
        self.assertTrue(True)  # Replace with stdout mock check

    def test_cd_valid(self):
        test_dir = "test_dir"
        os.mkdir(os.path.join(self.emulator.current_path, test_dir))
        self.emulator.execute_command(f"cd {test_dir}")
        self.assertTrue(self.emulator.current_path.endswith(test_dir))

    def test_cd_invalid(self):
        self.emulator.execute_command("cd non_existent_dir")
        self.assertNotIn("non_existent_dir", self.emulator.current_path)

    def test_wc(self):
        test_file = os.path.join(self.emulator.current_path, "test.txt")
        with open(test_file, "w") as f:
            f.write("hello world")
        self.emulator.execute_command("wc test.txt")
        self.assertTrue(True)  # Replace with stdout mock check

    def test_mv_valid(self):
        src = os.path.join(self.emulator.current_path, "src.txt")
        dst = os.path.join(self.emulator.current_path, "dst.txt")
        with open(src, "w") as f:
            f.write("content")
        self.emulator.execute_command(f"mv src.txt dst.txt")
        self.assertTrue(os.path.exists(dst))

    def test_mv_invalid(self):
        self.emulator.execute_command("mv non_existent_file.txt dst.txt")
        self.assertFalse(os.path.exists(os.path.join(self.emulator.current_path, "dst.txt")))

    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.emulator.execute_command("exit")
