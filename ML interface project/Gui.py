import tkinter as tk
from tkinter import ttk
import subprocess
import platform

def create_menu(button, options):
    """Create a drop-down menu for a button."""
    menu = tk.Menu(button, tearoff=0)
    for option in options:
        menu.add_command(label=option)
    button['menu'] = menu

def launch_photostream():
    """Launch the photostream script in a new window."""
    if platform.system() == "Windows":
        subprocess.Popen(["python", "photostream.py"])
    else:
        subprocess.Popen(["python3", "photostream.py"])

root = tk.Tk()

# Set window size
root.geometry('800x600')

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, side=tk.TOP)

# Create the buttonsy
test_button1 = tk.Menubutton(button_frame, text='Test 1', relief='raised')
test_button2 = tk.Menubutton(button_frame, text='Test 2', relief='raised')
make_selections_button = tk.Button(button_frame, text='Make Selections')
take_pictures_button = tk.Button(button_frame, text='Take Pictures of Selections')
clear_selections_button = tk.Button(button_frame, text='Clear Selections')
display_photostream_button = tk.Button(button_frame, text='Display Photostream', command=launch_photostream)

# Create drop-down menus for the test buttons
create_menu(test_button1, ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5'])
create_menu(test_button2, ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5'])

# Layout the buttons
test_button1.pack(side=tk.LEFT)
test_button2.pack(side=tk.LEFT)
make_selections_button.pack(side=tk.LEFT)
take_pictures_button.pack(side=tk.LEFT)
clear_selections_button.pack(side=tk.LEFT)
display_photostream_button.pack(side=tk.LEFT)

root.mainloop()
