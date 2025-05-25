from ultralytics import YOLO
from detection_utils import annotate_objects
import cv2
import yaml

# YOLO-Modell laden
PLAYER_DETECTION_MODEL = YOLO('yolo-Weights/player_ball.pt')
PITCH_MODEL = YOLO('yolo-Weights/pitch_keypoints.pt')
# Klassenliste
classNames = list(PLAYER_DETECTION_MODEL.names.values())

def main():
    start = True
    change_botsort(0.7)
    cap = cv2.VideoCapture('videos/test.mp4') #read video
    frames = []  # store frames
    frame_num = 0
    while True:
        ret, frame = cap.read() #read frame
        if not ret:
            break #if no frame, break
        results = PLAYER_DETECTION_MODEL.track(source=frame#, stream=True
                                               ,verbose=False, persist=True,
                                                   tracker='botsort.yaml', classes=[0, 1, 2]
                                               )
        if start:
            change_botsort(0.95)
            start = False

        annotate_objects(results, frame)

        results = PITCH_MODEL.predict(frame)
        frame = results[0].plot()

        frame_num += 1
        cv2.imshow('Frame', frame)
        frames.append(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def change_botsort(value):
    with open("botsort.yaml", "r") as f:
        bot_cfg = yaml.safe_load(f)
        bot_cfg["new_track_thresh"] = value
    with open("botsort.yaml", "w") as f:
        yaml.dump(bot_cfg, f)


if __name__ == "__main__":
    main()