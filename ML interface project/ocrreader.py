import easyocr
import cv2

# Create a reader object
reader = easyocr.Reader(['en'])

# Read an image file
image = cv2.imread('bankrightclick.png')

# Use the reader to detect text in the image
results = reader.readtext(image)

# Create a 2D array
# Each subarray (row) will have the format [bounding_box_coordinates, detected_text]
array_2d = [[res[0], res[1]] for res in results]

# Print the 2D array
for row in array_2d:
    print(row)
