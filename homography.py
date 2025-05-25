# This script performs homography transformation to map detected players from a video frame onto a 2D soccer pitch.

import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO

from utils import ViewTransformer, SoccerPitchConfiguration
from draw import draw_pitch, draw_points_on_pitch

# Load the YOLO models for pitch keypoints and player detection
PITCH_MODEL = YOLO('yolo-Weights/pitch_keypoints.pt')
PLAYER_DETECTION_MODEL = YOLO('yolo-Weights/player_ball.pt')

# Initialize standard pitch dimensions and vertices
CONFIG = SoccerPitchConfiguration()
# Convert pitch vertices to a numpy array for homography transformation
pitch_reference_points = np.array(CONFIG.vertices)
# Open the video file videos/test.mp4
cap = cv2.VideoCapture('videos/test.mp4')


while True:
    # Read a frame from the video
    ret, frame = cap.read()
    if not ret:
        print("End of video or error reading frame.")
        break
    # Draw the pitch on the frame
    annotated_frame = draw_pitch(CONFIG)
    # Run keypoint model
    results = PITCH_MODEL.predict(frame, verbose=False)
    # Extract the coordinates of keypoints from the results
    frame_reference_points = np.array(results[0].keypoints.xy[0])

    # Apply the mask to filter out undetected points
    non_zero_mask = ~np.all(frame_reference_points == 0, axis=1)
    frame_reference_points = frame_reference_points[non_zero_mask] #remove undetected points from frame_reference_points
    pitch_reference_points = pitch_reference_points[non_zero_mask] #remove respective unwanted points from pitch_reference_points

    if len(frame_reference_points) >= 4:
        # Initialize the ViewTransformer with the source and target points
        transformer = ViewTransformer(
            source=frame_reference_points,
            target=pitch_reference_points
        )
    else:
        # Less than 4 keypoints detected, skip homography transformation
        print("Insufficient keypoints in frame, skipping...")
        continue

    # Run player (class 2) and goalkeeper (class 1) detection model
    players_detections = PLAYER_DETECTION_MODEL.track(source=frame, stream=True
                                                      , verbose=False, persist=True,
                                                      tracker='bytetrack.yaml', classes=[1, 2]
                                                      )

    for detections in players_detections:
        #print(detections.boxes)
        # Convert detections to Supervision format
        detected_players = sv.Detections.from_ultralytics(detections)

        # Get the bottom center coordinates of the detected players: x = (x_min + x_max) / 2; y = y_max;
        players_xy = detected_players.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)
        # Compute homography
        pitch_players_xy = transformer.transform_points(points=players_xy)
        # Draw the players
        annotated_frame = draw_points_on_pitch(
            config=CONFIG,
            xy=pitch_players_xy,
            face_color=sv.Color.from_hex('00BFFF'),
            edge_color=sv.Color.BLACK,
            radius=16,
            pitch=annotated_frame)


    # Optional saving of the annotated frame for debugging
    # cv2.imwrite("output/pitch.jpg", annotated_frame)

    # Show the video
    cv2.imshow('Frame2', frame)
    # Show the annotated frame with pitch and players
    cv2.imshow('Frame', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Exit the loop if 'q' is pressed
        break
    # Reset the pitch reference points for the next frame
    pitch_reference_points = np.array(CONFIG.vertices)


cap.release()
cv2.destroyAllWindows()


#frame_ball_xy = ball_detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)
#pitch_ball_xy = transformer.transform_points(points=frame_ball_xy)