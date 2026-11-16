import configparser
from dataclasses import dataclass

from pathlib import Path

import cv2


@dataclass(frozen=True)
class CameraConfig:
    cam_index: int
    cam_width: int
    cam_height: int
    crop_x: int
    crop_y: int
    crop_width: int
    crop_height: int

    def validate(self) -> None:
        if self.cam_index < 0:
            raise ValueError("cam_index must be non-negative")
        if self.cam_width <= 0 or self.cam_height <= 0:
            raise ValueError("camera width and height must be positive")
        if self.crop_x < 0 or self.crop_y < 0:
            raise ValueError("crop offsets must be non-negative")
        if self.crop_width <= 0 or self.crop_height <= 0:
            raise ValueError("crop dimensions must be positive")
        if self.crop_x + self.crop_width > self.cam_width:
            raise ValueError("crop exceeds frame width")
        if self.crop_y + self.crop_height > self.cam_height:
            raise ValueError("crop exceeds frame height")


_CAMERA_KEYS = (
    "cam_index",
    "cam_width",
    "cam_height",
    "crop_x",
    "crop_y",
    "crop_width",
    "crop_height",
)

def _read_settings(settings_path: str | Path) -> configparser.ConfigParser:
    settings = configparser.ConfigParser()
    if not settings.read(settings_path):
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    return settings


def _camera_config_path(settings: configparser.ConfigParser) -> Path:
    return Path(settings["file paths"]["camera_config"]).expanduser()


def load_camera_config(settings_path: str | Path) -> CameraConfig:
    settings = _read_settings(settings_path)
    defaults = settings["default camera config"]

    camera_file = configparser.ConfigParser()
    camera_file.read_dict(
        {"camera": {key: defaults[key] for key in _CAMERA_KEYS}}
    )
    camera_file.read(_camera_config_path(settings))
    values = camera_file["camera"]

    config = CameraConfig(**{key: values.getint(key) for key in _CAMERA_KEYS})
    config.validate()
    return config


def save_camera_config(
    config: CameraConfig, settings_path: str | Path
) -> None:
    config.validate()
    settings = _read_settings(settings_path)
    camera_path = _camera_config_path(settings)
    camera_path.parent.mkdir(parents=True, exist_ok=True)

    camera_file = configparser.ConfigParser()
    camera_file["camera"] = {
        key: str(getattr(config, key)) for key in _CAMERA_KEYS
    }
    with camera_path.open("w", encoding="utf-8") as file:
        camera_file.write(file)


class Camera:
    def __init__(self, config: CameraConfig) -> None:
        config.validate()
        self.config = config
        self.capture: cv2.VideoCapture | None = None

    def _apply_config(self, config: CameraConfig | None = None) -> None:
        if config is not None:
            config.validate()
            self.config = config

        if self.capture is not None:
            self.capture.release()
            self.capture = None

        capture = cv2.VideoCapture(self.config.cam_index)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Could not open camera {self.config.cam_index}")

        for prop, value in (
            (cv2.CAP_PROP_FRAME_WIDTH, self.config.cam_width),
            (cv2.CAP_PROP_FRAME_HEIGHT, self.config.cam_height),
        ):
            if not capture.set(prop, value):
                capture.release()
                raise RuntimeError(f"Could not set camera property {prop}")

        self.capture = capture

    def getFrame(self):
        if self.capture is None:
            raise RuntimeError("Camera is not open")

        success, frame = self.capture.read()
        if not success:
            raise RuntimeError("Could not read a frame from the camera")

        x = self.config.crop_x
        y = self.config.crop_y
        width = self.config.crop_width
        height = self.config.crop_height
        cropped_frame = frame[y:y + height, x:x + width]
        if cropped_frame.size == 0:
            raise RuntimeError("Camera frame is smaller than the configured crop")
        return cropped_frame

    def __enter__(self) -> :
        return self.config

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
