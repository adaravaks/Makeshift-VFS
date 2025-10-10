import os


class VFSNode:
    def __init__(self, name, is_dir=False, content=None):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.parent = None
        self.children = {} if is_dir else None


class VFS:
    def __init__(self, path_to_directory: str):
        self.real_path = path_to_directory if path_to_directory.endswith('/') else path_to_directory + '/'
        directory_name = [part for part in path_to_directory.split('/') if part != ''][-1]
        self.root_dir = VFSNode(directory_name, is_dir=True)
        self.current_dir = self.root_dir
        self.current_path = '/'
        self._initial_scout()

    def _initial_scout(self, path=''):
        with os.scandir(self.real_path + path) as entries:
            for entry in entries:
                if entry.is_dir():
                    self.add_node(entry.name, is_dir=True)
                    self.change_current_dir(entry.name)
                    self._initial_scout(self.current_path)
                    self.change_current_dir('..')
                else:
                    self.add_node(entry.name, is_dir=False)

    def add_node(self, name, is_dir) -> bool:
        if not self.current_dir.children.get(name):
            new_node = VFSNode(name, is_dir=is_dir)
            self.current_dir.children[name] = new_node
            new_node.parent = self.current_dir
            return True
        return False

    def remove_node(self, name) -> bool:
        node = self.current_dir.children.get(name)
        if node:
            while node.children:
                children_names = list(node.children.keys())
                for child in children_names:
                    self.remove_node(child)
                    del node.children[child]
            else:
                del self.current_dir.children[name]
                del node
            return True
        return False

    def change_current_dir(self, name) -> bool:
        name = name.strip('/')
        if name.count('/') > 0:
            dirs = name.split('/')
            results = []
            for dir_name in dirs:
                results.append(self.change_current_dir(dir_name))
            if not all(results):
                for i in range(results.count(True)):
                    self.change_current_dir('..')
                return False
            else:
                return True

        node = self.current_dir.children.get(name)
        if (node and node.is_dir) or (name == '..' and self.current_dir.parent):
            if name != '..':
                self.current_path += f'{name}/'
                self.current_dir = node
            else:
                path_parts = [part for part in self.current_path.split('/') if part != '']
                self.current_path = '/'.join(path_parts[:-1]) + '/'
                self.current_dir = self.current_dir.parent
            return True
        return False

    def display_vfs_tree(self, node=None, level=0):
        node = self.root_dir if not node else node
        print('    ' * level + node.name)
        if node.is_dir:
            for child_name in node.children:
                self.display_vfs_tree(node.children[child_name], level + 1)

    def do_ls(self, args=None) -> str:
        if args is None:
            args = []

        show_all = '-a' in args
        long_format = '-l' in args
        if '-la' in args or '-al' in args:
            show_all = True
            long_format = True

        path_args = [arg for arg in args if arg not in ['-a', '-l', '-la', '-al']]
        target_path = path_args[0] if path_args else "."

        original_dir = self.current_dir
        original_path = self.current_path

        try:
            if target_path != "." and not self.change_current_dir(target_path):
                return f"ls: cannot access '{target_path}': No such file or directory\n"

            if not self.current_dir.is_dir:
                return f"ls: cannot access '{target_path}': Not a directory\n"

            if not self.current_dir.children:
                return ""

            items = []
            for name, node in self.current_dir.children.items():
                if not show_all and name.startswith('.'):
                    continue
                items.append((name, node))

            items.sort(key=lambda x: (not x[1].is_dir, x[0].lower()))

            if long_format:
                return self._format_long_listing(items)
            else:
                return self._format_simple_listing(items)

        finally:
            self.current_dir = original_dir
            self.current_path = original_path

    @staticmethod
    def _format_simple_listing(items) -> str:
        if not items:
            return ""

        lines = []
        for name, node in items:
            if node.is_dir:
                lines.append(f"{name}/")
            else:
                lines.append(name)

        return "\n".join(lines)

    @staticmethod
    def _format_long_listing(items) -> str:
        if not items:
            return ""

        lines = []
        total_blocks = len(items)
        lines.append(f"total {total_blocks}")

        for name, node in items:
            if node.is_dir:
                perms = "drwxr-xr-x"
                size = "4096"
            else:
                perms = "-rw-r--r--"
                size = str(len(node.content)) if node.content else "0"

            # fake but consistent metadata
            nlink = "1"
            user = "user"
            group = "user"
            date = "Jan 1 00:00"

            line = f"{perms} {nlink} {user} {group} {size:>8} {date} {name}"
            if node.is_dir:
                line += "/"
            lines.append(line)

        return "\n".join(lines)

    def do_tree(self, args=None) -> str:
        if args is None:
            args = []

        show_all = '-a' in args
        path_args = [arg for arg in args if arg not in ['-a', '-l', '-la', '-al']]
        target_path = path_args[0] if path_args else "."

        original_dir = self.current_dir
        original_path = self.current_path

        try:
            if target_path != "." and not self.change_current_dir(target_path):
                return f"tree: {target_path}: No such file or directory\n"

            if not self.current_dir.is_dir:
                return f"tree: {target_path}: Not a directory\n"

            result = [f"{target_path}\n"]
            self._build_tree(self.current_dir, "", result, show_all)
            return "".join(result)

        finally:
            self.current_dir = original_dir
            self.current_path = original_path

    def _build_tree(self, node, indent, result, show_all):
        if not node.is_dir or not node.children:
            return

        children = list(node.children.items())
        children.sort(key=lambda x: (not x[1].is_dir, x[0].lower()))

        for i, (name, child_node) in enumerate(children):
            if name[0] == '.' and not show_all:
                continue

            is_last = (i == len(children) - 1)

            branch = "└── " if is_last else "├── "

            result.append(f"{indent}{branch}{name}")
            if child_node.is_dir:
                result.append("/")
            result.append("\n")

            next_indent = indent + ("    " if is_last else "│   ")

            if child_node.is_dir:
                self._build_tree(child_node, next_indent, result, show_all)

    def do_find(self, args=None) -> str:
        if args is None:
            args = []

        if (len(args) < 3 or args[1] != '-name') and args:
            return "find: usage: find [path] -name 'pattern'\n"

        if args:
            start_path = args[0]
            pattern = args[2]
        else:
            start_path = self.current_path
            pattern = '*'

        original_dir = self.current_dir
        original_path = self.current_path

        try:
            if start_path not in './' and not self.change_current_dir(start_path):
                return f"find: '{start_path}': No such file or directory\n"

            if not self.current_dir.is_dir:
                return f"find: '{start_path}': Not a directory\n"

            results = []
            start_absolute_path = self.current_path
            self._find_recursive(self.current_dir, start_absolute_path, pattern, results)

            if not results:
                return ""

            return "\n".join(results)

        finally:
            self.current_dir = original_dir
            self.current_path = original_path

    def _find_recursive(self, node, current_path, pattern, results):
        if not node.is_dir or not node.children:
            return

        for name, child_node in node.children.items():
            if current_path == "/":
                child_full_path = f"/{name}"
            else:
                child_full_path = f"{current_path}{name}"

            if self._pattern_match(name, pattern):
                results.append(child_full_path)

            if child_node.is_dir:
                recursive_path = child_full_path + "/"
                self._find_recursive(child_node, recursive_path, pattern, results)

    @staticmethod
    def _pattern_match(filename, pattern):
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    def do_touch(self, args=None) -> str:
        if args is None:
            args = []

        if not args:
            return "touch: missing file operand\n"

        errors = []
        for filepath in args:
            success, error_msg = self._create_file(filepath)
            if not success:
                errors.append(f"touch: {error_msg}")

        return "\n".join(errors) + "\n" if errors else ""

    def _create_file(self, filepath) -> tuple[bool, str]:
        if '/' in filepath:
            parts = [p for p in filepath.strip('/').split('/') if p]
            if not parts:
                return False, "cannot touch '/': Is a directory"

            filename = parts[-1]
            dir_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'

            original_dir = self.current_dir
            original_path = self.current_path

            if not self.change_current_dir(dir_path):
                return False, f"cannot touch '{filepath}': No such directory"

            if filename in self.current_dir.children:
                existing_node = self.current_dir.children[filename]
                if existing_node.is_dir:
                    self.current_dir = original_dir
                    self.current_path = original_path
                    return False, f"cannot touch '{filepath}': Is a directory"
            else:
                self.add_node(filename, is_dir=False)

            self.current_dir = original_dir
            self.current_path = original_path

        else:
            if filepath in self.current_dir.children:
                existing_node = self.current_dir.children[filepath]
                if existing_node.is_dir:
                    return False, f"cannot touch '{filepath}': Is a directory"
            else:
                self.add_node(filepath, is_dir=False)

        return True, ""

    def do_rmdir(self, args=None) -> str:
        if args is None:
            args = []

        if not args:
            return "rmdir: missing operand\n"

        errors = []
        for dirpath in args:
            success, error_msg = self._remove_directory(dirpath)
            if not success:
                errors.append(f"rmdir: {error_msg}")

        return "\n".join(errors) + "\n" if errors else ""

    def _remove_directory(self, dirpath) -> tuple[bool, str]:
        if '/' in dirpath:
            parts = [p for p in dirpath.strip('/').split('/') if p]
            if not parts:
                return False, "failed to resolve path"

            dir_name = parts[-1]
            parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'

            original_dir = self.current_dir
            original_path = self.current_path

            if not self.change_current_dir(parent_path):
                return False, f"failed to remove '{dirpath}': No such file or directory"

            if dir_name not in self.current_dir.children:
                self.current_dir = original_dir
                self.current_path = original_path
                return False, f"failed to remove '{dirpath}': No such file or directory"

            target_node = self.current_dir.children[dir_name]

            if not target_node.is_dir:
                self.current_dir = original_dir
                self.current_path = original_path
                return False, f"failed to remove '{dirpath}': Not a directory"

            if target_node.children:
                self.current_dir = original_dir
                self.current_path = original_path
                return False, f"failed to remove '{dirpath}': Directory not empty"

            self.remove_node(dir_name)

            self.current_dir = original_dir
            self.current_path = original_path

        else:
            if dirpath not in self.current_dir.children:
                return False, f"failed to remove '{dirpath}': No such file or directory"

            target_node = self.current_dir.children[dirpath]

            if not target_node.is_dir:
                return False, f"failed to remove '{dirpath}': Not a directory"

            if target_node.children:
                return False, f"failed to remove '{dirpath}': Directory not empty"

            self.remove_node(dirpath)

        return True, ""
