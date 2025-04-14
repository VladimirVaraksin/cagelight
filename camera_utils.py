import AVFoundation
import cv2
from object_detection import model, detect_obj



#macOS solution
#"""
def get_cameras_with_resolutions():
    devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)
    camera_data = []

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
#"""
#Platform independent solution
"""
def get_cameras_with_resolutions(max_tested_devices=5):
    common_resolutions = [
        (1920, 1080), (1280, 720), (1024, 768),
        (800, 600), (640, 480), (320, 240)
    ]

    camera_data = []

    for index in range(max_tested_devices):

            cap = cv2.VideoCapture(index)

            # If the camera couldn't be opened, it will raise an exception
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
"""

# --- Kamera-Setup ---
def setup_camera(index, width, height):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap if cap.isOpened() else None


# --- Mehrere Kameras (eine oder mehrere) ---
def run_multiple_cams(cam_configs):
    caps = []
    for cfg in cam_configs:
        cap = setup_camera(cfg['index'], cfg['width'], cfg['height'])
        if cap:
            caps.append((cap, f"{cfg['name']}"))

    if not caps:
        print("Keine Kameras geöffnet.")
        return

    while True:
        for cap, name in caps:
            ret, frame = cap.read()
            if ret:
                results = model(frame, stream=True)
                detect_obj(results, frame)
                cv2.imshow(name, frame)
        if cv2.waitKey(1) == ord('q'):
            break

    for cap, _ in caps:
        cap.release()
    cv2.destroyAllWindows()