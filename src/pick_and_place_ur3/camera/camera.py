import configparser
from dataclasses import dataclass
import cv2
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

    def __init__(self, config_path: str, default_config: CameraConfig) -> None:
        """Initialize camera configuration and capture state."""
        self.config_path = config_path
        self.default_config = default_config

        self.saved_config: configparser.ConfigParser | None = None
        self.current_config: CameraConfig | None = None

    def _initialize_camera(self) -> None:
        """Initialize the camera using the default configuration."""
        self._load_config(self.default_config)
        self._apply_config()

    def _save_config(self) -> None:
        """Save the current camera configuration to the config file."""
        if self.current_config is None or self.saved_config is None:
            raise ValueError(f"Camera must be initialized before saving config.")
        self.current_config.validate()
        self.saved_config["camera"] = {key: str(getattr(self.current_config, key)) for key in _CAMERA_KEYS}

        with open(self.config_path, "w") as f:
            self.saved_config.write(f)

    def _load_config(self, config: CameraConfig) -> None:
        """Load and validate the supplied camera configuration."""
        if config is None:
            raise RuntimeError("Cannot load camera configuration before initialization")
        config.validate()
        self.current_config = CameraConfig(**{key: getattr(config, key) for key in _CAMERA_KEYS})

    def _reset_config_item(self, key: str) -> None:
        """Check that the provided key is a camera configuration property."""
        if key not in _CAMERA_KEYS:
            raise ValueError(f"Property: {key} is not a camera property")

    def _apply_config(self) -> None:
        """Open the configured camera and apply its frame dimensions."""
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
        self._apply_config()