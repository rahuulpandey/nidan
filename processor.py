# transforming and enhancing images using open cv 

import cv2
import numpy as np
from PIL import Image

#Image Conversion
def pil_to_gray_np(pil_img):
    img = np.array(pil_img)
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img

#Enhancement Methods using open cv
def enhance_xray(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    enhanced = cv2.filter2D(enhanced, -1, kernel)
    return enhanced

def enhance_ct(img):
    img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_norm)
    return enhanced

def enhance_mri(img):
    denoised = cv2.GaussianBlur(img, (3, 3), 0)
    enhanced = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)
    return enhanced

def enhance_generic(img):
    return enhance_xray(img)

# ---------- Analysis ----------
def analyze_quality(img):
    mean_intensity = float(np.mean(img))
    edges = cv2.Canny(img, 50, 150)
    edge_density = float(np.count_nonzero(edges) / img.size * 100)

    if edge_density < 3:
        comment = "Low detail/blurry image."
    elif edge_density < 8:
        comment = "Moderate detail; slightly unclear."
    else:
        comment = "Good edge detail."

    if mean_intensity < 60:
        comment += " Also dark (underexposed)."
    elif mean_intensity > 190:
        comment += " Also bright (overexposed)."

    return mean_intensity, edge_density, comment

def to_pil(img_np):
    return Image.fromarray(img_np).convert("L").convert("RGB")
