import cv2

def annotate_frame(frame, entries):
    """
    Draws annotations on the frame for each object entry.

    Parameters:
        frame (np.ndarray): The video frame to annotate.
        entries (list[dict]): List of detection entries (from save_objects).

    Returns:
        np.ndarray: Annotated frame.
    """

    for list in entries:
        match_time = list[0]["timestamp"]
        for entry in list:
            # Denormalize bounding box coordinates to pixel values
            bbox = entry["bbox_xyxy"]
            x1 = int(bbox[0] * frame.shape[1])
            y1 = int(bbox[1] * frame.shape[0])
            x2 = int(bbox[2] * frame.shape[1])
            y2 = int(bbox[3] * frame.shape[0])

            # Choose color based on object type and team
            if entry["object_type"] == "ball":
                color = (0, 255, 255)  # Yellow
            elif entry["team"] == "Team 1":
                color = (255, 255, 255)    # White
            elif entry["team"] == "Team 2":
                color = (0, 0, 0)    # Black
            else:
                color = (200, 200, 200)  # Gray for unknown

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Prepare annotation label
            label_text = f'{entry["object_type"]} #{entry["tracking_id"]} ({entry["team"]}) {int(entry["confidence"] * 100)}%'

            # Draw label text above the box
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, color, 1, cv2.LINE_AA)

        # Optionally: draw the latest timestamp (bottom-left corner)
        cv2.putText(frame, f'Time: {match_time}', (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame
