from gui import start_gui
from camera_utils import get_cameras_with_resolutions
from live_webcam_analysis import run_multiple_cams

def main():
     camera_data = get_cameras_with_resolutions()
     configs = start_gui(camera_data)
     # Optional: Hardcoded example for testing
     # configs = [{'index': 0, 'name': 'Camera_0', 'width': 1920, 'height': 1080}]
     run_multiple_cams(configs)

if __name__ == "__main__":
    main()