from ultralytics import YOLO
from team_assigner import TeamAssigner

team_assigner = TeamAssigner()

# YOLO-Modell laden
MODEL_PATH = 'models/last1.pt'
PLAYER_DETECTION_MODEL = YOLO(MODEL_PATH)
BALL_MODEL = YOLO(MODEL_PATH)

# Klassenliste
classNames = list(PLAYER_DETECTION_MODEL.names.values())

# --- Detection ---
def save_objects(results, frame, timestamp, camera_id=0):
    data = []
    height, width = frame.shape[:2]

    for model_results in results:
        for r in model_results:
            for box in r.boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Normalize bounding box coordinates
                norm = lambda val, dim: round(val / dim, 4)
                norm_x1, norm_y1 = norm(x1, width), norm(y1, height)
                norm_x2, norm_y2 = norm(x2, width), norm(y2, height)

                cls = int(box.cls[0])
                label = classNames[cls] if cls < len(classNames) else "Unknown"
                confidence = round(float(box.conf[0]), 2)
                l_id = int(box.id[0]) if box.id is not None else -1
                team = "unknown"

                if label in {"player", "goalkeeper", "ball"} and l_id != -1:
                    # Assign team based on player color for players and goalkeepers
                    if label in {"player", "goalkeeper"}:
                        bbox = (x1, y1, x2, y2)
                        player_color = team_assigner.get_player_color(frame, bbox)
                        team = team_assigner.assign_team(player_color)
                    # Common entry for all detected objects
                    common_entry = {
                        "tracking_id": l_id if label != "ball" else 0,
                        "object_type": label,
                        "team": team,
                        "object_position": [[norm_x1, norm_y1, norm_x2, norm_y2]],
                        "timestamp": timestamp,
                        "confidence": confidence,
                        "camera_id": camera_id,
                        "action": "unknown",
                        "x_min": norm_x1,
                        "y_min": norm_y1,
                        "x_max": norm_x2,
                        "y_max": norm_y2
                    }

                    data.append(common_entry)
    return data