# Documentation for camera.py

This file contains information about the classes, class methods and functions defined in camera.py.

## CameraConfig

```python
class CameraConfig(
    cam_index: int,
    cam_width: int,
    cam_height: int,
    crop_x: int,
    crop_y: int,
    crop_width: int,
    crop_height: int
) -> CameraConfig
```

Holds the in-memory camera configuration data.
> [!NOTE]
> This class has an `@dataclass(frozen=true)` decorator which automatically creates dunder methods, the frozen parameter makes the class variables constant/unchangable.

### Attributes

| Name | Type | Description |
| :--- | :--- | :--- |
| `cam_index` | `int` | Camera index passed to `cv2.videocapture()` function. |
| `cam_width` | `int` | Camera frame width in pixels. |
| `cam_height` | `int` | Camera frame height in pixels. |
| `crop_x` | `int` | x position of the top-left corner of the cropped frame, must be less then `cam_width`. |
| `crop_y` | `int` | y position of the top-left corner of the cropped frame. |
| `crop_width` | `int` | width of the cropped frame. |
| `crop_height` | `int` | height of the cropped frame. |



---

### Methods

#### `validate`

```python
def validate(self) -> None
```

Checks if all parameters are valid.

* **Parameters:**
  * `arg1` (`list[str]`): Description of the required argument.
  * `arg2` (`dict | None`, optional): Description of the optional argument. Defaults to `None`.
* **Returns:**
  * `bool`: `True` if the operation succeeded, `False` otherwise.
* **Raises:**
  * `ValueError`: If `arg1` is empty.

---

### Example Usage

```python
# Initialize the class
instance = ClassName(param1="example", param2=25)

# Run a method
result = instance.method_name(arg1=["a", "b"])
print(result)  # Output: True
```