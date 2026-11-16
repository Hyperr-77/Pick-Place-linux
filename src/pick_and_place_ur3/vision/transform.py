import numpy as np
from tflite_runtime.interpreter import Interpreter

interpreter = Interpreter(
    model_path="mobilenet_v2.tflite",
    num_threads=4,
)
interpreter.allocate_tensors()

def transform_batch(objects: list) -> list:
    if not objects:
        return []

    # The crops from OpenCV are BGR; the model expects RGB float values in [0, 255].
    batch = np.ascontiguousarray(
        np.stack(objects)[..., ::-1],
        dtype=np.float32,
    )

    # Prepare tensor
    input_detail = interpreter.get_input_details()[0]
    if not np.array_equal(batch.shape, input_detail["shape"]):
        interpreter.resize_tensor_input(input_detail["index"], batch.shape)
        interpreter.allocate_tensors()
        input_detail = interpreter.get_input_details()[0]

    # Run model
    interpreter.set_tensor(input_detail["index"], batch)
    interpreter.invoke()

    output_detail = interpreter.get_output_details()[0]
    features = interpreter.get_tensor(output_detail["index"]).astype(np.float32)
    return [features[i] for i in range(features.shape[0])]