import os
import tkinter as tk
from tkinter import scrolledtext
from vfs import VFS


class GUI:
    def __init__(self, config):
        self.valid_commands = {'ls', 'cd', 'tree', 'find', 'touch', 'rmdir', 'conf-dump', 'exit'}
        self.config = config
        self.vfs = None

        self.root = tk.Tk(className='Tk', screenName='VFS')
        self.root.title('VFS')

        self.output_field = tk.scrolledtext.ScrolledText(height=32, width=64)
        self.output_field.configure(state='disabled')
        self.output_field.grid(row=0, columnspan=2)

        self.input_label = tk.Label(self.root, text='user@linux:~$ ')
        self.input_label.grid(row=1, column=0)

        self.input_line = tk.Entry(self.root, width=64)
        self.input_line.grid(row=1, column=1)

    @staticmethod
    def _expand_input_command(command):
        words = []
        for word in command.strip().split():
            if len(word) > 2 and word[0] + word[-1] == '%%' and os.getenv(word[1:-1]):
                words.extend(os.getenv(word[1:-1]).split())
            else:
                words.append(word)
        return ' '.join(words)

    def _handle_input(self, event):
        command = event.widget.get()
        event.widget.delete(0, tk.END)

        self.output_field.configure(state='normal')
        self.output_field.insert(tk.END, f'user@linux:~{self.vfs.current_path}$ ' + command + '\n')
        responses = self._process_input(command)
        self.output_field.configure(state='disabled')
        self.input_label.configure(text=f'user@linux:~{self.vfs.current_path}$ ')
        self._display_responses(responses)

    def _handle_script_input(self, command):
        self.output_field.configure(state='normal')
        self.output_field.insert(tk.END, f'user@linux:~{self.vfs.current_path}$ ' + command + '\n')
        responses = self._process_input(command)
        self.output_field.configure(state='disabled')
        self.input_label.configure(text=f'user@linux:~{self.vfs.current_path}$ ')

        for response in responses:
            if 'Unrecognised' in response or 'Invalid' in response:
                return False
        self._display_responses(responses)
        return True

    def _display_responses(self, responses):
        self.output_field.configure(state='normal')
        for response in responses:
            if response == 'EXIT':
                self.root.destroy()
                return
            else:
                self.output_field.insert(tk.END, response + '\n')
        self.output_field.insert(tk.END, '\n')
        self.output_field.configure(state='disabled')

    def _process_input(self, input_command):
        responses = []
        command = self._expand_input_command(input_command.strip())
        first_word = command.split()[0]
        if first_word not in self.valid_commands:
            responses.append('Unrecognised command')
            return responses

        if first_word == 'ls':
            responses.append(self.vfs.do_ls(command.split()[1:]))
        elif first_word == 'cd':
            if len(command.split()) != 2:
                responses.append('Invalid arguments')
            else:
                if not self.vfs.change_current_dir(command.split()[1]):
                    responses.append(f'{command}: Invalid directory name or path')
        elif first_word == 'conf-dump':
            responses.append(f'VFS_PATH: {self.config['vfs_path']}')
            responses.append(f'SCRIPT_PATH: {self.config['script_path']}')
        elif first_word == 'tree':
            responses.append(self.vfs.do_tree(command.split()[1:]))
        elif first_word == 'find':
            responses.append(self.vfs.do_find(command.split()[1:]))
        elif first_word == 'touch':
            responses.append(self.vfs.do_touch(command.split()[1:]))
        elif first_word == 'rmdir':
            responses.append(self.vfs.do_rmdir(command.split()[1:]))
        elif first_word == 'exit':
            responses.append('EXIT')

        return responses

    def launch_gui_window(self):
        self.input_line.bind('<Return>', self._handle_input)
        # self.output_field.configure(state='normal')
        # self.output_field.insert(tk.END, f'VFS_PATH: {self.config['vfs_path']}' + '\n')
        # self.output_field.insert(tk.END, f'SCRIPT_PATH: {self.config['script_path']}' + '\n')
        # self.output_field.configure(state='disabled')

        try:
            self.vfs = VFS(self.config['vfs_path'])
        except (FileNotFoundError, NotADirectoryError):
            print('Invalid VFS path, unable to start the app.')
            return

        try:
            self._execute_script()
        except (FileNotFoundError, TypeError):
            self.output_field.configure(state='normal')
            self.output_field.insert(tk.END, 'Invalid startup script path.\n')
            self.output_field.configure(state='disabled')
        self.root.mainloop()

    def _execute_script(self):
        with open(self.config['script_path']) as f:
            for line in f.readlines():
                if not self._handle_script_input(line.strip('\n')):  # if command triggers an error
                    self.output_field.configure(state='normal')
                    self.output_field.insert(tk.END, 'Error during command execution, exiting script.\n')
                    self.output_field.configure(state='disabled')
                    break
