import cv2
import numpy as np

def segment(image, background, low: int, high: int):
    """Seperate the background from the foreground"""
    if image is None or background is None:
        raise ValueError("Image and background must both be loaded")
    if image.shape[:2] != background.shape[:2]:
        background = cv2.resize(
            background, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_AREA
        )
    if image.ndim != 3 or background.ndim != 3 or image.shape[2] != background.shape[2]:
        raise ValueError("Image and background must have the same color-channel count")

    # Convert images to LAB color space
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    background_lab = cv2.cvtColor(background, cv2.COLOR_BGR2LAB).astype(np.float32)
    # Calculate differences for each value
    differenceL = np.abs(image_lab[..., 0] - background_lab[..., 0])
    differenceA = np.abs(image_lab[..., 1] - background_lab[..., 1])
    differenceB = np.abs(image_lab[..., 2] - background_lab[..., 2])
    difference = np.maximum(differenceL * 2.0, np.maximum(differenceA, differenceB))
    difference = cv2.GaussianBlur(difference, (0, 0), 1.0)
    difference = np.clip(difference, 0, 255).astype(np.uint8)

    # Cut out the pixels where the difference is large
    strong = difference >= high
    weak = difference >= low
    # Keep low-difference pixels only when connected to a high-difference pixel.
    _, labels = cv2.connectedComponents(weak.astype(np.uint8), connectivity=8)
    keep = np.unique(labels[strong])
    keep = keep[keep != 0]
    # Create mask cut-out
    mask = np.isin(labels, keep).astype(np.uint8) * 255

    # Close holes in the mask
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    count, connected_image_lab, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    segmented_image = np.zeros_like(mask)
    # Skip the background label (index = 0)
    for stat_index in range(1, count):
        if stats[stat_index, cv2.CC_STAT_AREA] >= 30:
            segmented_image[connected_image_lab == stat_index] = 255

    return segmented_image