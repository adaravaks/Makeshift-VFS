import os
import tkinter as tk
from tkinter import scrolledtext


class GUI_VFS:
    def __init__(self):
        self.valid_commands = {'ls', 'cd', 'exit'}

        self.root = tk.Tk(className='Tk', screenName='VFS')
        self.root.title('VFS')

        self.output_field = tk.scrolledtext.ScrolledText(height=16, width=64)
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
                words.append(os.getenv(word[1:-1]))
            else:
                words.append(word)
        return ' '.join(words)

    def receive_input(self, event):
        command = event.widget.get()
        event.widget.delete(0, tk.END)
        responses = self.process_input(command)

        self.output_field.configure(state='normal')
        self.output_field.insert(tk.END, 'user@linux:~$ ' + command + '\n')
        for response in responses:
            if response == 'EXIT':
                self.root.destroy()
                return
            else:
                self.output_field.insert(tk.END, response + '\n')
        self.output_field.configure(state='disabled')

    def process_input(self, input_command):
        responses = []
        first_word = input_command.strip().split()[0]
        if first_word not in self.valid_commands:
            responses.append('Unrecognised command')
            return responses
        command = self._expand_input_command(input_command)

        if first_word == 'ls':
            responses.append(command)
        elif first_word == 'cd':
            if len(command.split()) != 2:
                responses.append('Invalid arguments')
            else:
                responses.append(command)
        elif first_word == 'exit':
            responses.append('EXIT')

        return responses

    def launch_gui_window(self):
        self.input_line.bind('<Return>', self.receive_input)
        self.root.mainloop()
