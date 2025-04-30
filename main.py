from gui import start_gui
from camera_utils import get_cameras_with_resolutions
from multithreading_cameras import run_multiple_cams

def main():
     camera_data = get_cameras_with_resolutions()
     configs = start_gui(camera_data)
     # configs for phone camera
     # configs = [{'index': 0, 'name': 'Phone Camera', 'width': 1920, 'height': 1080}]
     run_multiple_cams(configs)

if __name__ == "__main__":
    main()