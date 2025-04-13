from ultralytics import YOLO
import cv2
import math
from camera_list import list_camera_resolutions, choose_device

def select_onecam():
    devices = list_camera_resolutions()
    selected_index = choose_device(devices)
    # start webcam
    cap = cv2.VideoCapture(selected_index)  # -> index of the first camera
    cap.set(3, 1920)  # resolution
    cap.set(4, 1080)
    return cap



# model
model = YOLO("yolo-Weights/yolov8x.pt")

# object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
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

def detect_obj(results, img):
    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

            # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # confidence
            confidence = math.ceil((box.conf[0] * 100)) / 100
            print("Confidence --->", confidence)

            # class name
            cls = int(box.cls[0])

            print("Class name -->", classNames[cls])

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            color = (255, 0, 0)
            thickness = 2

            cv2.putText(img, classNames[cls], org, font, font_scale, color, thickness)


def run_single_camera(cap, name):
    while True:
        success, img = cap.read()
        results = model(img, stream=True)

        detect_obj(results, img)

        if success:
            cv2.imshow(name, img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def run_multiple_cams(cam1, cam2):
    while True:
        ret1, frame1 = cam1.read()
        ret2, frame2 = cam2.read()

        if ret1:
            results = model(frame1, stream=True)
            detect_obj(results, frame1)
            cv2.imshow("Kamera 1", frame1)
        if ret2:
            results = model(frame2, stream=True)
            detect_obj(results, frame2)
            cv2.imshow("Kamera 2", frame2)

        # Warten auf 'q' zum Beenden
        if cv2.waitKey(1) == ord('q'):
            break

def main():
    cam1 = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    cam2 = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

    if not cam1.isOpened() or not cam2.isOpened():
        print("Eine oder beide Kameras konnten nicht geöffnet werden.")
        exit()

    print("Drücke 'q' zum Beenden.")
    #multiple
    #run_multiple_cams(cam1, cam2)

    #single
    #run_single_camera(select_onecam(), 'Kamera1')

if __name__ == "__main__":
    main()
