# this script processes YOLO detection results and returns structured data for each object (player or ball)
from ultralytics import YOLO
from utils import TeamAssigner, ViewTransformer, PoseClassifier
import numpy as np

team_assigner = TeamAssigner()
view_transformer = ViewTransformer()
pose_classifier = PoseClassifier()

MODEL_PATH = 'models/yolov11n.pt'
player_model = YOLO(MODEL_PATH)
ball_model = YOLO(MODEL_PATH)

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
    height, width = frame.shape[:2]
    for detections in results:
        for box in detections.boxes:
            # Extract bounding box coordinates (x1, y1, x2, y2)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # Compute the bottom-center point of the bounding box
            point = np.array([(x1 + x2) / 2, y2], dtype=np.float32)
            # Compute the pitch coordinates using the view transformer
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

            if label == "person":
                label = "player"
            elif label == "sports ball":
                label = "ball"
            # Get tracking ID (if available), else use -1
            box_id = getattr(box, 'id', None)
            tracking_id = int(box_id[0]) if isinstance(box_id, (list, np.ndarray)) else int(box_id) if box_id else -1

            # Only continue if the object is of interest and has a valid tracking ID
            if label in {"player", "ball"} and tracking_id != -1:
                entry_action = "unknown"  # Initialize action as unknown
                if label == "player":
                    # Assign team based on player color
                    team = team_assigner.get_player_team(tracking_id)
                    if team is None:
                        # If the player is not assigned to a team, get the player color and assign a team
                        player_color = team_assigner.get_player_color(frame, bbox)
                        team = team_assigner.assign_team(player_color, tracking_id)
                    # Action classification
                    entry_action = pose_classifier.classify_pose(bbox)
                else:
                    team = "none"
                # Extract pitch coordinates
                pitch_x, pitch_y = pitch_point[0]
                # print pitch coordinates for debugging
                # print(pitch_x, pitch_y)

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
                    "action": entry_action,
                    "bbox_xyxy": norm_bbox,
                }

                data.append(entry)

    return data