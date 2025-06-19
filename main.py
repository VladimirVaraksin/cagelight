# this script is used to record a soccer match, detect players and the ball using YOLOv11, and save the data to a database or a local file.
# CageLight project - Soccer Match Recording and Analysis
# library imports
from typing import Optional
from app import start_dashboard, update_dashboard
from object_detection import save_objects, player_model, ball_model, player_actions, player_model_2, ball_model_2
from db_save_player import create_player_table, insert_many_players
from camera_utils import release_sources, setup_cam_streams
from utils import annotate_frame, create_pitch_frame, draw_pitch, SoccerPitchConfiguration, injury_warning, create_voronoi_frame, TeamAssigner
import time
import cv2
import os
import json
import argparse
import threading
import webbrowser
import numpy as np
import logging

# Constants for game configuration
DURATION_GAME = 5400
FPS_DEFAULT = 30
HALF_TIME_DURATION = 900
RESOLUTION_DEFAULT = (1280, 720)
SAVE_FOLDER = 'output'
CAM_IDS_DEFAULT = (0,)  # Default camera IDs
START_AFTER_DEFAULT = 0
STANDARD_RESOLUTION = ((1280, 720), None)
BALL_CLASS_ID = 32
WARNING_THRESHOLD = 5
PERSON_CLASS_ID = 0
CONFIDENCE_THRESHOLD_BALL = 0.4
data = []
USE_VIDEO = True  # Set to True to use video files for testing, False to use camera streams
CREATE_PLAYER_TABLE = False  # Set to True to create the player table in the database

# GameConfig Class for game configuration
class GameConfig:
    def __init__(self, lcl_args=None):
        self.duration_game = lcl_args.spieldauer if lcl_args and lcl_args.spieldauer else DURATION_GAME
        self.half_time_duration = lcl_args.halbzeitdauer if lcl_args and lcl_args.halbzeitdauer else HALF_TIME_DURATION
        self.fps = lcl_args.fps if lcl_args and lcl_args.fps else FPS_DEFAULT
        self.resolution = tuple(lcl_args.resolution) if lcl_args and lcl_args.resolution else RESOLUTION_DEFAULT
        self.cam_ids = lcl_args.cam_ids if lcl_args and lcl_args.cam_ids else CAM_IDS_DEFAULT
        self.start_after = lcl_args.start_after if lcl_args and lcl_args.start_after else START_AFTER_DEFAULT
        self.team_colors = lcl_args.team_colors if lcl_args and lcl_args.team_colors else TeamAssigner.default_colors
        self.team_names = lcl_args.team_names if lcl_args and lcl_args.team_names else ["Team 1", "Team 2"]
        self.create_player_table = lcl_args.create_player_table if lcl_args and lcl_args.create_player_table is not None else CREATE_PLAYER_TABLE
        self.use_video = lcl_args.use_video if lcl_args and lcl_args.use_video is not None else USE_VIDEO
        TeamAssigner.team_colors = {name: color for name, color in zip(self.team_names, self.team_colors)} if self.team_colors else {}


def validate_inputs(config):
    for arg in (config.duration_game, config.half_time_duration, config.fps, config.start_after):
        if arg < 0:
            raise ValueError("Ungültige Eingabewerte. Alle Werte müssen >= 0 sein.")
    for cam_id in config.cam_ids:
        if cam_id < 0:
            raise ValueError("Ungültige Kamera-ID. Kamera-IDs müssen >= 0 sein.")
    if config.resolution not in STANDARD_RESOLUTION:
        raise ValueError("Ungültige Auflösung. Aktuell nur 1280x720 erlaubt.")

def setup_video_streams(paths=None):
    video_steams = []
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file {path} does not exist.")
    for path in paths:
        video_stream = cv2.VideoCapture(path)
        if not video_stream.isOpened():
            raise RuntimeError(f"Video {path} could not be opened.")
        video_steams.append(video_stream)
    return video_steams


def process_frames(frame = None, frame_2 = None, match_time = 0.0):
    frame_data, frame_data_2 = [], []
    if frame is not None:
        players = player_model.track(source=frame, stream=True, verbose=False, persist=True,
                                     tracker='bytetrack/bytetrack.yaml', classes=[PERSON_CLASS_ID])
        ball = ball_model.predict(source=frame, verbose=False, classes=[BALL_CLASS_ID], conf=CONFIDENCE_THRESHOLD_BALL)
        frame_data = save_objects([*players, *ball], frame, match_time, 0)

    if frame_2 is not None:
        players_2 = player_model_2.track(source=frame_2, stream=True, verbose=False, persist=True,
                                       tracker='bytetrack/bytetrack.yaml', classes=[PERSON_CLASS_ID])
        ball_2 = ball_model_2.predict(source=frame_2, verbose=False, classes=[BALL_CLASS_ID], conf=CONFIDENCE_THRESHOLD_BALL)
        frame_data_2 = save_objects([*players_2, *ball_2], frame_2, match_time, 1)

    return frame_data, frame_data_2


