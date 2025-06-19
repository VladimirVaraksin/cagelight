import numpy as np
from utils import draw_points_on_pitch, SoccerPitchConfiguration, draw_pitch_voronoi_diagram
CONFIG = SoccerPitchConfiguration()
import supervision as sv

def create_pitch_frame(pitch_frame, entries):
    """
    Draws annotations on the frame for each object entry.

    Parameters:
        :param pitch_frame: The video frame to annotate.
        :param entries: (list[dict]): List of detection entries (from save_objects).

    Returns:
        pitch_frame: Annotated frame.
    """
    # Listen für beide Teams
    pitch_points_team1, pitch_points_team2, ball_points = get_team_arrays(entries, with_id=True)
    # ensure we only take the first ball point if multiples are detected
    ball_points = ball_points[0:1] if len(ball_points) > 0 else []
    #print(pitch_points_team1, pitch_points_team2)

    if len(pitch_points_team1) == 0 and len(pitch_points_team2) == 0:
        return pitch_frame

    pitch_frame = draw_points_on_pitch(
        config=CONFIG,
        xy=pitch_points_team1,
        face_color=sv.Color.from_hex('00BFFF'),
        edge_color=sv.Color.BLACK,
        radius=16,
        pitch=pitch_frame,
        scale=0.5
    )

    pitch_frame = draw_points_on_pitch(
        config=CONFIG,
        xy=pitch_points_team2,
        face_color=sv.Color.from_hex('FF4500'),
        edge_color=sv.Color.BLACK,
        radius=16,
        pitch=pitch_frame,
        scale=0.5
    )

    pitch_frame = draw_points_on_pitch(
        config=CONFIG,
        xy=ball_points,
        face_color=sv.Color.BLACK,
        edge_color=sv.Color.BLACK,
        radius=10,
        pitch=pitch_frame,
        scale=0.5
    )

    return pitch_frame

def create_voronoi_frame(pitch_frame, entries):
    """
    Draws Voronoi regions on the pitch frame based on team entries.

    Parameters:
        pitch_frame (np.ndarray): The video frame to annotate.
        entries (list[dict]): List of detection entries (from save_objects).

    Returns:
        np.ndarray: Annotated frame with Voronoi regions.
    """
    # Get team points
    pitch_points_team1, pitch_points_team2, _ = get_team_arrays(entries)
    #print("voronoi", pitch_points_team1, pitch_points_team2)

    if len(pitch_points_team1) == 0 or len(pitch_points_team2) == 0:
        return pitch_frame

    # Draw Voronoi regions
    pitch_frame = draw_pitch_voronoi_diagram(
        config=CONFIG,
        pitch=pitch_frame,
        scale=0.5,
        team_1_xy=pitch_points_team1,
        team_2_xy=pitch_points_team2,
        team_1_color=sv.Color.from_hex('00BFFF'),
        team_2_color=sv.Color.from_hex('FF4500')
    )

    return pitch_frame


def get_team_arrays(entries, with_id=False):
    """
    Extracts team lists from the entries.

    Parameters:
        :param entries: List of detection entries.
        :param with_id: True if tracking IDs should be included in the output arrays.

    Returns:
        tuple: Two numpy arrays containing team 1 and team 2 entries.
    """
    team1_points = []
    team2_points = []
    ball_points = []

    for entry in entries:
        if not with_id and entry.get("object_type") == "ball":
            continue

        pitch_pos = np.array(entry.get("pitch_position"), dtype=np.float32) * 100
        tracking_id = entry.get("tracking_id")
        team = entry.get("team")

        if with_id:
            point = [pitch_pos[0], pitch_pos[1], tracking_id]
        else:
            point = [pitch_pos[0], pitch_pos[1]]

        if team == "Team 1":
            team1_points.append(point)
        elif team == "Team 2":
            team2_points.append(point)
        elif entry.get("object_type") == "ball":
            ball_points.append(point)

    # Convert to regular ndarray
    if with_id:
        pitch_points_team1 = np.array(team1_points, dtype=object)
        pitch_points_team2 = np.array(team2_points, dtype=object)
        ball_points = np.array(ball_points, dtype=object)
    else:
        pitch_points_team1 = np.array(team1_points, dtype=np.float32).reshape(-1, 2)
        pitch_points_team2 = np.array(team2_points, dtype=np.float32).reshape(-1, 2)

    return pitch_points_team1, pitch_points_team2, ball_points
