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
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
                bbox_width, bbox_height = x2 - x1, y2 - y1

                norm = lambda val, dim: round(val / dim, 4)
                norm_cx, norm_cy = norm(center_x, width), norm(center_y, height)
                norm_w, norm_h = norm(bbox_width, width), norm(bbox_height, height)

                cls = int(box.cls[0])
                label = classNames[cls] if cls < len(classNames) else "Unknown"
                confidence = round(float(box.conf[0]), 2)
                l_id = int(box.id[0]) if box.id is not None else -1

                team = "unknown"
                if label in {"player", "goalkeeper"}:
                    bbox = (x1, y1, x2, y2)
                    player_color = team_assigner.get_player_color(frame, bbox)
                    team = team_assigner.assign_team(player_color)

                common_entry = {
                    "tracking_id": l_id if label != "ball" else 0,
                    "object_type": label,
                    "team": team,
                    "object_position": [[norm_cx, norm_cy, norm_w, norm_h]],
                    "timestamp": timestamp,
                    "confidence": confidence,
                    "camera_id": camera_id,
                    "action": "unknown",
                    "x_center": norm_cx,
                    "y_center": norm_cy,
                    "width": 0.02 if label == "ball" else norm_w,
                    "height": 0.02 if label == "ball" else norm_h
                }

                if label in {"player", "goalkeeper", "ball"}:
                    data.append(common_entry)

                #save entry to Database
    return data