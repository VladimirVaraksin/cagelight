from camera_utils import setup_camera, release_cameras
from object_detection import save_objects, PLAYER_DETECTION_MODEL, BALL_MODEL
import time


DAUER_SPIEL = 5400  # Dauer des Spiels in Sekunden (90 Minuten)
FPS = 30  # Frames pro Sekunde
HALBZEIT_DAUER = 900  # Dauer der Halbzeitpause in Sekunden (15 Minuten)
RESOLUTION = (1280, 720)  # Auflösung der Kamera

def main():
    camera_id = 0
    frame_num = 1
    camera = setup_camera(camera_id, RESOLUTION[0], RESOLUTION[1])
    if not camera:
        print(f"Failed to open camera with ID {camera_id}.")
        return
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

        save_objects(players, frame, frame_num)
        save_objects(ball, frame, frame_num)
    release_cameras(camera)

if __name__ == "__main__":
    main()