from ultralytics import YOLO
import cv2
class PoseClassifier:
    def __init__(self, lying_ratio_threshold=0.5, standing_ratio_threshold=1.3):
        """
        :param lying_ratio_threshold: Breiter als hoch = liegend
        :param standing_ratio_threshold: Deutlich höher als breit = stehend
        """
        self.lying_ratio_threshold = lying_ratio_threshold
        self.standing_ratio_threshold = standing_ratio_threshold
        self.model = YOLO('models/action.pt')
        self.classnames = list(self.model.names.values())

    def classify_pose(self, bbox):
        """
        :param bbox: (x1, y1, x2, y2)
        :return: "lying", "standing", "sitting"
        """
        x1, y1, x2, y2 = map(int, bbox)
        width = x2 - x1
        height = y2 - y1

        if width == 0 or height == 0:
            return "unknown"

        ratio = height / width

        if ratio < self.lying_ratio_threshold:
            return "lying"
        elif ratio > self.standing_ratio_threshold:
            return "standing"
        else:
            return "sitting"

    def predict_action(self, frame, bbox):
        """
        Predicts the action in the given frame using the YOLO model.

        :param frame: The input image frame (numpy array).
        :return: A list of predicted actions for each detected object.
        """
        x1, y1, x2, y2 = map(int, bbox)
        image = frame[y1:y2, x1:x2]
        #image = cv2.resize(image, (640, 640))
        results = self.model.predict(image, verbose=False)

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                label = self.classnames[cls] if cls < len(self.classnames) else "Unknown"
                return label
            return None
        return None


import math


def compute_real_object_size(object_size_px, image_size_px, view_angle_deg, distance_to_object_m=None):
    """
    Berechnet das Verhältnis r und ggf. die reale Größe des Objekts.

    Parameter:
    - object_size_px: Größe des Objekts im Bild (Pixel)
    - image_size_px: Gesamte Bildgröße entlang der relevanten Achse (Pixel)
    - view_angle_deg: Kamera-Sichtwinkel entlang dieser Achse (Grad)
    - distance_to_object_m: (optional) Abstand zum Objekt in Metern

    Rückgabe:
    - r: Tangens des halben Winkels, unter dem das Objekt erscheint
    - real_size_m: (optional) reale Objektgröße in Metern (wenn Abstand bekannt)
    """

    # Verhältnis des Objekts zur Gesamtbildgröße
    r = object_size_px / image_size_px

    # Umrechnung des Sichtwinkels von Grad in Bogenmaß
    half_angle_rad = math.radians(view_angle_deg / 2)

    # r entspricht nun tan(halber Winkel unter dem das Objekt erscheint)
    r *= math.tan(half_angle_rad)

    # Wenn Abstand bekannt ist, reale Größe berechnen
    real_size_m = None
    if distance_to_object_m is not None:
        real_size_m = 2 * r * distance_to_object_m

    return real_size_m