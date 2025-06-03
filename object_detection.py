from ultralytics import YOLO
from utils import TeamAssigner, ViewTransformer
import numpy as np
# Initialize helper classes
team_assigner = TeamAssigner()
view_transformer = ViewTransformer()

# Load YOLOv8 models (player and ball use the same model in our case)
MODEL_PATH = 'models/yolov8n.pt'
player_model = YOLO(MODEL_PATH)
ball_model = YOLO(MODEL_PATH)

# Class names from the model
class_names = list(player_model.names.values())

def save_objects(results, frame, timestamp, camera_id=0):
    """
    Processes YOLO detection results and returns structured data for each object (player or ball).

    Parameters:
        results: YOLO model detection results
        frame: Current video frame (numpy array)
        timestamp: Float timestamp from time.time()
        camera_id: Optional integer camera ID

    Returns:
        A list of dictionaries, each containing tracking and object metadata.
    """
    data = []
    height, width = frame.shape[:2]  # Extract frame dimensions

    # Loop over each detection in the result set
    for detections in results:
        for box in detections.boxes:
            # Extract bounding box coordinates (x1, y1, x2, y2)
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Compute the bottom-center point of the bounding box
            point = np.array([(x1 + x2) / 2, y2], dtype=np.float32)

            # Transform to pitch (real-world) coordinates
            pitch_point = view_transformer.transform_point(point)

            # Skip detections outside the defined field area
            if pitch_point is None:
                continue

            # Normalize the bounding box with respect to frame size
            bbox = [x1, y1, x2, y2]
            norm_bbox = [round(b / dim, 4) for b, dim in zip(bbox, [width, height, width, height])]

            # Get class index and label
            cls = int(box.cls[0])
            label = class_names[cls] if cls < len(class_names) else "Unknown"
            confidence = round(float(box.conf[0]), 2)

            # Normalize label names
            if label == "person":
                label = "player"
            elif label == "sports ball":
                label = "ball"

            # Get tracking ID (if available), else use -1
            box_id = getattr(box, 'id', None)
            tracking_id = int(box_id[0]) if isinstance(box_id, (list, np.ndarray)) else int(box_id) if box_id else -1

            # Only continue if the object is of interest and has a valid tracking ID
            if label in {"player", "ball"} and tracking_id != -1:
                # Assign team color for players
                if label == "player":
                    player_color = team_assigner.get_player_color(frame, bbox)
                    team = team_assigner.assign_team(player_color)
                else:
                    team = "none"

                # Extract pitch coordinates
                pitch_x, pitch_y = pitch_point[0]
                print(pitch_x, pitch_y)

                # Format timestamp as MM:SS:MS
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                milliseconds = int((timestamp % 1) * 1000)
                match_time_formatted = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

                # Build the data entry
                entry = {
                    "tracking_id": tracking_id if label != "ball" else 0,
                    "object_type": label,
                    "team": team,
                    "pitch_position": [round(float(pitch_x), 2), round(float(pitch_y), 2)],
                    "timestamp": match_time_formatted,
                    "confidence": confidence,
                    "camera_id": camera_id,
                    "action": "unknown",  # Placeholder for future action classification
                    "bbox_xyxy": norm_bbox,
                }

                # Append the structured entry to the result list
                data.append(entry)

    return data