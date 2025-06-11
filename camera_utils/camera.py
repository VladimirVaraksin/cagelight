import cv2
import os

# --- Kamera-Setup ---
def setup_camera(index=0, width=1280, height=720):
    system = os.name

    if system == "Windows":
        backend = cv2.CAP_DSHOW
    elif system == "Linux":
        backend = cv2.CAP_V4L2
    elif system == "Darwin":
        backend = cv2.CAP_AVFOUNDATION
    else:
        backend = 0  # Default

    cap = cv2.VideoCapture(index, backend)  # Open camera with specified backend
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)  # Set width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  # Set height

    return cap if cap.isOpened() else None


def release_sources(cameras):
    """
    Release all camera streams.
    """
    for cam in cameras:
        cam.release()

def setup_cam_streams(camera_indices, resolution, save_folder):
    """
    Set up multiple video streams from cameras and define video writers.

    Parameters:
    - camera_indices: List of camera indices to open.
    - resolution: Tuple specifying the resolution (width, height).
    - save_folder: Folder where the output videos will be saved.

    Returns:
    - video_streams: List of opened video streams.
    - video_writers: List of VideoWriter objects for each stream.
    """
    video_streams = []
    video_writers = []

    for index in camera_indices:
        # Open the video stream
        video_stream = setup_camera(index, resolution[0], resolution[1])
        if not video_stream.isOpened():
            print(f"Kamera mit Index {index} konnte nicht geöffnet werden.")
            return None, None  # Return None if any camera fails to open

        # Get the FPS, width, and height
        fps = video_stream.get(cv2.CAP_PROP_FPS)
        width = int(video_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the VideoWriter for the current stream
        output_file = os.path.join(save_folder, f'output_video_{index}.mp4')
        out = cv2.VideoWriter(
            output_file,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        # Append the video stream and writer to the lists
        video_streams.append(video_stream)
        video_writers.append(out)

    return video_streams, video_writers

if __name__ == "__main__":
    # Example usage
    camera = setup_camera(0, 1280, 720)
    if camera:
        print("Camera setup successful.")
        for i in range(200):  # Display test frames
            ret, frame = camera.read()
            if not ret:
                print("Failed to grab frame.")
                break
            cv2.imshow("Camera Feed", frame)
    else:
        print("Failed to set up camera.")
    release_sources([camera])