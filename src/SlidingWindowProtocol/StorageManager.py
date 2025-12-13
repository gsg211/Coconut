import os


class StorageManager:
    def __init__(self, root_dir: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        self._root_dir = os.path.join(project_root, root_dir)

        if not os.path.exists(self._root_dir):
            os.makedirs(self._root_dir)

    def create_file(self, relative_path: str) -> None:
        full_path = os.path.join(self._root_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        try:
            with open(full_path, 'a'):
                os.utime(full_path, None)
        except OSError:
            pass

    def make_directory(self, relative_path: str) -> None:
        full_path = os.path.join(self._root_dir, relative_path)
        os.makedirs(full_path, exist_ok=True)

    def read(self, relative_path: str) -> str:
        full_path = os.path.join(self._root_dir, relative_path)
        if self.find(relative_path):
            with open(full_path, 'r') as f:
                return f.read()
        return ""

    def find(self, relative_path: str) -> bool:
        full_path = os.path.join(self._root_dir, relative_path)
        return os.path.exists(full_path)

    def write(self, relative_path: str, data: str) -> None:
        full_path = os.path.join(self._root_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(data)

    def list_files(self, relative_path: str) -> str:
        full_path = os.path.join(self._root_dir, relative_path)
        if not os.path.exists(full_path):
            return ""
        files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
        return "\n".join(files)

    def list_files_and_directories(self, relative_path: str) -> str:
        full_path = os.path.join(self._root_dir, relative_path)
        if not os.path.exists(full_path):
            return ""
        items = os.listdir(full_path)
        return "\n".join(f"- {'D' if os.path.isdir(os.path.join(full_path, item)) else 'F'} {item}"for item in items)

    def generate_tree_view(self, relative_path: str) -> str:
        start_path = os.path.join(self._root_dir, relative_path)
        tree_str = []
        if not os.path.exists(start_path):
            return ""
        for root, dirs, files in os.walk(start_path):
            level = root.replace(start_path, '').count(os.sep)
            indent = ' ' * 4 * level
            tree_str.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                tree_str.append(f"{subindent}{f}")
        return "\n".join(tree_str)


if __name__ == "__main__":
    storage_manager = StorageManager(root_dir="ClientStorage")

    storage_manager.make_directory("test_dir")
    storage_manager.create_file("test_dir/myfile.txt")
    storage_manager.write("test_dir/test.text", "write + create file")
    storage_manager.write("test_dir/myfile.txt", "write test")
    print("Test read:")
    print(storage_manager.read("test_dir/myfile.txt"))
    print("Test list_files:")
    print(storage_manager.list_files("test_dir"))
    print()
    print("Test list files and directories:")
    print(storage_manager.list_files_and_directories(""))
    print()

    print(f"Storage Root: {storage_manager._root_dir}")
    print("--- Tree View ---")
    print(storage_manager.generate_tree_view(""))