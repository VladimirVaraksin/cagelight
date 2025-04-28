from utils import save_video
from ultralytics import YOLO
from cv_draw import draw_ellipse, draw_traingle
from object_detection import annotate_objects
import cv2
import numpy as np
import yaml

VALID_IDS = set(range(1, 26))

# YOLO-Modell laden
PLAYER_DETECTION_MODEL = YOLO('yolo-Weights/last1.pt')
# Klassenliste
classNames = list(PLAYER_DETECTION_MODEL.names.values())
#print(PLAYER_DETECTION_MODEL.names.values())

def main():
    start = True
    change_botsort(0.7)
    cap = cv2.VideoCapture('videos/test.mp4') #read video
    frames = []  # store frames
    while True:
        ret, frame = cap.read() #read frame
        if not ret:
            break #if no frame, break
        results = PLAYER_DETECTION_MODEL.track(source=frame#, stream=True
                                               ,verbose=False, persist=True,
                                                   tracker='botsort.yaml'#, classes=[0, 1, 2]
                                               )
        if start:
            change_botsort(0.95)
            start = False

        annotate_objects(results, frame)
        cv2.imshow('Frame', frame)
        frames.append(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

    #save_video(frames, 'videos/output.avi')


previous_players = {}  # Globale Variable, die Positionen von letztem Frame speichert

def change_botsort(value):
    with open("botsort.yaml", "r") as f:
        bot_cfg = yaml.safe_load(f)
        bot_cfg["new_track_thresh"] = value
    with open("botsort.yaml", "w") as f:
        yaml.dump(bot_cfg, f)
"""
def get_closest_id(center, l_previous_players, taken_ids):
    min_dist = float('inf')
    best_id = -1
    for pid, prev_center in l_previous_players.items():
        if pid in taken_ids:
            continue
        dist = np.linalg.norm(np.array(center) - np.array(prev_center))
        if dist < min_dist:
            min_dist = dist
            best_id = pid
    return best_id

def annotate_objects(results, frame):
    global previous_players
    current_players = {}
    taken_ids = set()

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            box_id = int(box.id[0]) if box.id is not None else -1

            # Zentrum des Spielers
            center = ((x1 + x2) // 2, (y1 + y2) // 2)

            if box_id in VALID_IDS:
                l_id = box_id
            else:
                # ID durch Matching aus vorherigem Frame finden
                matched_id = get_closest_id(center, previous_players, taken_ids)
                if matched_id != -1:
                    l_id = matched_id
                else:
                    # Nimm eine freie ID aus VALID_IDS
                    available_ids = VALID_IDS - taken_ids
                    l_id = min(available_ids) if available_ids else -1

            if l_id != -1:
                taken_ids.add(l_id)
                current_players[l_id] = center  # merke Position für nächstes Frame

                # Zeichnen
                label = classNames[cls] if cls < len(classNames) else "Unknown"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, f'{label} ID: {l_id}', (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    previous_players = current_players.copy()
"""

if __name__ == "__main__":
    main()