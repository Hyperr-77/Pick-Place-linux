import cv2
import numpy as np

def detect_contours(segmented_image, min_contour_area: int, max_contour_area: int) -> list:
    """Detect contours and only return the ones that fit the criteria"""
    contours, _ = cv2.findContours(segmented_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_contours = []
    for contour in contours:
        contour_area = cv2.contourArea(contour)
        # Exclude contours that are too small or too large
        if contour_area < min_contour_area or contour_area > max_contour_area:
            continue
        detected_contours.append(contour)

    return detected_contours

def detect_rectangles(detected_contours: list) -> list:
    """Detect the smallest possible rectangle for every contour,
    a rectangle is represented as a center (x,y), size (w,h) and an angle"""
    rectangles = []
    for contour in detected_contours:
        rectangles.append(cv2.minAreaRect(contour))

    return rectangles

def calculate_contour_average(contours: list) -> dict[str, int]:
    """Calculate the overall centerpoint of all contours"""
    if not contours:
        raise ValueError("At least one contour is required")
    merged_contours = np.vstack(contours)
    center_x = int(np.mean(merged_contours[:, 0, 0]))    
    center_y = int(np.mean(merged_contours[:, 0, 1]))
    return {"x": center_x, "y": center_y}