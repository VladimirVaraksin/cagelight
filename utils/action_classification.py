from ultralytics import YOLO

# Modell laden
action_model = YOLO('models/action.pt')
class_names = list(action_model.names.values())

# Mappings für bessere Wartbarkeit
LABEL_MAP = {
    "running": "running",
    "person_running": "running",
    "Running - v2 2023-09-23 12-33am": "running",
    "Person_Standing": "standing",
    "Person_Walking": "walking",
    "jump": "jumping"
}

def classify_action(frame, bbox):
    x1, y1, x2, y2 = map(int, bbox)
    image = frame[y1:y2, x1:x2]
    results = action_model.predict(image, conf=0.3, verbose=False)

    if not results:
        return None

    detections = results[0]
    if not detections.boxes:
        return None

    for box in detections.boxes:
        cls_id = int(box.cls[0])
        label = class_names[cls_id] if cls_id < len(class_names) else "Unknown"
        return LABEL_MAP.get(label, "unknown") # running, standing, walking, jumping, or unknown

    return None
