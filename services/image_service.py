# # services/image_service.py
# # Image processing functions: enhancement, edge detection and summary.

# import numpy as np
# import cv2
# from PIL import Image
# from typing import Tuple

# def enhance_and_analyze_image(image: Image.Image) -> Tuple:
#     """
#     Convert PIL image to grayscale numpy array, apply histogram equalization,
#     compute edges and return metrics + a short human comment.
#     Returns: (equalized_image_pil, edges_image_pil, mean_intensity, edge_density, comment)
#     """
#     # Convert to grayscale numpy array
#     img_array = np.array(image.convert('L'))
#     equalized = cv2.equalizeHist(img_array)
#     edges = cv2.Canny(equalized, 100, 200)

#     # Calculate metrics
#     mean_intensity = float(np.mean(equalized))
#     edge_density = float(np.mean(edges > 0) * 100)  # percent

#     # Basic human-readable comment
#     if mean_intensity < 50:
#         comment = "The image appears quite dark. Make sure it's properly scanned."
#     elif mean_intensity > 200:
#         comment = "The image seems very bright. Check for overexposure."
#     elif edge_density < 10:
#         comment = "The image has low edge density. It might be blurry or low in detail."
#     else:
#         comment = "Image appears to be of good quality. Further analysis requires specialized tools."

#     # Convert numpy arrays back to PIL for Streamlit display
#     equalized_pil = Image.fromarray(equalized)
#     edges_pil = Image.fromarray(edges)

#     return equalized_pil, edges_pil, mean_intensity, edge_density, comment





# services/image_service.py

import numpy as np
import cv2
from PIL import Image
from typing import Tuple

# ------ Enhancement Methods Based on Modality ------

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

# ------ MAIN FUNCTION ------

def enhance_and_analyze_image(image: Image.Image, modality: str) -> Tuple:
    """
    Convert PIL -> grayscale np array, enhance based on modality,
    compute edges & return enhanced image + metrics + summary.
    Returns: (enhanced_image_pil, edges_image_pil, mean_intensity, edge_density, comment)
    """

    # Convert to grayscale numpy array
    img_array = np.array(image.convert('L'))

    # Enhancement based on modality from UI
    if modality == "X-ray":
        enhanced = enhance_xray(img_array)
    elif modality == "CT":
        enhanced = enhance_ct(img_array)
    elif modality == "MRI":
        enhanced = enhance_mri(img_array)
    else:
        enhanced = enhance_generic(img_array)

    # Edge detection for metric
    edges = cv2.Canny(enhanced, 100, 200)

    # Calculate metrics
    mean_intensity = float(np.mean(enhanced))
    edge_density = float(np.mean(edges > 0) * 100)

    # Quality Text
    if mean_intensity < 50:
        comment = "The image appears dark. It may be underexposed or scanned poorly."
    elif mean_intensity > 200:
        comment = "The image looks bright. Possible overexposure or low tissue contrast."
    elif edge_density < 5:
        comment = "Extremely low structural detail. Possible blur or low resolution."
    elif edge_density < 10:
        comment = "Moderate structural detail. Might lack clarity."
    else:
        comment = "Image has good contrast and detail for further analysis."

    # PIL format for UI use
    enhanced_pil = Image.fromarray(enhanced)
    edges_pil = Image.fromarray(edges)

    return enhanced_pil, edges_pil, mean_intensity, edge_density, comment
