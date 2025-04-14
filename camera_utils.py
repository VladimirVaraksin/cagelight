import AVFoundation
import cv2
from object_detection import model, detect_obj

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