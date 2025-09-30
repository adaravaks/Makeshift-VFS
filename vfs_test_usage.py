from vfs import VFS

test_vfs = VFS('vfs_test_directory')

# test_vfs.add_node('dir1', is_dir=True)
# test_vfs.add_node('dir2', is_dir=True)
# test_vfs.add_node('text.txt', is_dir=False)
# test_vfs.change_current_dir('dir1')
# test_vfs.add_node('text2.txt', is_dir=False)
# test_vfs.add_node('dir3', is_dir=True)
# test_vfs.change_current_dir('dir3')
# test_vfs.add_node('image.png', is_dir=False)
# test_vfs.change_current_dir('..')
# test_vfs.change_current_dir('..')
test_vfs.display_vfs_tree()
