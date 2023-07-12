import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from pynput import mouse, keyboard
import os
import json

DISPLAY_WINDOW = [True]
root = tk.Tk()
label = tk.Label(root)
label.pack()

mouse_controller = mouse.Controller()
keyboard_controller = keyboard.Controller()

z_pressed = [False]
y_pressed = [False]
drag_coords = [None, None]
img_count = [0]
areasofinterest = []

# Load areas of interest from file
try:
    with open('areasofinterest.txt', 'r') as file:
        areasofinterest = json.load(file)
except FileNotFoundError:
    open('areasofinterest.txt', 'w').close()
except json.JSONDecodeError:
    pass  # If file is empty, do nothing

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        if y_pressed[0] and pressed:
            drag_coords[0] = (x, y)
        elif y_pressed[0] and not pressed:
            drag_coords[1] = (x, y)

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
                    areasofinterest.append([left, top, width, height])

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

def on_press(key):
    global areasofinterest
    if key == keyboard.Key.space:
        DISPLAY_WINDOW[0] = not DISPLAY_WINDOW[0]
        if DISPLAY_WINDOW[0]:
            root.deiconify()
        else:
            root.withdraw()
    elif key == keyboard.KeyCode.from_char('p'):
        keyboard_controller.press(keyboard.Key.space)
        keyboard_controller.release(keyboard.Key.space)
    elif key == keyboard.KeyCode.from_char('o'):
        mouse_controller.click(mouse.Button.left, 1)
    elif key == keyboard.KeyCode.from_char('z'):
        for index, (left, top, width, height) in enumerate(areasofinterest):
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save(f'image_{img_count[0]}_{index}.png')
        img_count[0] += 1
    elif key == keyboard.KeyCode.from_char('y'):
        y_pressed[0] = not y_pressed[0]
    elif key == keyboard.KeyCode.from_char('t'):
        areasofinterest = []
    elif key == keyboard.KeyCode.from_char('s'):
        with open('areasofinterest.txt', 'w') as file:
            json.dump(areasofinterest, file)

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

def update_image():
    screenshot = pyautogui.screenshot()
    screenshot_draw = screenshot.convert("RGBA")
    draw = ImageDraw.Draw(screenshot_draw)
    
    for (left, top, width, height) in areasofinterest:
        draw.rectangle([(left, top), (left + width, top + height)], outline="yellow")
    
    screenshot = ImageTk.PhotoImage(screenshot_draw)
    if DISPLAY_WINDOW[0]:
        label.configure(image=screenshot)
        label.image = screenshot
    root.after(1000, update_image)
    
update_image()
root.mainloop()
