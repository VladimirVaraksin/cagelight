import cv2
from object_detection import annotate_objects, PLAYER_DETECTION_MODEL
from camera_utils import setup_camera

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
                #results = PLAYER_DETECTION_MODEL(frame, stream=True)
                results = PLAYER_DETECTION_MODEL.track(source=frame, stream=True,
                                                       verbose=False, persist=True, tracker='bytetrack.yaml'#, classes=[0, 1, 2]
                )
                #results = PLAYER_DETECTION_MODEL.predict(frame, verbose=False)
                annotate_objects(results, frame)
                cv2.imshow(name, frame)
        if cv2.waitKey(1) == ord('q'):
            break
    for cap, _ in caps:
        cap.release()
    cv2.destroyAllWindows()

#Test für Setup Camera
def main():
    cap = setup_camera(index=0, width=1280, height=720)
    if not cap:
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        cv2.imshow("Live Camera", frame)

        # q drücken zum Beenden
        if cv2.waitKey(1) == ord('q'):
            print("q gedrückt, beenden...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()