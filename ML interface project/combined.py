import pyautogui
import tkinter as tk
from tkinter import ttk

from tkinter import filedialog
import tkinter.messagebox
import tkinter.scrolledtext as st
from PIL import Image, ImageTk, ImageDraw
from PIL import ImageFont
from pynput import mouse, keyboard
import os
import json
import threading
import time
import cv2
import numpy as np

DISPLAY_WINDOW = [True]
root = tk.Tk()
label = tk.Label(root)
label.pack()

# Initialize HSV values:
hsv_values = {
    'lower': [0, 0, 0],
    'upper': [179, 255, 255]
}

img_count = [0]
areasofinterest = []
dragging = [False]
drag_coords = [None, None]
buttons = []
mouse_controller = mouse.Controller()
current_mouse_position = [None]

def apply_filter(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_bound = np.array(hsv_values['lower'], dtype=np.uint8)
    upper_bound = np.array(hsv_values['upper'], dtype=np.uint8)
    mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
    return cv2.bitwise_and(img, img, mask=mask)

# Load areas of interest from file
try:
    with open('areasofinterest.txt', 'r') as file:
        areasofinterest = json.load(file)
except FileNotFoundError:
    open('areasofinterest.txt', 'w').close()
except json.JSONDecodeError:
    pass  # If file is empty, do nothing

def save_areas_of_interest():
    with open('areasofinterest.txt', 'w') as file:
        json.dump(areasofinterest, file)

def update_mouse_position():
    while True:
        current_mouse_position[0] = mouse_controller.position
        time.sleep(0.02)  # Update 50 times per second

mouse_position_thread = threading.Thread(target=update_mouse_position, daemon=True)
mouse_position_thread.start()


def open_command_window():
    command_window = tk.Toplevel(root)
    command_window.title('Command window')

    console = st.ScrolledText(command_window, state='disabled')
    console.grid(column=0, row=0, sticky='nsew')

    tutorial_text = tk.Text(command_window, width=40)
    tutorial_text.grid(column=1, row=0, sticky='nsew')

    entry_frame = tk.Frame(command_window)
    entry_frame.grid(column=0, row=1, sticky='ew')

    entry = tk.Entry(entry_frame)
    entry.pack(side='left', fill='x', expand=True)
    entry.bind('<Return>', lambda event: submit_entry())

    def submit_entry():
        console.configure(state='normal')
        console.insert('end', entry.get() + '\n')
        console.configure(state='disabled')
        with open('Commandhistory.txt', 'a') as file:
            file.write(entry.get() + '\n')
        entry.delete(0, 'end')

    submit_button = tk.Button(entry_frame, text='Submit', command=submit_entry)
    submit_button.pack(side='left')

    def submit_from_file():
        filename = filedialog.askopenfilename()
        if filename:
            with open(filename, 'r') as file:
                for line in file:
                    entry.delete(0, 'end')
                    entry.insert('end', line.rstrip('\n'))
                    submit_entry()

    submit_file_button = tk.Button(entry_frame, text='Submit from File', command=submit_from_file)
    submit_file_button.pack(side='left')

    try:
        with open('Tutorialtext.txt', 'r') as file:
            tutorial_text.insert('end', file.read())
    except FileNotFoundError:
        print("Tutorialtext.txt not found")

def exit_application():
    # Here you can handle anything you want to do before closing the application
    root.quit()
    root.destroy()  # This is required for the application to close when the X button is clicked


root.protocol("WM_DELETE_WINDOW", exit_application)


def toggle_display_window():
    DISPLAY_WINDOW[0] = not DISPLAY_WINDOW[0]
def load_areas_of_interest():
    global areasofinterest
    filename = filedialog.askopenfilename()
    if filename:
        try:
            with open(filename, 'r') as file:
                areasofinterest = json.load(file)
        except json.JSONDecodeError:
            tk.messagebox.showerror("Invalid file", "The selected file does not contain valid JSON data.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")


def on_press(key):
    if key == keyboard.Key.f8:  # Use F8 key for marking corners of rectangles
        if root.focus_get() is not None:  # Handle keypress event only when our window is focused
            if btn_vars[0].get():  # If 'Select regions' mode is active
                if drag_coords[0] is None:  # If initial corner is not yet marked
                    drag_coords[0] = mouse_controller.position
                    print(f'Set drag_coords[0] 142= {drag_coords[0]}')
                else:  # If initial corner is already marked
                    drag_coords[1] = mouse_controller.position
                    print(f'Set drag_coords[0] 144= {drag_coords[1]}')
                    # Call the code that handles the completion of rectangle drawing
                    select_regions_complete()
                    drag_coords[0] = None  # Reset the initial corner

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

def select_regions():
    global dragging
    if not dragging[0]:  # If not currently dragging
        dragging[0] = True  # Begin selection
        # Disable other buttons
        for b in buttons:
            if b != buttons[0]:  # Skip 'Select regions' button
                b.configure(state='disabled')
               # Enable other buttons
    else:  
        dragging[0]=False
        for b in buttons:
            if b != buttons[0]:  # Skip 'Select regions' button
                b.configure(state='normal')

def select_regions_complete():
    global areasofinterest, dragging
    # If currently dragging
   # dragging[0] = False  # Complete selection
    drag_coords[1] = mouse_controller.position
    left = min(drag_coords[0][0], drag_coords[1][0])
    top = min(drag_coords[0][1], drag_coords[1][1])
    width = abs(drag_coords[0][0] - drag_coords[1][0])
    height = abs(drag_coords[0][1] - drag_coords[1][1])



 

    # Ensure the region is within screen bounds
    left = max(0, left)
    top = max(0, top)
    right = min(pyautogui.size()[0], left + width)
    bottom = min(pyautogui.size()[1], top + height)
    width = right - left
    height = bottom - top

    if width > 0 and height > 0:  # Ignore zero-sized region
        if len(areasofinterest) < 100:  # Limit to 100 rectangles
            areasofinterest.append([left, top, width, height, str(len(areasofinterest))])  # Add index as label

    # Reset the drag coordinates after completing a rectangle
    drag_coords[0], drag_coords[1] = None, None


def take_pictures_of_regions():
    global areasofinterest, img_count
    for index, (left, top, width, height, _) in enumerate(areasofinterest):
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        os.makedirs(str(index), exist_ok=True)  # Create directory if it doesn't exist
        screenshot.save(os.path.join(str(index), f'image_{img_count[0]}_{index}.png'))
    img_count[0] += 1

def clear_selections():
    global areasofinterest
    areasofinterest = []

def update_image():
    if DISPLAY_WINDOW[0]:
        screenshot = pyautogui.screenshot()
        screenshot_draw = screenshot.convert("RGBA")
        draw = ImageDraw.Draw(screenshot_draw)
        font = ImageFont.truetype("arial", 20)  # Define the font and size

        for (left, top, width, height, area_label) in areasofinterest:
            draw.rectangle([(left, top), (left + width, top + height)], outline="yellow")
            bbox = draw.textbbox((0, 0), area_label, font=font)  # Get the bounding box of the text
            text_width = bbox[2] - bbox[0]  # Calculate the width of the text
            text_height = bbox[3] - bbox[1]  # Calculate the height of the text
            text_x = left + (width - text_width) / 2  # Center the text
            text_y = top + (height - text_height) / 2  # Center the text
            draw.text((text_x, text_y), area_label, fill="yellow", font=font)  # Pass the font parameter to draw.text

        # If a rectangle is being drawn, draw it
        if drag_coords[0] is not None and current_mouse_position[0] is not None:
            left = min(drag_coords[0][0], current_mouse_position[0][0])
            top = min(drag_coords[0][1], current_mouse_position[0][1])
            width = abs(drag_coords[0][0] - current_mouse_position[0][0])
            height = abs(drag_coords[0][1] - current_mouse_position[0][1])
            draw.rectangle([(left, top), (left + width, top + height)], outline="yellow")

        screenshot = ImageTk.PhotoImage(screenshot_draw)
        label.configure(image=screenshot)
        label.image = screenshot

    root.after(300, update_image)


# Create toolbar frame
toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)
toolbar.pack(side=tk.TOP, fill=tk.X)

