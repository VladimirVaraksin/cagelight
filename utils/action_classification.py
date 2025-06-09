# this file contains functions for action classification
from ultralytics import YOLO
import cv2

class PoseClassifier:
    def __init__(self, lying_ratio_threshold=0.5, standing_ratio_threshold=1.3):
        """
        :param lying_ratio_threshold: Ratio below which a person is considered lying.
        :param standing_ratio_threshold: Ratio above which a person is considered standing.
        """
        self.lying_ratio_threshold = lying_ratio_threshold
        self.standing_ratio_threshold = standing_ratio_threshold
        self.model = YOLO('models/best.pt')
        self.classnames = self.model.names

    def classify_pose(self, frame, bbox):
        """
        Classify the pose based on bounding box aspect ratio and model prediction.
        :param frame: Full frame (numpy array)
        :param bbox: Tuple (x1, y1, x2, y2)
        :return: "lying", "standing", "sitting", or "unknown"
        """
        x1, y1, x2, y2 = self._sanitize_bbox(bbox)
        width, height = x2 - x1, y2 - y1

        if width == 0 or height == 0:
            return "unknown"

        ratio = height / width

        if ratio < self.lying_ratio_threshold:
            return "lying"
        elif ratio > self.standing_ratio_threshold:
            action = self._predict_action(frame, (x1, y1, x2, y2))
            if not action:
                # action = self._predict_action(frame, (x1, y1, x2, y2), rotate=True)
                # if action == "fall":
                    return "lying"
            return "standing"
        else:
            return "sitting"

    def _predict_action(self, frame, bbox, rotate=False):
        """
        Predicts the action for a cropped person region.
        :param frame: Full frame (numpy array)
        :param bbox: Tuple (x1, y1, x2, y2)
        :param rotate: Whether to rotate the cropped image
        :return: Predicted label or None
        """
        x1, y1, x2, y2 = bbox
        image = frame[y1:y2, x1:x2]
        if rotate:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.resize(image, (640, 640))

        results = self.model.predict(image, verbose=False, conf = 0.25)
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                #print(self.classnames.get(cls_id, "Unknown"), bbox, box.conf[0])
                return self.classnames.get(cls_id, "Unknown")
        return None

    @staticmethod
    def _sanitize_bbox(bbox):
        """
        Ensures bounding box values are integers.
        """
        return tuple(map(int, bbox))

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

    # r entspricht nun tan (halber Winkel unter dem das Objekt erscheint)
    r *= math.tan(half_angle_rad)

    # Wenn Abstand bekannt ist, reale Größe berechnen
    real_size_m = None
    if distance_to_object_m is not None:
        real_size_m = 2 * r * distance_to_object_m

    return real_size_m