def update_frames_and_dashboard(frame, frame_2, frame_data, frame_data_2, pitch_frame, voronoi_frame, match_time):
    frame_all = frame_data + frame_data_2
    if frame_all:
        data.append(frame_all)
        if frame_data:
            frame = annotate_frame(frame, frame_data)
        if frame_data_2:
            frame_2 = annotate_frame(frame_2, frame_data_2)
        pitch_frame = create_pitch_frame(pitch_frame, frame_all)
        voronoi_frame = create_voronoi_frame(voronoi_frame, frame_all)

    warnings = injury_warning(player_actions, match_time, threshold=10)
    warning_lines = [f"Warning: Player {w[0]} has been {w[1]} for {w[2]:.2f} seconds." for w in warnings]

    update_dashboard(frame, frame_2, pitch_frame, voronoi_frame, warning_lines)



def main(lcl_args: Optional[argparse.Namespace] = None) -> None:
    config = GameConfig(lcl_args)
    logging.basicConfig(level=logging.INFO)
    try:
        validate_inputs(config)
    except ValueError as e:
        logging.error(e)
        return
    halbzeit_gedruckt = False

    os.makedirs(SAVE_FOLDER, exist_ok=True) # create a directory for saving output locally if it doesn't exist
    if config.create_player_table:
        create_player_table()  # Uncomment if you want to create the player table in the database
    time.sleep(config.start_after)

    if config.use_video: # test for debugging using a video file
        try:
            video_streams = setup_video_streams(paths=["videos/cam_right.mp4", "videos/cam_left.mp4"])
            #video_stream = cv2.VideoCapture("videos/black.mp4")
            #video_streams = [video_stream]
        except (FileNotFoundError, RuntimeError) as e:
            logging.error(e)
            print("Fehler beim Öffnen der Videodateien. Bitte überprüfen Sie die Pfade.")
            return
    else:
        video_streams, video_writers = setup_cam_streams(config.cam_ids, RESOLUTION_DEFAULT, SAVE_FOLDER)
        if not video_streams:
            logging.error("Kamera konnte nicht geöffnet werden.")
            return

    # Start the Flask dashboard in a background thread
    threading.Thread(target=start_dashboard, daemon=True).start()
    time.sleep(1) # Wait for the dashboard to start

    webbrowser.open("http://localhost:5050") # Open the dashboard in the default web browser

    # initialize pitch and voronoi frames
    pitch_frame_base = draw_pitch(SoccerPitchConfiguration(), scale=0.5)
    voronoi_frame_base = draw_pitch(SoccerPitchConfiguration(), scale=0.5)
    demo_frame = np.zeros((pitch_frame_base.shape[0], pitch_frame_base.shape[1], 3), dtype=np.uint8)

    update_dashboard(demo_frame, demo_frame, pitch_frame_base, voronoi_frame_base, [])
    start_time = time.time()  # Startzeitpunkt der Aufnahme

    while True:
        frames = []
        for video_stream in video_streams:
            ret, frame = video_stream.read()
            if not ret:
                logging.error("Frame konnte nicht gelesen werden.")
                break
            frames.append(frame)
        if not frames:
            logging.error("Keine Frames von den Videoquellen erhalten.")
            break
        elif len(frames) < 2:
            frames.append(None) # Append None if the second frame is not available

        match_time = time.time() - start_time
        if not halbzeit_gedruckt and match_time >= config.duration_game / 2:
            logging.info("Halbzeitpause...")
            halbzeit_gedruckt = True
            time.sleep(config.half_time_duration)

        if match_time >= config.duration_game + config.half_time_duration:
            logging.info("Spiel beendet.")
            break


        frame_data, frame_data_2 = process_frames(frames[0], frames[1], match_time)
        update_frames_and_dashboard(frames[0], frames[1], frame_data, frame_data_2, pitch_frame_base.copy(), voronoi_frame_base.copy(), match_time)
        # Save the frames
        if not config.use_video:
            for video_writer, v_frame in zip(video_writers, frames):
                    video_writer.write(v_frame)



    if config.use_video:
        release_sources(video_streams)  # Release the video streams
    else:
        release_sources(video_writers+video_streams)
        logging.info("\nSaving collected data to database...This may take a while.\n")
        insert_many_players(data)  # Save the collected data to the database

    # Save the collected data to a local file
    with open(os.path.join(SAVE_FOLDER, 'live_output.json'), 'w') as jf:
        json.dump(data, jf, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konfiguriere die Spielaufnahme.")
    parser.add_argument("--spieldauer", type=int, help="Dauer des Spiels (Sekunden)")
    parser.add_argument("--halbzeitdauer", type=int, help="Halbzeitpause (Sekunden)")
    parser.add_argument("--fps", type=int, help="Bilder pro Sekunde")
    parser.add_argument("--resolution", type=int, nargs=2, metavar=('BREITE', 'HÖHE'))
    parser.add_argument("--cam_ids", type=int, nargs=2, help="Kamera-ID (z.B. 0, 1)")
    parser.add_argument("--start_after", type=int, help="Startverzögerung (Sekunden)")
    parser.add_argument("--team_colors", type=str, nargs=2, help="Teamfarben in Hex-Format (z.B. #B2A48A #154460)")
    parser.add_argument("--team_names", type=str, nargs=2, help="Teamnamen (z.B. Team1 Team2)")
    parser.add_argument("--create_player_table", type=bool, help="Erstelle die Spieler-Tabelle in der Datenbank (True/False)")
    parser.add_argument("--use_video", type=bool, help="Verwende Videodateien für das Testen (True/False)")
    args = parser.parse_args()
    main(args)
