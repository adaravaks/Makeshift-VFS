import tkinter as tk
import tkinter.scrolledtext
import subprocess


def get_linux_env_var(var_name):
    try:
        var_value = subprocess.run(
            ['wsl.exe', 'sh', '-c', f"echo {var_name}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return ''.join(var_value.stdout.split())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_valid_command(first_word):
    valid_commands = {'ls', 'cd', 'exit'}
    return True if first_word in valid_commands else False


root = tk.Tk(className='Tk', screenName='VFS')
root.title('VFS')

output_field = tk.scrolledtext.ScrolledText(height=16, width=64)
output_field.configure(state='disabled')
output_field.grid(row=0, columnspan=2)

input_label = tk.Label(root, text='user@linux:~$ ')
input_label.grid(row=1, column=0)

input_line = tk.Entry(root, width=64)
input_line.grid(row=1, column=1)


def process_input(command: str):
    if command.split()[0] == 'exit':
        root.destroy()

    words = command.split()
    for i in range(len(words)):
        if words[i][0] == '$' and get_linux_env_var(words[i]):
            words[i] = get_linux_env_var(words[i])

    expanded_command = ' '.join(words)
    output_field.configure(state='normal')
    output_field.insert(tk.END, 'user@linux:~$ ' + command + '\n')
    if is_valid_command(words[0]) and (words[0] == 'cd' and len(words) == 2 or words[0] == 'ls'):
        output_field.insert(tk.END, expanded_command + '\n')
    elif is_valid_command(words[0]):
        output_field.insert(tk.END, 'Invalid arguments\n')
    else:
        output_field.insert(tk.END, 'Unrecognised command\n')
    output_field.configure(state='disabled')


def receive_input(event):
    command = event.widget.get()
    event.widget.delete(0, tkinter.END)
    process_input(command)


input_line.bind('<Return>', receive_input)
root.mainloop()
