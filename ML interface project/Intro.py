import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from pynput import mouse, keyboard
import os

DISPLAY_WINDOW = [True]  # Use a list so that changes are reflected across all functions
root = tk.Tk()
label = tk.Label(root)
label.pack()

# Create a controller for mouse events
mouse_controller = mouse.Controller()

# Create a controller for keyboard events
keyboard_controller = keyboard.Controller()

# flag to indicate that 'z' key was pressed
z_pressed = [False]

# flag to indicate that 'y' key was pressed
y_pressed = [False]

# store the coordinates of the mouse drag event
drag_coords = [None, None]

# Image save count
img_count = [0]

def on_click(x, y, button, pressed):
    if (z_pressed[0] or y_pressed[0]) and button == mouse.Button.left:
        if pressed:
            drag_coords[0] = (x, y)
        else:
            drag_coords[1] = (x, y)

            left = min(drag_coords[0][0], drag_coords[1][0])
            top = min(drag_coords[0][1], drag_coords[1][1])
            width = abs(drag_coords[0][0] - drag_coords[1][0])
            height = abs(drag_coords[0][1] - drag_coords[0][1])

            if z_pressed[0]:
                # Capture and save the screenshot
                screenshot = pyautogui.screenshot(region=(left, top, width, height))
                screenshot.save(f'image_{img_count[0]}.png')
                img_count[0] += 1

                # Reset z_pressed flag
                z_pressed[0] = False
            elif y_pressed[0]:
                # Reset y_pressed flag
                y_pressed[0] = False

def on_drag(x, y, button):
    print('Mouse dragged to {0}'.format((x, y)))

# Define and start a mouse listener that responds to clicks and drags
mouse_listener = mouse.Listener(on_click=on_click, on_drag=on_drag)
mouse_listener.start()

def on_press(key):
    print('Key {0} pressed'.format(key))
    if key == keyboard.Key.space:
        DISPLAY_WINDOW[0] = not DISPLAY_WINDOW[0]
        if DISPLAY_WINDOW[0]:
            root.deiconify()
        else:
            root.withdraw()
    elif key == keyboard.KeyCode.from_char('p'):
        # Simulate a space key press
        keyboard_controller.press(keyboard.Key.space)
        keyboard_controller.release(keyboard.Key.space)
    elif key == keyboard.KeyCode.from_char('o'):
        # Simulate a left mouse click at the current cursor position
        mouse_controller.click(mouse.Button.left, 1)
    elif key == keyboard.KeyCode.from_char('z'):
        z_pressed[0] = True
    elif key == keyboard.KeyCode.from_char('y'):
        y_pressed[0] = True

def on_release(key):
    print('Key {0} released'.format(key))
    if key == keyboard.Key.esc:
        print('Stop listener')
        return False

# Define and start a keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()

def update_image():
    screenshot = pyautogui.screenshot()
    
    if drag_coords[1] is not None:
        # If a rectangle has been selected, draw it on the screenshot
        screenshot_draw = screenshot.copy()
        screenshot_draw = screenshot_draw.convert("RGBA")
        screenshot_draw_draw = ImageDraw.Draw(screenshot_draw)
        
        left = min(drag_coords[0][0], drag_coords[1][0])
        top = min(drag_coords[0][1], drag_coords[1][1])
        right = max(drag_coords[0][0], drag_coords[1][0])
        bottom = max(drag_coords[0][1], drag_coords[1][1])
        
        screenshot_draw_draw.rectangle([(left, top), (right, bottom)], outline="yellow")
        screenshot = Image.alpha_composite(screenshot, screenshot_draw)

    screenshot = ImageTk.PhotoImage(screenshot)
    if DISPLAY_WINDOW[0]:
        label.configure(image=screenshot)
        label.image = screenshot
    root.after(1000, update_image)  # update every 1 sec (1000 ms)

update_image()  # start updating
root.mainloop()
