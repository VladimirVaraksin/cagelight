from ultralytics import YOLO
import cv2
# load the action classification model
action_model = YOLO('models/action.pt')
class_names = list(action_model.names.values())
#print(class_names)

def classify_action(frame, bbox):
    x1, y1, x2, y2 = map(int, bbox)
    # crop the image to the bounding box
    image = frame[y1:y2, x1:x2]
    image = cv2.resize(image, (640, 640)) # Resize to the input size of the model
    # run the action classification model
    results = action_model.predict(image, #conf=0.3,
                                   verbose=False)

    if not results:
        return None

    detections = results[0]
    if not detections.boxes:
        return None

    for box in detections.boxes:
        cls_id = int(box.cls[0])
        label = class_names[cls_id] if cls_id < len(class_names) else "Unknown"
        return label # ['falling', 'lying', 'running', 'sitting', 'standing', 'walking']

    return None
