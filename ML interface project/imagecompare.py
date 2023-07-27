import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import os

# Function to apply HSV filter to image
def apply_hsv_filter(image, lower_h, lower_s, lower_v, upper_h, upper_s, upper_v):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_bound = np.array([lower_h, lower_s, lower_v])
    upper_bound = np.array([upper_h, upper_s, upper_v])

    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    filtered_image = cv2.bitwise_and(image, image, mask=mask)

    return filtered_image

# Function to compare images using edge detection
def compare_edge_images(imageA, imageB):
    # Apply Canny Edge Detection
    edge_imageA = cv2.Canny(imageA, threshold1=30, threshold2=100)
    edge_imageB = cv2.Canny(imageB, threshold1=30, threshold2=100)

    # If the images are not the same size, we cannot directly compare them
    if edge_imageA.shape != edge_imageB.shape:
        print("Images must be the same size to compare")
        return

    # Calculate the Hamming distance between the two edge images
    hamming_distance = np.sum(edge_imageA != edge_imageB)

    # Maximum possible hamming distance
    max_hamming = edge_imageA.shape[0] * edge_imageA.shape[1]

    # Calculate similarity percentage
    similarity_percentage = ((max_hamming - hamming_distance) / max_hamming) * 100

    return similarity_percentage

# Function to save images
def save_images():
    global imageA, imageB

    imageA_filtered = apply_hsv_filter(imageA, lower_h.get(), lower_s.get(), lower_v.get(), upper_h.get(), upper_s.get(), upper_v.get())
    imageB_filtered = apply_hsv_filter(imageB, lower_h.get(), lower_s.get(), lower_v.get(), upper_h.get(), upper_s.get(), upper_v.get())

    cv2.imwrite('image7_filtered.png', imageA_filtered)
    cv2.imwrite('image6_filtered.png', imageB_filtered)

# Create the root window
root = Tk()

# Read the images
imageA = cv2.imread('image7.png', cv2.IMREAD_COLOR)
imageB = cv2.imread('image6.png', cv2.IMREAD_COLOR)

# Create variables for the HSV values
lower_h = IntVar(value=0)
lower_s = IntVar(value=0)
lower_v = IntVar(value=0)
upper_h = IntVar(value=179)
upper_s = IntVar(value=255)
upper_v = IntVar(value=255)

# Function to update the images and the comparison value
def update(*args):
    global imageA, imageB

    # Apply the HSV filter to the images
    imageA_filtered = apply_hsv_filter(imageA, lower_h.get(), lower_s.get(), lower_v.get(), upper_h.get(), upper_s.get(), upper_v.get())
    imageB_filtered = apply_hsv_filter(imageB, lower_h.get(), lower_s.get(), lower_v.get(), upper_h.get(), upper_s.get(), upper_v.get())

    # Update the image labels
    imageA_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageA_filtered, cv2.COLOR_BGR2RGB)))
    imageB_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageB_filtered, cv2.COLOR_BGR2RGB)))
    label_imageA.config(image=imageA_tk)
    label_imageA.image = imageA_tk
    label_imageB.config(image=imageB_tk)
    label_imageB.image = imageB_tk

    # Update the comparison value
    similarity_percentage = compare_edge_images(imageA_filtered, imageB_filtered)
    label_comparison_value.config(text=str(similarity_percentage))

# Create the HSV sliders
Scale(root, from_=0, to=179, orient=HORIZONTAL, label='Lower Hue', variable=lower_h, command=update).pack()
Scale(root, from_=0, to=255, orient=HORIZONTAL, label='Lower Saturation', variable=lower_s, command=update).pack()
Scale(root, from_=0, to=255, orient=HORIZONTAL, label='Lower Value', variable=lower_v, command=update).pack()
Scale(root, from_=0, to=179, orient=HORIZONTAL, label='Upper Hue', variable=upper_h, command=update).pack()
Scale(root, from_=0, to=255, orient=HORIZONTAL, label='Upper Saturation', variable=upper_s, command=update).pack()
Scale(root, from_=0, to=255, orient=HORIZONTAL, label='Upper Value', variable=upper_v, command=update).pack()

# Create the image labels
imageA_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageA, cv2.COLOR_BGR2RGB)))
imageB_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageB, cv2.COLOR_BGR2RGB)))
label_imageA = Label(root, image=imageA_tk)
label_imageA.pack(side=LEFT)
label_imageB = Label(root, image=imageB_tk)
label_imageB.pack(side=LEFT)

# Create the comparison value label
label_comparison_value = Label(root, text='')
label_comparison_value.pack()

# Create the save button
Button(root, text='Save Images', command=save_images).pack()

# Start the GUI
root.mainloop()
