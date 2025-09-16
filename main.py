import os
from vfs import GUI_VFS
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VFS Emulator')
    parser.add_argument('--vfs-path', type=str, help='Path to VFS physical location', default=None)
    parser.add_argument('--script-path', type=str, help='Path to startup script', default=None)
    args = parser.parse_args()
    config = {
        'vfs_path': args.vfs_path,
        'script_path': args.script_path
    }
    print(config)
    vfs = GUI_VFS(config)
    vfs.launch_gui_window()
