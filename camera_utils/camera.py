import cv2
import platform

#Platform independent solution
#"""
def get_cameras_with_resolutions(max_tested_devices=2):
    common_resolutions = [
        (1920, 1080), (1280, 720), (1024, 768),
        (800, 600), (640, 480), (320, 240)
    ]

    camera_data = []

    for index in range(max_tested_devices):

            cap = cv2.VideoCapture(index)


            if not cap.isOpened():
                print(f"Camera at index {index} could not be opened.")
                return camera_data



            name = f"Camera {index}"
            supported_res = []

            for width, height in common_resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if (actual_width, actual_height) == (width, height):
                    supported_res.append((width, height))

            cap.release()

            if supported_res:
                camera_data.append({
                    'index': index,
                    'name': name,
                    'resolutions': supported_res
                })
    return camera_data
#"""

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