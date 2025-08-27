from PIL import Image

# Open the image
img = Image.open("LookALike/frog2.jpg")

# Convert to grayscale ('L' mode = 8-bit pixels, black and white)
gray_img = img.convert("L")

# Save or display it
gray_img.save("LookALike/frog2.jpg")
