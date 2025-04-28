import threading
import cv2
from object_detection import annotate_objects, PLAYER_DETECTION_MODEL
from camera_utils import setup_camera
import numpy as np

def run_tracker_in_thread(camera, cam_name, cam_disp):
    while True:
        ret, frame = camera.read()
        if ret:
            results = PLAYER_DETECTION_MODEL.track(source=frame, stream=True,
                                                    verbose=False, persist=True, tracker='bytetrack.yaml')
            #  annotate the frame
            annotate_objects(results, frame)
            cam_disp[cam_name] = frame.copy()  # Store the latest frame for main thread to display
            #print(results)

        if cam_disp.get('exit', False):
            break

    camera.release()

def run_multiple_cams(cam_configs):
    caps = []
    cam_disp = {}

    # Setup cameras
    for cfg in cam_configs:
        cap = setup_camera(cfg['index'], cfg['width'], cfg['height'])
        if cap:
            caps.append((cap, cfg['name']))

    if not caps:
        print("Keine Kameras geöffnet.")
        return

    # Pre-warm the detection model
    dummy_frame = np.zeros((640, 480, 3), dtype=np.uint8)
    PLAYER_DETECTION_MODEL.track(source=dummy_frame, verbose=False, persist=True, tracker='bytetrack.yaml')

    # Start tracking threads
    tracker_threads = []
    for cap, cam_name in caps:
        l_thread = threading.Thread(target=run_tracker_in_thread, args=(cap, cam_name, cam_disp), daemon=True)
        tracker_threads.append(l_thread)
        l_thread.start()

    try:
        while True:
            for _, cam_name in caps:
                if cam_name in cam_disp:
                    cv2.imshow(cam_name, cam_disp[cam_name])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cam_disp['exit'] = True
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
        cam_disp['exit'] = True

    finally:
        for thread in tracker_threads:
            thread.join()
        cv2.destroyAllWindows()




if __name__ == '__main__':
    #configs = [{'index': 0, 'name': 'Phone Camera', 'width': 1920, 'height': 1080}, {'index': 1, 'name': 'Webcam', 'width': 1920, 'height': 1080}]
    configs = [{'index': 'videos/test.mp4', 'name': 'video1', 'width': 1920, 'height': 1080}, {'index': 'videos/test.mp4', 'name': 'video2', 'width': 1920, 'height': 1080}]
    run_multiple_cams(configs)