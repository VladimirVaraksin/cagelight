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

    for arg in (dauer_spiel, halbzeit_dauer, fps, kameranummer, start_after): # check if any argument is negative
        if arg < 0:
            print("Ungültige Eingabewerte. Alle Werte müssen >= 0 sein.") # exit if any argument is negative
            return

    if resolution not in standard_resolution:
        print("Ungültige Auflösung. Nur 1280x720 oder 1920x1080 erlaubt.") # exit if resolution is not valid
        return

    time.sleep(start_after)
    start_time = time.time() # start the timer for the game duration

    os.makedirs(save_folder, exist_ok=True) # create the output folder if it does not exist
    data = []

    camera = setup_camera(0, resolution[0], resolution[1]) # setup the camera with the specified resolution


    if not camera:
        print(f"Kamera mit Index 0 konnte nicht geöffnet werden.") # exit if camera cannot be opened
        return

    fps = camera.get(cv2.CAP_PROP_FPS)
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) # get the camera resolution
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) # get the camera resolution

    out = cv2.VideoWriter(
        os.path.join(save_folder, 'output_video.mp4'), # specify the output file name
        cv2.VideoWriter_fourcc(*'mp4v'), # 'mp4v' for mp4 format
        fps,
        (width, height)
    )

    halbzeit_gedruckt = False # flag to indicate if halftime has been printed
    create_player_table() # create the player table in the database

    #test for debugging using a video file
    camera = cv2.VideoCapture("videos/test.mp4") # replace with camera index if needed

    while True:
        ret, frame = camera.read() # read a frame from the camera
        if not ret:
            print("Frame konnte nicht gelesen werden.") # exit the loop if no frame is read
            break

        elapsed = time.time() - start_time
        if not halbzeit_gedruckt and elapsed >= dauer_spiel / 2:
            print("Halbzeitpause...") # print a message when halftime is reached
            halbzeit_gedruckt = True
            time.sleep(halbzeit_dauer) # wait for the halftime duration

        if elapsed >= dauer_spiel + halbzeit_dauer:
            print("Spiel beendet.") # exit the loop if the game duration is over
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
        frame_data = save_objects([*players, *ball], frame, time.time(), kameranummer) # save the data to be saved in the database
        print(frame_data)

        data.append(frame_data) # collect the data for later saving to the database

        out.write(frame)
        # Display the frame for debugging purposes
        cv2.imshow('Frame', frame) # show the current frame in a window

        if cv2.waitKey(1) & 0xFF == ord('q'): # exit if 'q' is pressed
            break

    release_sources((camera, out)) # release the camera and video writer resources
    cv2.destroyAllWindows() # close all OpenCV windows
    # Save the collected data to the database
    print("\nSaving collected data to database...This may take a while.\n")
    insert_many_players(data) # save the data to the database

    """   Save the collected data to a local JSON file for debugging purposes
    with open(os.path.join(save_folder, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)
    """

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
# main.py
from camera_utils import setup_camera, release_sources
from object_detection import save_objects, PLAYER_DETECTION_MODEL, BALL_MODEL
from db_save_player import create_player_table
from app import create_app
from threading import Thread
import time
import cv2
import os
import argparse
import webbrowser

def main(lcl_args=None):
    dauer_spiel = 5400
    fps = 30
    halbzeit_dauer = 900
    resolution = (1280, 720)
    kameranummer = 0
    start_after = 0
    save_folder = 'output'
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

    # Start dashboard server
    app, socketio, dashboard_thread = create_app()
    Thread(target=lambda: socketio.run(app, host='0.0.0.0', port=5000)).start()
    webbrowser.open("http://localhost:5000")

    time.sleep(start_after)
    start_time = time.time()
    os.makedirs(save_folder, exist_ok=True)

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

        frame_data = save_objects([*players, *ball], frame, time.time(), kameranummer)
        print(frame_data)

        out.write(frame)

    release_sources((camera, out))

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
