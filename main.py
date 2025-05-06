from camera_utils import setup_camera, release_sources
from object_detection import save_objects, PLAYER_DETECTION_MODEL, BALL_MODEL
import time
import cv2
import os
import json
import argparse


def main(lcl_args=None):
    # Standard Konfiguration
    dauer_spiel = 5400  # Dauer des Spiels in Sekunden (90 Minuten)
    fps = 30  # Frames pro Sekunde
    halbzeit_dauer = 900  # Dauer der Halbzeitpause in Sekunden (15 Minuten)
    resolution = (1280, 720)  # Auflösung der Kamera
    save_folder = 'output'  # Ordner für die Ausgabedateien
    camera_id = kameranummer = 0  # Standard Kamera-ID
    start_after = 0  # Wartezeit vor dem Start der Aufnahme

    if lcl_args is not None:
        dauer_spiel = lcl_args.spieldauer*60 if lcl_args.spieldauer else dauer_spiel
        halbzeit_dauer = lcl_args.halbzeitdauer*60 if lcl_args.halbzeitdauer else halbzeit_dauer
        fps = lcl_args.fps if lcl_args.fps else fps
        resolution = tuple(lcl_args.resolution) if lcl_args.resolution else resolution
        kameranummer = lcl_args.kameranummer if lcl_args.kameranummer else 0
        start_after = lcl_args.start_after if lcl_args.start_after else 0

    if dauer_spiel < 0 or halbzeit_dauer < 0 or fps <= 0 or resolution[0] <= 0 or resolution[1] <= 0 or kameranummer < 0 or start_after < 0:
        print("Ungültige Eingabewerte. Bitte überprüfen Sie die Argumente.")
        return


    time.sleep(start_after)

    os.makedirs(save_folder, exist_ok=True)
    data = []

    frame_num = 1
    camera = setup_camera(camera_id, resolution[0], resolution[1])

    if not camera:
        print(f"Failed to open camera with ID {camera_id}.")
        return

    out = cv2.VideoWriter(
        os.path.join(save_folder, 'output_video.mp4'),
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (resolution[0], resolution[1])  # Create a video writer object
    )

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame.")
            break

        frame_num += 1  # Framezähler erhöhen

        if frame_num == (dauer_spiel / 2) * fps:
            print("Halbzeit")
            time.sleep(halbzeit_dauer) # 15 Minuten Pause

        if frame_num == dauer_spiel* fps + halbzeit_dauer* fps:
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
        data.append(save_objects(players, frame, frame_num, kameranummer))
        data.append(save_objects(ball, frame, frame_num, kameranummer))
        # Write the frame to the video file
        out.write(frame)

    release_sources({camera, out})
    with open(os.path.join(save_folder, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konfiguriere die Spielaufnahme.")

    parser.add_argument(
        "--spieldauer",
        type=int,
        help="Gesamtdauer des Spiels in Minuten."
    )

    parser.add_argument(
        "--halbzeitdauer",
        type=int,
        help="Dauer der Halbzeitpause in Minuten."
    )

    parser.add_argument(
        "--fps",
        type=int,
        help="Anzahl der Bilder pro Sekunde (Frames per Second) für die Aufnahme."
    )

    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        metavar=('BREITE', 'HÖHE'),
        help="Auflösung der Videoaufnahme im Format: BREITE HÖHE (z. B. 1280 720)."
    )

    parser.add_argument(
        "--kameranummer",
        type=int,
        help="Nummer der verwendeten Kamera z.B 0-3)."
    )

    parser.add_argument(
        "--start_after",
        type=int,
        help="Wartezeit in Sekunden, bevor die Aufnahme beginnt."
    )

    args = parser.parse_args()
    #print(args)
    main(args)