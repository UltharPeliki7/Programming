import easyocr
reader = easyocr.Reader(["en"])

print(reader.readtext("image5_filtered.png"))
print("image5")
print(reader.readtext("image1_filtered.png"))
print("image1")
print(reader.readtext("image2_filtered.png"))
print("image2")
print(reader.readtext("image6_filtered.png"))
print("image6")
print(reader.readtext("image7_filtered.png"))
print("image7")
print(reader.readtext("bankrightclick.png"))
print("bankrightclickimage")