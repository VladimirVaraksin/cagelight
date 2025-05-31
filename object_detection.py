from ultralytics import YOLO
from team_assigner import TeamAssigner
from utils import ViewTransformer, SoccerPitchConfiguration
from db_save_player import insert_record
import numpy as np

# initialize TeamAssigner
team_assigner = TeamAssigner()

# Load the YOLO models for pitch keypoints, player and ball detection
MODEL_PATH = 'models/player_ball.pt'
PLAYER_DETECTION_MODEL = YOLO(MODEL_PATH)
BALL_MODEL = YOLO(MODEL_PATH)
PITCH_MODEL = YOLO('models/pitch_keypoints.pt')

# Initialize standard pitch dimensions and vertices
CONFIG = SoccerPitchConfiguration()
# Convert pitch vertices to a numpy array for homography transformation
PITCH_REFERENCE_POINTS = np.array(CONFIG.vertices)


# Klassenliste
classNames = list(PLAYER_DETECTION_MODEL.names.values())

def save_objects(results, frame, timestamp, camera_id=0):
    data = []
    height, width = frame.shape[:2]

    # --- Step 1: Keypoint detection and homography ---
    pitch_detections = PITCH_MODEL.predict(frame, verbose=False)

    try:
        keypoints_xy = np.array(pitch_detections[0].keypoints.xy[0])
    except (IndexError, AttributeError):
        print("No keypoints detected.")
        keypoints_xy = np.zeros((0, 2))

    non_zero_mask = ~np.all(keypoints_xy == 0, axis=1)

    frame_reference_points = keypoints_xy[non_zero_mask]

    if len(PITCH_REFERENCE_POINTS) != len(non_zero_mask):
        print("Mismatch in reference points. Skipping transformation.")
        transformer = None
    elif len(frame_reference_points) >= 4:
        pitch_reference_points = PITCH_REFERENCE_POINTS[non_zero_mask]
        transformer = ViewTransformer(
            source=frame_reference_points,
            target=pitch_reference_points
        )
    else:
        print("Insufficient keypoints in frame, skipping homography...")
        transformer = None

    # --- Step 2: Object processing ---
    for detections in results:
        for box in detections.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox = [x1, y1, x2, y2]
            norm_bbox = [round(b / dim, 4) for b, dim in zip(bbox, [width, height, width, height])]

            cls = int(box.cls[0])
            label = classNames[cls] if cls < len(classNames) else "Unknown"
            confidence = round(float(box.conf[0]), 2)

            # Handle ID safely
            box_id = getattr(box, 'id', None)
            if box_id is not None:
                tracking_id = int(box_id[0]) if hasattr(box_id, '__getitem__') else int(box_id)
            else:
                tracking_id = -1

            if label in {"player", "goalkeeper", "ball"} and tracking_id != -1:
                # Determine team
                if label in {"player", "goalkeeper"}:
                    player_color = team_assigner.get_player_color(frame, bbox)
                    team = team_assigner.assign_team(player_color)
                else:
                    team = "none"

                # Transform position on the pitch
                if transformer is not None:
                    player_point = np.array([[(x1 + x2) / 2, y2]])
                    pitch_xy = transformer.transform_points(points=player_point)
                    pitch_x, pitch_y = float(pitch_xy[0][0]), float(pitch_xy[0][1])


                    # This is a workaround to ensure pitch_x and pitch_y are in meters
                    #config = SoccerPitchConfiguration() # Initialize the configuration
                    #frame_width = frame.shape[1] # Get the width of the frame
                    #frame_height = frame.shape[0] # Get the height of the frame

                    #pitch_x_meters = (pitch_x / frame_width) * config.PITCH_LENGTH_METERS # Convert pitch_x to meters
                    #pitch_y_meters = (pitch_y / frame_height) * config.PITCH_WIDTH_METERS # Convert pitch_y to meters





                else:
                    pitch_x, pitch_y = 0.0, 0.0

                # Build and append entry
                match_time_formatted = f"{int(timestamp // 60):02d}:{int(timestamp % 60):02d}"
                entry = {
                    "tracking_id": tracking_id if label != "ball" else 0,
                    "object_type": label,
                    "team": team,
                    "pitch_position": [pitch_x, pitch_y], # "pitch_position": [pitch_x_meters, pitch_y_meters], here is where to uncomment when real time.
                    "timestamp": match_time_formatted,
                    #"timestamp": timestamp,
                    "confidence": confidence,
                    "camera_id": camera_id,
                    "action": "unknown",
                    "bbox_xyxy": norm_bbox,
                }
                # Insert the entry into the database
                #insert_record(entry)

                data.append(entry)

    return data
