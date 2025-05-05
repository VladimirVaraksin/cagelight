import cv2
import platform

# --- Kamera-Setup ---
def setup_camera(index=0, width=1280, height=720):
    system = platform.system()

    if system == "Darwin":  # macOS
        backend = cv2.CAP_AVFOUNDATION
    elif system == "Windows":
        backend = cv2.CAP_DSHOW
    elif system == "Linux":
        backend = cv2.CAP_V4L2
    else:
        backend = 0  # Default backend

    cap = cv2.VideoCapture(index, backend)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap if cap.isOpened() else None

def release_sources(cameras):
    """
    Release all camera streams.
    """
    for cam in cameras:
        cam.release()
