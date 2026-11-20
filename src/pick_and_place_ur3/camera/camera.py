import configparser
from dataclasses import dataclass
import cv2
import os
from numpy import ndarray


_CAMERA_KEYS = (
    "cam_index",
    "cam_width",
    "cam_height",
    "crop_x",
    "crop_y",
    "crop_width",
    "crop_height",
)

@dataclass(frozen=True)
class CameraConfig:
    """Store and validate camera settings."""

    cam_index: int
    cam_width: int
    cam_height: int
    crop_x: int
    crop_y: int
    crop_width: int
    crop_height: int

    def validate(self) -> None:
        """Check that camera and crop settings are within valid bounds."""
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

class Camera:
    capture: cv2.VideoCapture | None = None

    def __init__(self, config_path: str) -> None:
        """Initialize camera configuration and capture state."""
        self.config_path = config_path

        self.config_parser: configparser.ConfigParser | None = None
        self.current_config: CameraConfig | None = None

    def initialize(self, initial_config_path: str) -> None:
        """Initialize the camera using the default configuration."""
        self.config_parser = configparser.ConfigParser()
        self.load_config(initial_config_path)
        if self.current_config is None:
            raise RuntimeError("Could not propperly load given camera config while initializing.")
        self.save_config(self.current_config)
        self.apply_config()

    def save_config(self, config: CameraConfig) -> None:
        """Save the current camera configuration to the config file."""
        if config is None or self.config_parser is None:
            raise ValueError(f"Camera must be initialized before saving config.")

        config.validate()
        self.config_parser["camera_config"] = {key: str(getattr(config, key)) for key in _CAMERA_KEYS}
        
        with open(self.config_path, "w") as f:
            self.config_parser.write(f)

    def load_config(self, config_path: str) -> None:
        """Load and validate the saved camera configuration."""
        if self.config_parser is None:
            raise RuntimeError("Cannot load saved camera configuration before initialization.")

        self.config_parser.read(config_path)
        config = self.config_parser["camera_config"]

        if config == None:
            raise RuntimeError("Tried to load config but it doesn't exist.")
        
        self.current_config = CameraConfig(
            **{key: int(config[key]) for key in _CAMERA_KEYS}
        )
        self.current_config.validate()

    def apply_config(self) -> None:
        """Apply the current config to the camera."""
        if self.current_config is None:
            raise RuntimeError("Camera must be initialized before applying config")

        self.current_config.validate()

        if self.capture is not None:
            self.capture.release()
            self.capture = None

        capture = cv2.VideoCapture(self.current_config.cam_index)
        if not capture.isOpened():
        
            capture.release()
            raise RuntimeError(f"Could not open camera {self.current_config.cam_index}")

        for prop, value in (
            (cv2.CAP_PROP_FRAME_WIDTH, self.current_config.cam_width),
            (cv2.CAP_PROP_FRAME_HEIGHT, self.current_config.cam_height)
        ):
            if not capture.set(prop, value):
                capture.release()
                raise RuntimeError(f"Could not set camera property {prop}")

        Camera.capture = capture

    def getFrame(self) -> ndarray:
        """Read and return a cropped frame from the camera."""
        if self.current_config is None or self.capture is None or Camera.capture is None:
            raise RuntimeError("Camera must be initialized before reading")

        success, frame = Camera.capture.read()
        if not success:
            raise RuntimeError("Could not read a frame from the camera")

        x = self.current_config.crop_x
        y = self.current_config.crop_y
        width = self.current_config.crop_width
        height = self.current_config.crop_height
        cropped_frame = frame[y:y + height, x:x + width]
        if cropped_frame.size == 0:
            raise RuntimeError("Camera frame is smaller than the configured crop")
        return cropped_frame

    def __enter__(self) -> CameraConfig:
        """Return the current configuration for a context manager block."""
        if self.current_config is None:
            raise RuntimeError("Camera is not initialized")
        return self.current_config

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        """Apply the current configuration when leaving a context manager block."""
        if exception_type is not None:
            print(f"Error detected before saving camera config: {exception_value}. Changes are not saved.")
        self.apply_config()