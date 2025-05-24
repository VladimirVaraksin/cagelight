from camera_utils import setup_camera, release_sources
from object_detection import save_objects, PLAYER_DETECTION_MODEL, BALL_MODEL
from db_save_player import create_player_table, insert_many_players
import time
import cv2
import os
import json
import argparse

def main(lcl_args=None):
    dauer_spiel = 5400
    fps = 30
    halbzeit_dauer = 900
    resolution = (1280, 720)
    save_folder = 'output'
    kameranummer = 0
    start_after = 0
    standard_resolution = {(1280, 720), (1920, 1080)}

    if lcl_args is not None:
        dauer_spiel = lcl_args.spieldauer if lcl_args.spieldauer else dauer_spiel
        halbzeit_dauer = lcl_args.halbzeitdauer if lcl_args.halbzeitdauer else halbzeit_dauer
        fps = lcl_args.fps if lcl_args.fps else fps
        resolution = tuple(lcl_args.resolution) if lcl_args.resolution else resolution
        kameranummer = lcl_args.kameranummer if lcl_args.kameranummer else kameranummer
        start_after = lcl_args.start_after if lcl_args.start_after else start_after

    for arg in (dauer_spiel, halbzeit_dauer, fps, kameranummer, start_after):
        if arg < 0:
            print("Ungültige Eingabewerte. Alle Werte müssen >= 0 sein.")
            return

    if resolution not in standard_resolution:
        print("Ungültige Auflösung. Nur 1280x720 oder 1920x1080 erlaubt.")
        return

    time.sleep(start_after)
    start_time = time.time()

    os.makedirs(save_folder, exist_ok=True)
    data = []

    camera = setup_camera(kameranummer, resolution[0], resolution[1])
    if not camera:
        print(f"Kamera mit Index {kameranummer} konnte nicht geöffnet werden.")
        return

    out = cv2.VideoWriter(
        os.path.join(save_folder, 'output_video.mp4'),
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (resolution[0], resolution[1])
    )

    halbzeit_gedruckt = False
    create_player_table()

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Frame konnte nicht gelesen werden.")
            break

        elapsed = time.time() - start_time
        if not halbzeit_gedruckt and elapsed >= dauer_spiel / 2:
            print("Halbzeitpause...")
            halbzeit_gedruckt = True
            time.sleep(halbzeit_dauer)

        if elapsed >= dauer_spiel + halbzeit_dauer:
            print("Spiel beendet.")
            break

        players = PLAYER_DETECTION_MODEL.track(
            source=frame, stream=True, verbose=False, persist=True,
            tracker='bytetrack/bytetrack.yaml', classes=[1, 2]
        )
        ball = BALL_MODEL.track(
            source=frame, stream=True, verbose=False, persist=True,
            tracker='bytetrack/bytetrack_ball.yaml', classes=[0]
        )

        frame_data = save_objects((players, ball), frame, time.time(), kameranummer)
        insert_many_players(frame_data)
        data.append(frame_data)

        out.write(frame)
        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    release_sources({camera, out})
    cv2.destroyAllWindows()
    with open(os.path.join(save_folder, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konfiguriere die Spielaufnahme.")
    parser.add_argument("--spieldauer", type=int, help="Dauer des Spiels (Sekunden)")
    parser.add_argument("--halbzeitdauer", type=int, help="Halbzeitpause (Sekunden)")
    parser.add_argument("--fps", type=int, help="Bilder pro Sekunde")
    parser.add_argument("--resolution", type=int, nargs=2, metavar=('BREITE', 'HÖHE'))
    parser.add_argument("--kameranummer", type=int, help="Kamera-ID (z.B. 0)")
    parser.add_argument("--start_after", type=int, help="Startverzögerung (Sekunden)")
    args = parser.parse_args()
    main(args)

"""
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
    kameranummer = 0  # Standard Kamera-ID
    start_after = 0  # Wartezeit vor dem Start der Aufnahme

    standard_resolution = {(1280, 720), (1920, 1080)}  # Standardauflösung

    if lcl_args is not None:
        dauer_spiel = lcl_args.spieldauer if lcl_args.spieldauer else dauer_spiel
        halbzeit_dauer = lcl_args.halbzeitdauer if lcl_args.halbzeitdauer else halbzeit_dauer
        fps = lcl_args.fps if lcl_args.fps else fps
        resolution = tuple(lcl_args.resolution) if lcl_args.resolution else resolution
        kameranummer = lcl_args.kameranummer if lcl_args.kameranummer else kameranummer
        start_after = lcl_args.start_after if lcl_args.start_after else start_after

    for arg in (dauer_spiel, halbzeit_dauer, fps, kameranummer, start_after):
        if arg < 0:
            print("Ungültige Eingabewerte. Alle Werte müssen größer oder gleich Null sein.")
            return

    if resolution not in standard_resolution:
        print("Ungültige Eingabewerte für Auflösung. Bitte überprüfen Sie die Argumente. Erlaubt sind: 1280x720 oder 1980x1080.")
        return


    time.sleep(start_after)
    start_time = time.time() # Startzeit der Aufnahme

    os.makedirs(save_folder, exist_ok=True)
    data = []

    camera = setup_camera(0, resolution[0], resolution[1])

    if not camera:
        print(f"Failed to open camera with Index {0}.")
        return

    out = cv2.VideoWriter(
        os.path.join(save_folder, 'output_video.mp4'),
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (resolution[0], resolution[1])  # Create a video writer object
    )

    halbzeit_gedruckt = False

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame.")
            break

        elapsed = time.time() - start_time
        if not halbzeit_gedruckt and elapsed >= dauer_spiel / 2:
            print("Halbzeit")
            halbzeit_gedruckt = True
            time.sleep(halbzeit_dauer)

        if elapsed >= dauer_spiel + halbzeit_dauer:
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
        data.append(save_objects((players, ball), frame, time.time(), kameranummer))

        # Write the frame to the video file
        out.write(frame)
        cv2.imshow('Frame', frame)


    release_sources({camera, out})
    with open(os.path.join(save_folder, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konfiguriere die Spielaufnahme.")

    parser.add_argument(
        "--spieldauer",
        type=int,
        help="Gesamtdauer des Spiels in Sekunden."
    )

    parser.add_argument(
        "--halbzeitdauer",
        type=int,
        help="Dauer der Halbzeitpause in Sekunden."
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
    main(args)
"""