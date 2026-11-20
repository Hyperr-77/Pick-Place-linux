import os
import cv2
import time
import numpy as np
import argparse
import configparser
from tflite_runtime.interpreter import Interpreter

from .camera import Camera
from .database import Database
from .vision.segment import segment
from .vision.detect import detect_contours, detect_rectangles
from .vision.transform import transform_batch
from .vision.classify import classify_objects


SETTINGS_PATH = 'settings.conf'

settings_parser = configparser.ConfigParser()
settings_parser.read(SETTINGS_PATH)

PATHS = settings_parser["file_paths"]
MODEL_PATH = os.path.expanduser(PATHS["model"])
DATABASE_PATH = os.path.expanduser(PATHS["database"])
CAMERA_CONFIG_PATH = os.path.expanduser(PATHS["camera_config"])

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(os.path.dirname(CAMERA_CONFIG_PATH), exist_ok=True)

CAMERA_CONFIG = settings_parser["camera_config"]
VISION_CONFIG = settings_parser["vision_config"]

def start(args) -> None:
    print("Starting client...")

    model = Interpreter(
        model_path=MODEL_PATH,
        num_threads=4, # Optimal for raspberry pi
    )
    model.allocate_tensors()

    database = Database(DATABASE_PATH)

    cam = Camera(CAMERA_CONFIG_PATH)

    cam.initialize(SETTINGS_PATH)

    cam.getFrame()

    input_shape = model.get_input_details()[0]["shape"]
    crop_height, crop_width = int(input_shape[1]), int(input_shape[2])

    try:
        print("Waiting for camera calibration...")
        for i in range(50):
            background = cam.getFrame()
        while True:
            frame = cam.getFrame()

            segmented = segment(
                frame,
                background,
                VISION_CONFIG.getint("low", fallback=0),
                VISION_CONFIG.getint("high", fallback=255)
            )

            detected = detect_contours(
                segmented,
                VISION_CONFIG.getint("min_area", fallback=0),
                VISION_CONFIG.getint("max_area", fallback=1000000)
            )

            rectangles = detect_rectangles(detected)
            object_crops = []
            for contour in detected:
                x, y, width, height = cv2.boundingRect(contour)
                crop = frame[y:y + height, x:x + width]
                if crop.size == 0:
                    raise ValueError("Detected contour produced an empty image crop")
                object_crops.append(
                    cv2.resize(crop, (crop_width, crop_height), interpolation=cv2.INTER_AREA)
                )

            transformed = transform_batch(object_crops, model)

            classified = classify_objects(
                transformed,
                database,
                VISION_CONFIG.getfloat("default_eps", fallback=100),
                rectangles,
                frame,
                background
            )

            if not draw_frame(frame, background, segmented, rectangles, classified[0]):
                break
    finally:
        if Camera.capture is not None:
            Camera.capture.release()
            Camera.capture = None
        cv2.destroyAllWindows()

def stop(args: argparse._ArgumentGroup) -> None:
    print("Stopping client...")

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser(
        "start",
        help="Start the Pick&Place client"
    )
    start_parser.set_defaults(handler=start)

    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop the Pick&Place client"
    )
    stop_parser.set_defaults(handler=stop)

    args = parser.parse_args()
    args.handler(args)
    return 0

def draw_frame(frame, background, segmented, rectangles, ids):
    if len(rectangles) != len(ids):
        raise ValueError("Rectangles and ids are not the same size")

    new_image = frame.copy()
    segmented_image = cv2.cvtColor(segmented, cv2.COLOR_GRAY2BGR)

    for i, rectangle in enumerate(rectangles):
        label = str(ids[i])
        corners = cv2.boxPoints(rectangle).astype(np.int32)
        cv2.polylines(new_image, [corners], True, (0, 150, 255), 2)
        center_x, center_y = np.round(rectangle[0]).astype(int)
        cv2.putText(
            new_image,
            label,
            (int(center_x), max(int(center_y) - 10, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

    cv2.putText(segmented_image, "Segmented", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 150, 255), 2)
    cv2.putText(new_image, "Output", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 150, 255), 2)
    cv2.imshow("Output", np.hstack((segmented_image, new_image, background)))
    key = cv2.waitKey(1) & 0xFF
    return key not in (27, ord("q"), ord("Q"))