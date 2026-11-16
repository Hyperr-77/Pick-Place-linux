import cv2
import numpy as np
from ..database import Database

def classify_objects(feature_vectors: list, database: Database, default_eps: float, rectangles: list, full_image, background_image) -> tuple[list[int], list[int | None]]:
    """Classify vectors and save image examples for clusters created from a frame."""
    if rectangles is not None and len(rectangles) != len(feature_vectors):
        raise ValueError("Each feature vector must have a corresponding rectangle")
    if full_image is not None and rectangles is None:
        raise ValueError("Rectangles are required when saving cluster images")
    if full_image is None:
        raise ValueError("Full frame image required for database modification during object classification")
    if background_image is None:
        raise ValueError("Background image required for database modification during object classification")
    
    assigned_clusters = []
    assigned_bins = []
    clusters = []
    for cluster in database.stream_clusters():
        vector = np.frombuffer(cluster["vector"], dtype=np.float32)
        clusters.append((cluster["id"], cluster["eps"], vector))

    for index, vector in enumerate(feature_vectors):
        vector = np.asarray(vector, dtype=np.float32).flatten()
        vector_length = np.linalg.norm(vector)
        if vector_length == 0:
            assigned_clusters.append(-1)
            assigned_bins.append(None)
            continue
        vector_normal = vector / vector_length

        best_match_cluster = None
        best_similarity = -1.0
        best_eps = default_eps
        for cluster_id, eps, cluster_vector in clusters:
            if cluster_vector.shape != vector.shape:
                raise ValueError(f"Cluster {cluster_id} has {cluster_vector.size} features; "f"received {vector.size}")
            cluster_length = np.linalg.norm(cluster_vector)
            if cluster_length == 0:
                continue
            cluster_normal = cluster_vector / cluster_length
            similarity = np.dot(cluster_normal, vector_normal)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_cluster = cluster_id
                best_eps = eps

        if best_match_cluster is not None and best_similarity >= best_eps:
            assigned_cluster = best_match_cluster
        else:
            # Add a new cluster to the cluster table in the database
            assigned_cluster = database.add_cluster(vector.astype(np.float32).tobytes(), default_eps)
            clusters.append((assigned_cluster, default_eps, vector.copy()))
            
            # Extract preview image from full image
            corners = cv2.boxPoints(rectangles[index]).astype(int)
            x, y, width, height = cv2.boundingRect(corners)
            image_height, image_width = full_image.shape[:2]
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(image_width, x + width), min(image_height, y + height)
            preview_image = full_image[y1:y2, x1:x2]
            if preview_image.size == 0:
                raise ValueError("A cluster preview rectangle is outside the frame")

            # Encode images
            preview_ok, preview_bytes = cv2.imencode(".jpg", preview_image)
            full_ok, full_bytes = cv2.imencode(".jpg", full_image)
            background_ok, background_bytes = cv2.imencode(".jpg", background_image)

            if not preview_ok or not full_ok or not background_ok:
                raise RuntimeError("Failed to encode images during database preperation")

            # Add new cluster data to the ui-data table in the database
            if not database.add_ui(assigned_cluster, preview_bytes.tobytes(), full_bytes.tobytes(), background_bytes.tobytes()):
                raise RuntimeError(f"Failed to save UI images for cluster {assigned_cluster}")

        assigned_clusters.append(assigned_cluster)
        bin_data = database.get_bin(assigned_cluster)
        assigned_bins.append(bin_data["id"] if bin_data is not None else None)

    return assigned_clusters, assigned_bins