def update_img_display(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv_img)
    tk_img = ImageTk.PhotoImage(pil_img)
    img_label.config(image=tk_img)
    img_label.image = tk_img

def apply_filter(cv_img):
    lower_bound = np.array(hsv_values['lower'], dtype=np.uint8)
    upper_bound = np.array(hsv_values['upper'], dtype=np.uint8)
    hsv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
    result = cv2.bitwise_and(cv_img, cv_img, mask=mask)
    return result

def select_file():
    filename = filedialog.askopenfilename()
    if filename:
        global photo_img
        photo_img = cv2.imread(filename)
        filtered_img = apply_filter(photo_img)
        update_img_display(filtered_img)

def update_values(lower_upper, h_s_v, value):
    hsv_values[lower_upper][h_s_v] = value
    if 'photo_img' in globals():
        filtered_img = apply_filter(photo_img)
        update_img_display(filtered_img)


def display_photostream():
    pass


def open_filter_window():
    global photo_img
    global hsv_values
    hsv_values = {'lower': [0, 0, 0], 'upper': [255, 255, 255]}
    
    # Initialize the filter window
    filter_window = tk.Toplevel(root)
    filter_window.title('Filter window')
    
    # Create a frame for the sliders
    sliders_frame = tk.Frame(filter_window)
    sliders_frame.grid(column=1, row=0, sticky='nsew')
    
    # Create sliders for HSV lower and upper bounds
    for i, bound in enumerate(['lower', 'upper']):
        for j, channel in enumerate(['H', 'S', 'V']):
            label = tk.Label(sliders_frame, text=f'{bound} {channel}')
            label.grid(row=3*i, column=j)
            
            slider = tk.Scale(sliders_frame, from_=0, to=255, orient='horizontal', command=lambda v, bound=bound, channel=j: update_values(bound, channel, int(v)))
            slider.grid(row=3*i+1, column=j)
    
    # Button to select a file
    file_button = tk.Button(filter_window, text='Select file', command=select_file)
    file_button.grid(column=1, row=1)
    
    # Display the image
    global img_label
    img_label = tk.Label(filter_window)
    img_label.grid(column=0, row=0)

