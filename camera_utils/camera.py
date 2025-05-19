import cv2
# --- Kamera-Setup ---
def setup_camera(index=0, width=1280, height=720):
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap if cap.isOpened() else None

def release_sources(cameras):
    """
    Release all camera streams.
    """
    for cam in cameras:
        cam.release()
