from gui import GUI
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VFS Emulator')
    parser.add_argument('--vfs-path', type=str, help='Path to VFS physical location', default='vfs_test_directory')
    parser.add_argument('--script-path', type=str, help='Path to startup script', default='startup_script.txt')
    args = parser.parse_args()
    config = {
        'vfs_path': args.vfs_path,
        'script_path': args.script_path
    }
    vfs = GUI(config)
    vfs.launch_gui_window()
