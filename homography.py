import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO

from utils import ViewTransformer, SoccerPitchConfiguration
from draw import draw_pitch, draw_points_on_pitch

PITCH_MODEL = YOLO('yolo-Weights/pitch_keypoints.pt')
PLAYER_DETECTION_MODEL = YOLO('yolo-Weights/player_ball.pt')

# Initialize pitch config and video
CONFIG = SoccerPitchConfiguration()
pitch_reference_points = np.array(CONFIG.vertices)
cap = cv2.VideoCapture('videos/test.mp4')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run keypoint model
    results = PITCH_MODEL.predict(frame, verbose=False)
    frame_reference_points = np.array(results[0].keypoints.xy[0])

    non_zero_mask = ~np.all(frame_reference_points == 0, axis=1)

    # Apply the mask to filter out undetected points
    frame_reference_points = frame_reference_points[non_zero_mask]
    pitch_reference_points = pitch_reference_points[non_zero_mask]

    players_detections = PLAYER_DETECTION_MODEL.track(source=frame, stream=True
                                           , verbose=False, persist=True,
                                           tracker='bytetrack.yaml'   , classes=[1, 2]
                                           )
    for detections in players_detections:

        detected_players = sv.Detections.from_ultralytics(detections)

        if len(frame_reference_points) >= 4:
            # Compute homography
            transformer = ViewTransformer(
                source=frame_reference_points,
                target=pitch_reference_points
            )

            players_xy = detected_players.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)
            pitch_players_xy = transformer.transform_points(points=players_xy)

            annotated_frame = draw_pitch(CONFIG)
            annotated_frame = draw_points_on_pitch(
                config=CONFIG,
                xy=pitch_players_xy,
                face_color=sv.Color.from_hex('00BFFF'),
                edge_color=sv.Color.BLACK,
                radius=16,
                pitch=annotated_frame)

            cv2.imshow('Frame', annotated_frame)
            #cv2.imwrite("output/pitch.jpg", annotated_frame)
        else:
            print("Insufficient keypoints in frame, skipping...")
    cv2.imshow('Frame2', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    pitch_reference_points = np.array(CONFIG.vertices)


cap.release()
cv2.destroyAllWindows()


#frame_ball_xy = ball_detections.get_anchors_coordinates(sv.Position.BOTTOM_CENTER)
#pitch_ball_xy = transformer.transform_points(points=frame_ball_xy)