from ultralytics import YOLO
import cv2
from camera_list import list_camera_resolutions, choose_device


# --- Model & Klassen ---
model = YOLO("yolo-Weights/yolov8n.pt")

classNames = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
    "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
    "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
    "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
    "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
    "teddy bear", "hair drier", "toothbrush", "ball"
]


# --- Detection ---
def detect_obj(results, img):
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = round(float(box.conf[0]), 2)
            cls = int(box.cls[0])
            label = classNames[cls] if cls < len(classNames) else "Unknown"

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.putText(img, f'{label} {confidence}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)


# --- Kamera Setup ---
def setup_camera(index, width=1920, height=1080):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if not cap.isOpened():
        print(f"Kamera {index} konnte nicht geöffnet werden.")
        return None
    return cap


# --- Modus: Einzelkamera ---
def run_single_camera(index, name="Kamera"):
    cap = setup_camera(index)
    if not cap:
        return

    while True:
        success, img = cap.read()
        if not success:
            break
        results = model(img, stream=True)
        detect_obj(results, img)
        cv2.imshow(name, img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# --- Modus: Zwei Kameras ---
def run_multiple_cams(index1, index2):
    cap1 = setup_camera(index1)
    cap2 = setup_camera(index2)

    if not cap1 or not cap2:
        return

    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if ret1:
            results1 = model(frame1, stream=True)
            detect_obj(results1, frame1)
            cv2.imshow("Kamera 1", frame1)
        if ret2:
            results2 = model(frame2, stream=True)
            detect_obj(results2, frame2)
            cv2.imshow("Kamera 2", frame2)

        if cv2.waitKey(1) == ord('q'):
            break

    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()


# --- Hauptprogramm ---
def main():
    devices = list_camera_resolutions()
    print("\nMehrere Kameras auswählen? (y/n): ", end="")
    multi = input().strip().lower() == 'y'

    if multi:
        print("Wähle zwei Kameras durch Komma getrennt (z. B. 0,1): ", end="")
        selection = input()
        try:
            index1, index2 = map(int, selection.split(','))
            run_multiple_cams(index1, index2)
        except:
            print("Ungültige Eingabe.")
    else:
        selected_index = choose_device(devices)
        run_single_camera(selected_index, name=f"Kamera {selected_index}")


if __name__ == "__main__":
    main()
