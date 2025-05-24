import cv2
from ultralytics import YOLO
from cv_draw import draw_ellipse, draw_traingle
from team_assigner import TeamAssigner

team_assigner = TeamAssigner()

# YOLO-Modell laden
PLAYER_DETECTION_MODEL = YOLO('yolo-Weights/last1.pt')
BALL_MODEL = YOLO('yolo-Weights/last1.pt')
# Klassenliste
classNames = list(PLAYER_DETECTION_MODEL.names.values())
#print(PLAYER_DETECTION_MODEL.names)

# --- Detection ---
def annotate_objects(results, frame):
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            #confidence = round(float(box.conf[0]), 2)
            cls = int(box.cls[0])
            l_id = int(box.id[0]) if box.id is not None else -1
            label = classNames[cls] if cls < len(classNames) else "Unknown"

            if label in {"player", "goalkeeper"}:
                bbox = (x1, y1, x2, y2)
                player_color = team_assigner.get_player_color(frame, bbox)
                team = team_assigner.assign_team(player_color)
                frame = draw_ellipse(frame, box.xyxy[0], (255, 255, 255))
                cv2.putText(frame, f'id: {l_id} team: {team}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            elif label == 'ball':
                frame = draw_traingle(frame, box.xyxy[0], (128, 128, 128))
                #cv2.putText(frame, f'id: {l_id} c:{confidence}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            # elif label == 'referee':
            #     frame = draw_ellipse(frame, box.xyxy[0], (0, 0, 0))