# Create toolbar frame
toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)
toolbar.pack(side=tk.TOP, fill=tk.X)

# Create the drop-down menu
settings = tk.Menu(root)
root.config(menu = settings)
filter_menu = tk.Menu(settings)
settings.add_cascade(label ='Settings', menu = filter_menu)
filter_menu.add_command(label ='Add Filter', command = open_filter_window)

# Add action buttons
btn_text = ["Select regions [F8]", "Save regions", "Load Selections", 
            "Take Pictures of regions", "Clear selections", "Display Photostream", 
            "Open Command Window"]
btn_commands = [select_regions, save_areas_of_interest, load_areas_of_interest,
                take_pictures_of_regions, clear_selections, display_photostream,
                open_command_window]

btn_vars = [tk.BooleanVar() for _ in btn_text]  # Variable for each button

for i, (text, command, var) in enumerate(zip(btn_text, btn_commands, btn_vars)):
    if i == 0:  # Check button for 'Select regions' button
        btn = tk.Checkbutton(toolbar, text=text, variable=var, command=command)
    else:  # Normal button for other buttons
        btn = tk.Button(toolbar, text=text, command=command)
    btn.grid(row=0, column=i)
    buttons.append(btn)  # Add button to list

label = tk.Label(root)
label.pack()

update_image()
root.mainloop()
