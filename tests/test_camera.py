import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pick_and_place_ur3.camera import Camera, CameraConfig


def test_load_config_sets_current_config():
    cfg = CameraConfig(
        cam_index=0,
        cam_width=640,
        cam_height=480,
        crop_x=10,
        crop_y=20,
        crop_width=100,
        crop_height=80,
    )
    cam = Camera("/tmp/test_camera.ini", cfg)

    cam.initialize()
    cam.load_config()

    assert cam.current_config == cfg

if __name__ == "__main__":
    test_load_config_sets_current_config()