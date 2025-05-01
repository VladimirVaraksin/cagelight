import cv2
import platform
import pyudev
import AVFoundation # macOS only
#from pygrabber.dshow_graph import FilterGraph #windows

def test_resolutions_for_camera(cap, resolutions):
    supported_res = []
    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if (actual_width, actual_height) == (width, height):
            supported_res.append((width, height))
    return supported_res


def get_cameras_with_resolutions(max_tested_devices=2):
    common_resolutions = [
        (1920, 1080), (1280, 720)
        #, (1024, 768),
        #(800, 600), (640, 480), (320, 240)
    ]

    camera_data = []
    current_platform = platform.system()

    if current_platform == "Linux":
        # Linux: Use pyudev to get video devices
        context = pyudev.Context()
        video_devices = [device.device_node for device in context.list_devices(subsystem='video4linux')]

        for index, dev in enumerate(video_devices[:max_tested_devices]):
            cap = cv2.VideoCapture(dev)
            if not cap.isOpened():
                continue

            supported_res = test_resolutions_for_camera(cap, common_resolutions)
            cap.release()

            if supported_res:
                camera_data.append({
                    'index': index,  # Add the index of the camera
                    'name': dev,
                    'resolutions': supported_res
                })

    elif current_platform == "Windows":
        from pygrabber.dshow_graph import FilterGraph
        # Windows: Use FilterGraph to get camera name and OpenCV to test resolutions
        devices = FilterGraph().get_input_devices()

        for device_index, device_name in enumerate(devices[:max_tested_devices]):
            cap = cv2.VideoCapture(device_name)
            if not cap.isOpened():
                continue

            supported_res = test_resolutions_for_camera(cap, common_resolutions)
            cap.release()

            if supported_res:
                camera_data.append({
                    'index': device_index,  # Add the index of the camera
                    'name': device_name,
                    'resolutions': supported_res
                })
    elif current_platform == "Darwin":  # macOS
        # macOS: Use AVFoundation via pyobjc to list cameras and resolutions
        devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)
        for index, device in enumerate(devices):
            name = device.localizedName()
            formats = device.formats()
            resolutions = set()

            for fmt in formats:
                desc = fmt.formatDescription()
                dimensions = AVFoundation.CMVideoFormatDescriptionGetDimensions(desc)
                resolution = (dimensions.width, dimensions.height)
                resolutions.add(resolution)

            # Sortiere nach Breite (aufsteigend)
            sorted_res = sorted(list(resolutions), key=lambda r: r[0])

            camera_data.append({
                'index': index,
                'name': name,
                'resolutions': sorted_res
            })

    return camera_data

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

if __name__ == "__main__":
    print(get_cameras_with_resolutions())