# utils.py
# Helper utilities for reading images, encoding, and trimming borders.

import base64
import os
from PIL import Image, ImageChops
from config import IMAGE_FOLDER

def get_base64_image(path):
    """Return data URL (jpg) for embedding in HTML."""
    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded}"

def get_base64_image_raw(path):
    """Return base64 string (useful for img src without data mime)."""
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_base64_png_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def encode_image(img_path):
    """Same as get_base64_image, kept for compatibility with original code."""
    return get_base64_image(img_path)

def trim_image(im: Image.Image):
    """Crop image by removing uniform border (assumes top-left pixel is background)."""
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def get_default_image_paths():
    """Return list of example image paths from image folder."""
    image_files = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"]
    return [os.path.join(IMAGE_FOLDER, img) for img in image_files]
