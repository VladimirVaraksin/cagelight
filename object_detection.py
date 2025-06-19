# this script processes YOLO detection results and returns structured data for each object (player or ball)
from ultralytics import YOLO
from utils import TeamAssigner, ViewTransformer, PoseClassifier, IDManager
import numpy as np
from collections import deque

# store last N frames of player data
recent_entries = deque(maxlen=100)

id_manager = IDManager(max_age_seconds=3)  # Initialize IDManager with a max age of 3 seconds
team_assigner = TeamAssigner()
view_transformer = ViewTransformer()
pose_classifier = PoseClassifier()

MODEL_PATH = 'models/yolov11n.pt' # Path to the YOLO model
player_model = YOLO(MODEL_PATH)
player_model_2 = YOLO(MODEL_PATH)  # Duplicate model for second camera
ball_model_2 = YOLO(MODEL_PATH)  # Duplicate model for second camera
ball_model = YOLO(MODEL_PATH)

class_names = list(player_model.names.values())
player_actions = {}
FIRST_FRAME = True  # Flag to indicate if it's the first frame

def save_objects(results, frame, timestamp, camera_id=0):
    global FIRST_FRAME, player_actions, recent_entries
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
    #print(recent_entries)
    data = []
    height, width = frame.shape[:2]
    ball_detected = False  # Flag to track if the ball is detected in the current frame
    for detections in results:
        for box in detections.boxes:
            # Extract bounding box coordinates (x1, y1, x2, y2)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # Compute the bottom-center point of the bounding box
            point = np.array([(x1 + x2) / 2, y2], dtype=np.float32)
            # Compute the pitch coordinates using the view transformer
            pitch_point = view_transformer.transform_point(point, camera_id=camera_id)

            # Skip detections outside the defined field area
            # Normalize the bounding box with respect to frame size
            bbox = [x1, y1, x2, y2]
            norm_bbox = [round(b / dim, 4) for b, dim in zip(bbox, [width, height, width, height])]
            # Get class index and label
            cls = int(box.cls[0])
            label = class_names[cls] if cls < len(class_names) else "Unknown"
            confidence = round(float(box.conf[0]), 2)

            # Get tracking ID (if available), else use -1
            box_id = getattr(box, 'id', None)
            tracking_id = int(box_id[0]) if isinstance(box_id, (list, np.ndarray)) else int(box_id) if box_id else -1
            #if FIRST_FRAME:
            tracking_id = camera_id * 10 + tracking_id  # Ensure unique ID across cameras
            if label == "person":
                label = "player"
            elif label == "sports ball":
                label = "ball"
                tracking_id = 0  # Assign a fixed ID for the ball

            if pitch_point is None:
                if label == "player":
                    continue
                elif label == "ball":
                    for entry in data:
                        if entry["tracking_id"] == 0:
                            ball_detected = True
                            break
                    if ball_detected:
                        continue
                    # If the ball is not detected, we can still create an entry with a default position
                    for i, past in enumerate(recent_entries):
                        if past["tracking_id"] == 0:
                            pitch_point = np.array(past["pitch_position"], dtype=np.float32).reshape(1, 2)
                    if pitch_point is None:
                        # If no past entry exists, use a default position
                        pitch_point = np.array([0.0, 0.0], dtype=np.float32).reshape(1, 2)


            # Only continue if the object is of interest and has a valid tracking ID
            if label in {"player", "ball"} and tracking_id != -1:
                # Extract pitch coordinates
                pitch_x, pitch_y = pitch_point[0]
                #print(tracking_id, timestamp, pitch_x, pitch_y)
                entry_action = "unknown"  # Initialize action as unknown
                if label == "player":
                    # Assign the team based on player color
                    team = team_assigner.get_player_team(tracking_id)
                    if team is None:
                        if TeamAssigner.default_colors is not None:
                            team = team_assigner.assign_team_from_color(team_assigner.get_player_color(frame, bbox),tracking_id)
                        else:
                            # If the player is not assigned to a team, get the player color and assign a team
                            player_color = team_assigner.get_player_color(frame, bbox, tracking_id)
                            team = team_assigner.assign_team(player_color, tracking_id)
                    # Action classification
                    entry_action = pose_classifier.classify_pose(frame, bbox)
                    # Store the action for the player
                    if entry_action == "lying" or entry_action == "sitting":
                        if tracking_id not in player_actions or player_actions[tracking_id][0] != entry_action:
                            # Update the action if it has changed
                            player_actions[tracking_id] = (entry_action, timestamp)
                    else:
                        if tracking_id in player_actions:
                            del player_actions[tracking_id]  # Remove if action is not lying or sitting
                else:
                    team = "none"


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

                # assign persistent ID
                persistent_id = id_manager.get_persistent_id(tracking_id, entry, recent_entries, first_frame=FIRST_FRAME)
                entry["tracking_id"] = persistent_id

                data.append(entry)

                # store latest player entry (only one per persistent ID)
                for i, past in enumerate(recent_entries):
                    if past["tracking_id"] == persistent_id:
                        recent_entries[i] = entry
                        break
                else:
                    recent_entries.append(entry)


    FIRST_FRAME = False  # Set the flag to False after processing the first frame
    return data