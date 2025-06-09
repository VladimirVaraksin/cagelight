import cv2
import numpy as np
from utils import draw_pitch, draw_points_on_pitch, SoccerPitchConfiguration
CONFIG = SoccerPitchConfiguration()
import supervision as sv

def create_pitch_frame(pitch_frame, entries):
    """
    Draws annotations on the frame for each object entry.

    Parameters:
        frame (np.ndarray): The video frame to annotate.
        entries (list[dict]): List of detection entries (from save_objects).

    Returns:
        np.ndarray: Annotated frame.
    """
    # Listen für beide Teams
    team1_points = []
    team2_points = []

    for entry in entries:
        if entry.get("object_type") == "ball":
            continue

        pitch_pos = np.array(entry.get("pitch_position"), dtype=np.float32) * 100
        tracking_id = entry.get("tracking_id")
        team = entry.get("team")

        point = (pitch_pos[0], pitch_pos[1], tracking_id)

        if team == "Team 1":
            team1_points.append(point)
        elif team == "Team 2":
            team2_points.append(point)

    # Structured dtype: x, y, id
    dtype = [('x', np.float32), ('y', np.float32), ('id', 'U50')]
    pitch_points_team1 = np.array(team1_points, dtype=dtype)
    pitch_points_team2 = np.array(team2_points, dtype=dtype)

    pitch_frame = draw_points_on_pitch(
        config=CONFIG,
        xy=pitch_points_team1,
        face_color=sv.Color.from_hex('00BFFF'),
        edge_color=sv.Color.BLACK,
        radius=16,
        pitch=pitch_frame)

    pitch_frame = draw_points_on_pitch(
        config=CONFIG,
        xy=pitch_points_team2,
        face_color=sv.Color.from_hex('FF4500'),
        edge_color=sv.Color.BLACK,
        radius=16,
        pitch=pitch_frame)
    return pitch_frame