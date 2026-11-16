import numpy as np

class Plate():
    """Plate class for controlling the plate"""
    def __init__(self) -> None:
        self.tilt_x = 0.5
        self.tilt_y = 0.5
        self.vibrating = False

    def set_flat(self) -> None:
        self.tilt_x = 0.5
        self.tilt_y = 0.5

    def tilt_plate(self, tilt_x: float, tilt_y: float) -> None:
        self.tilt_x = np.clip(tilt_x, 0, 1)
        self.tilt_y = np.clip(tilt_y, 0, 1)

    def set_vibrate(self, mode: bool) -> None:
        self.vibrating = mode