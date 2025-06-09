# this script is used to record a soccer match, detect players and the ball using YOLOv11, and save the data to a database or a local file.
# CageLight project
from app import start_dashboard, update_dashboard
from object_detection import save_objects, player_model, ball_model, player_actions
#from db_save_player import create_player_table, insert_many_players
from camera_utils import setup_camera, release_sources
from utils import annotate_frame, create_pitch_frame, draw_pitch, SoccerPitchConfiguration, injury_warning, create_voronoi_frame
import time
import cv2
import os
import json
import argparse
import threading
import webbrowser

def main(lcl_args=None):
    dauer_spiel = 5400
    fps = 30
    halbzeit_dauer = 900
    resolution = (1280, 720)
    save_folder = 'output'
    kameranummer = 0
    start_after = 0
    standard_resolution = ((1280, 720), (1920, 1080))
    halbzeit_gedruckt = False
    data = []
    # create directory for saving output locally if it doesn't exist
    os.makedirs(save_folder, exist_ok=True)
    # create_player_table()  # Uncomment if you want to create the player table in the database

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

    # uncomment the following lines to use a camera instead of a video file
    # video_stream = setup_camera(0, resolution[0], resolution[1])
    #
    # if not video_stream:
    #     print(f"Kamera mit Index 0 konnte nicht geöffnet werden.")
    #     return
    #
    # fps = video_stream.get(cv2.CAP_PROP_FPS)
    # width = int(video_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #
    # out = cv2.VideoWriter(
    #     os.path.join(save_folder, 'output_video.mp4'),
    #     cv2.VideoWriter_fourcc(*'mp4v'),
    #     fps,
    #     (width, height)
    # )

    # test for debugging using a video file
    video_stream = cv2.VideoCapture("videos/action_test_blender.mp4")
    if not video_stream.isOpened():
        print("Video could not be opened.")
        return

    # Start the Flask dashboard in a background thread
    threading.Thread(target=start_dashboard, daemon=True).start()
    time.sleep(2)
    webbrowser.open("http://localhost:5000")

    start_time = time.time()  # Startzeitpunkt der Aufnahme
    while True:
        ret, frame = video_stream.read()
        pitch_frame = draw_pitch(SoccerPitchConfiguration(), scale=0.5)
        voronoi_frame = draw_pitch(SoccerPitchConfiguration(), scale=0.5)

        if not ret:
            print("Frame konnte nicht gelesen werden.")
            break

        match_time = time.time() - start_time
        if not halbzeit_gedruckt and match_time >= dauer_spiel / 2:
            print("Halbzeitpause...")
            halbzeit_gedruckt = True
            time.sleep(halbzeit_dauer)

        if match_time >= dauer_spiel + halbzeit_dauer:
            print("Spiel beendet.")
            break

        players = player_model.track(
            source=frame, stream=True, verbose=False, persist=True,
            tracker='bytetrack/bytetrack.yaml', classes=[0]
        )
        ball = ball_model.track(
            source=frame, stream=True, verbose=False, persist=True,
            tracker='bytetrack/bytetrack_ball.yaml', classes=[32]
        )

        frame_data = save_objects([*players, *ball], frame, match_time, kameranummer)

        if frame_data:
            data.append(frame_data)
            frame = annotate_frame(frame, frame_data)
            pitch_frame = create_pitch_frame(pitch_frame, frame_data)
            voronoi_frame = create_voronoi_frame(voronoi_frame, frame_data)

        warnings = injury_warning(player_actions, match_time, threshold=5)
        warning_lines = []

        for w in warnings:
            msg = f"Warning: Player {w[0]} has been {w[1]} for {w[2]:.2f} seconds."
            #print(msg)
            warning_lines.append(msg)

        update_dashboard(pitch_frame, warning_lines)

        #out.write(frame)
        # Display the frames
        cv2.imshow('Frame', frame)
        cv2.imshow('Pitch', pitch_frame)
        cv2.imshow('Voronoi', voronoi_frame)

        time.sleep(0.001)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #release_sources((video_stream, out))
    video_stream.release()
    cv2.destroyAllWindows()
    # Save the collected data to the database
    # print("\nSaving collected data to database...This may take a while.\n")
    #insert_many_players(data)

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