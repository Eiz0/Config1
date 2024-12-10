import os
import tarfile
import configparser
import xml.etree.ElementTree as ET
import datetime
import shutil


class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.log_tree = ET.Element("log")
        self.current_path = "/"
        self.filesystem_root = "/"
        self.init_virtual_filesystem()
        self.run_startup_script()

    def load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.username = config.get("settings", "username")
        self.hostname = config.get("settings", "hostname")
        self.fs_archive_path = config.get("settings", "fs_archive_path")
        self.log_path = config.get("settings", "log_path")
        self.start_script_path = config.get("settings", "start_script_path")

    def init_virtual_filesystem(self):
        if os.path.exists("virtual_fs"):
            shutil.rmtree("virtual_fs")
        os.mkdir("virtual_fs")
        with tarfile.open(self.fs_archive_path, "r") as tar:
            tar.extractall("virtual_fs")
        self.filesystem_root = os.path.abspath("virtual_fs")
        self.current_path = self.filesystem_root

    def log_action(self, action):
        entry = ET.SubElement(self.log_tree, "entry")
        timestamp = datetime.datetime.now().isoformat()
        ET.SubElement(entry, "timestamp").text = timestamp
        ET.SubElement(entry, "user").text = self.username
        ET.SubElement(entry, "action").text = action

    def save_log(self):
        tree = ET.ElementTree(self.log_tree)
        with open(self.log_path, "wb") as log_file:
            tree.write(log_file)

    def run_startup_script(self):
        if os.path.exists(self.start_script_path):
            with open(self.start_script_path, "r") as script:
                for command in script:
                    self.execute_command(command.strip())

    def execute_command(self, command):
        self.log_action(command)
        if command.startswith("cd "):
            self.change_directory(command.split(" ", 1)[1])
        elif command == "ls":
            self.list_directory()
        elif command == "exit":
            self.exit_shell()
        elif command.startswith("wc "):
            self.word_count(command.split(" ", 1)[1])
        elif command.startswith("mv "):
            self.move_file(command.split(" ", 2)[1:])
        else:
            print(f"Command not found: {command}")

    def change_directory(self, path):
        new_path = os.path.abspath(os.path.join(self.current_path, path))
        if new_path.startswith(self.filesystem_root) and os.path.exists(new_path) and os.path.isdir(new_path):
            self.current_path = new_path
        else:
            print(f"No such directory: {path}")

    def list_directory(self):
        for item in os.listdir(self.current_path):
            print(item)

    def word_count(self, file_path):
        abs_path = os.path.join(self.current_path, file_path)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            with open(abs_path, "r") as file:
                content = file.read()
                print(len(content.split()))
        else:
            print(f"No such file: {file_path}")

    def move_file(self, args):
        if len(args) != 2:
            print("Invalid arguments for mv")
            return
        src, dst = args
        abs_src = os.path.join(self.current_path, src)
        abs_dst = os.path.join(self.current_path, dst)
        if os.path.exists(abs_src):
            shutil.move(abs_src, abs_dst)
        else:
            print(f"No such file or directory: {src}")

    def exit_shell(self):
        print("Exiting shell...")
        self.save_log()
        exit()

    def run(self):
        while True:
            command = input(f"{self.username}@{self.hostname}:{self.current_path}$ ")
            self.execute_command(command)
