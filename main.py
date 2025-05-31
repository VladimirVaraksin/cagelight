# main.py
from camera_utils import setup_camera, release_sources
from object_detection import save_objects, PLAYER_DETECTION_MODEL, BALL_MODEL
from db_save_player import create_player_table, insert_many_players
import time
import cv2
import os
#import json
import argparse

def main(lcl_args=None):
    dauer_spiel = 5400
    fps = 30
    halbzeit_dauer = 900
    resolution= (1280, 720)
    save_folder = 'output'
    kameranummer = 0
    start_after = 0
    standard_resolution = ((1280, 720), (1920, 1080))

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
    start_time = time.time() # Startzeitpunkt der Aufnahme

    os.makedirs(save_folder, exist_ok=True)
    data = []

    camera = setup_camera(0, resolution[0], resolution[1])


    if not camera:
        print(f"Kamera mit Index 0 konnte nicht geöffnet werden.")
        return

    fps = camera.get(cv2.CAP_PROP_FPS)
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        os.path.join(save_folder, 'output_video.mp4'),
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )

    halbzeit_gedruckt = False
    create_player_table()

    #test for debugging using a video file
    camera = cv2.VideoCapture("videos/test.mp4")

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
        # save the detected players and ball positions for debugging purposes
        match_time = time.time() - start_time
        frame_data = save_objects([*players, *ball], frame, match_time, kameranummer) # save_objects function collects player and ball data with exact timestamp
        #frame_data = save_objects([*players, *ball], frame, time.time(), kameranummer)
        print(frame_data)

        data.append(frame_data)

        out.write(frame)
        # Display the frame for debugging purposes
        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    release_sources((camera, out))
    cv2.destroyAllWindows()
    # Save the collected data to the database
    print("\nSaving collected data to database...This may take a while.\n")
    insert_many_players(data)
#since there is a database connection we do not need to save the data to a local file
    """   Save the collected data to a local JSON file for debugging purposes
    with open(os.path.join(save_folder, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konfiguriere die Spielaufnahme.") # ArgumentParser erstellt ein Argumentenparser-Objekt
    parser.add_argument("--spieldauer", type=int, help="Dauer des Spiels (Sekunden)") # Argument für die Spieldauer in Sekunden
    parser.add_argument("--halbzeitdauer", type=int, help="Halbzeitpause (Sekunden)") # Argument für die Halbzeitpause in Sekunden
    parser.add_argument("--fps", type=int, help="Bilder pro Sekunde") # Argument für die FPS (Frames pro Sekunde)
    parser.add_argument("--resolution", type=int, nargs=2, metavar=('BREITE', 'HÖHE')) # Argument für die Auflösung in Breite und Höhe
    parser.add_argument("--kameranummer", type=int, help="Kamera-ID (z.B. 0)") # Argument für die Kameranummer
    parser.add_argument("--start_after", type=int, help="Startverzögerung (Sekunden)") # Argument für die Startverzögerung in Sekunden
    args = parser.parse_args()
    main(args)

