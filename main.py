from camera_utils import setup_camera, release_sources
from object_detection import save_objects, PLAYER_DETECTION_MODEL, BALL_MODEL
import time
import cv2
import os
import json

DAUER_SPIEL = 5400  # Dauer des Spiels in Sekunden (90 Minuten)
FPS = 30  # Frames pro Sekunde
HALBZEIT_DAUER = 900  # Dauer der Halbzeitpause in Sekunden (15 Minuten)
RESOLUTION = (1280, 720)  # Auflösung der Kamera
OUTPUT_FOLDER = 'output'  # Ordner für die Ausgabedateien


def main():
    save_folder = os.path.join(OUTPUT_FOLDER, 'output_video')
    os.makedirs(save_folder, exist_ok=True)
    data = []
    camera_id = 0
    frame_num = 1
    camera = setup_camera(camera_id, RESOLUTION[0], RESOLUTION[1])

    if not camera:
        print(f"Failed to open camera with ID {camera_id}.")
        return

    out = cv2.VideoWriter(
        os.path.join(save_folder, 'output_video.mp4'),
        cv2.VideoWriter_fourcc(*'mp4v'),
        FPS,
        (RESOLUTION[0], RESOLUTION[1])  # Create a video writer object
    )

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame.")
            break

        frame_num += 1  # Framezähler erhöhen

        if frame_num == (DAUER_SPIEL / 2) * FPS:
            print("Halbzeit")
            time.sleep(HALBZEIT_DAUER) # 15 Minuten Pause

        if frame_num == DAUER_SPIEL* FPS + HALBZEIT_DAUER* FPS:
            print("Ende des Spiels")
            break

        players = PLAYER_DETECTION_MODEL.track(
            source=frame,
            stream=True,
            verbose=False,
            persist=True,
            tracker='bytetrack/bytetrack.yaml',
            classes=[1, 2]
        )

        ball = BALL_MODEL.track(
            source=frame,
            stream=True,
            verbose=False,
            persist=True,
            tracker='bytetrack/bytetrack_ball.yaml',
            classes=[0]
        )
        data.append(save_objects(players, frame, frame_num))
        data.append(save_objects(ball, frame, frame_num))
        # Write the frame to the video file
        out.write(frame)
        break
    release_sources({camera, out})
    with open(os.path.join(save_folder, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)


if __name__ == "__main__":
    main()