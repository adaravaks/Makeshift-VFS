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
            for child in node.children:
                self.change_current_dir(child.name)
                self.remove_node(child.name)
            del node
            return True
        return False

    def change_current_dir(self, name) -> bool:
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
                self.display_vfs_tree(node.children[child_name], level+1)
