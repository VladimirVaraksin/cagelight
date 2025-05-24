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