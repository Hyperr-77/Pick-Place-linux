import numpy as np
from tflite_runtime.interpreter import Interpreter

def transform_batch(objects: list, model: Interpreter) -> list:
    if not objects:
        return []

    # The crops from OpenCV are BGR; the model expects RGB float values in [0, 255].
    batch = np.ascontiguousarray(
        np.stack(objects)[..., ::-1],
        dtype=np.float32,
    )

    # Prepare tensor
    input_detail = model.get_input_details()[0]
    if not np.array_equal(batch.shape, input_detail["shape"]):
        model.resize_tensor_input(input_detail["index"], batch.shape)
        model.allocate_tensors()
        input_detail = model.get_input_details()[0]

    # Run model
    model.set_tensor(input_detail["index"], batch)
    model.invoke()

    output_detail = model.get_output_details()[0]
    features = model.get_tensor(output_detail["index"]).astype(np.float32)
    return [features[i] for i in range(features.shape[0])]