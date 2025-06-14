# this file contains functions for action classification
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf

mp_selfie_segmentation = mp.solutions.selfie_segmentation
segment = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

class PoseClassifier:
    def __init__(self, lying_ratio_threshold=0.5, standing_ratio_threshold=1.2):
        """
        :param lying_ratio_threshold: Ratio below which a person is considered lying.
        :param standing_ratio_threshold: Ratio above which a person is considered standing.
        """
        self.lying_ratio_threshold = lying_ratio_threshold
        self.image_size = (224, 224)
        self.model = tf.keras.models.load_model("models/pose_model.keras")
        self.classnames = ['bending', 'lying', 'sitting', 'standing']
        self.standing_ratio_threshold = standing_ratio_threshold


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

        action = self._predict_action(frame, bbox)

        if action is None:
            return "unknown"

        #print(f"Predicted action: {action}, Ratio: {ratio:.2f}")
        if action == "bending":
            action = "standing"

        if ratio > self.standing_ratio_threshold:
            if action == "lying":
                return "lying"
            else:
                return "standing"
        return action



    def _predict_action(self, frame, bbox):
        """
        Predicts the action (pose) for a cropped person region using a silhouette and trained model.
        """
        x1, y1, x2, y2 = bbox
        image = frame[y1:y2, x1:x2]
        image = cv2.resize(image, self.image_size)

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get segmentation mask
        results = segment.process(img_rgb)
        mask = results.segmentation_mask

        # Create silhouette: person = black, background = white
        silhouette = np.ones_like(image, dtype=np.uint8) * 255  # white background
        silhouette[mask > 0.5] = (0, 0, 0)  # black person

        # Resize and preprocess for the model
        silhouette_resized = cv2.resize(silhouette, self.image_size)
        silhouette_array = silhouette_resized.astype(np.float32) / 255.0  # normalize
        input_tensor = np.expand_dims(silhouette_array, axis=0)  # add batch dim

        # cv2.imshow("Silhouette", silhouette_resized) # Debugging line to show the silhouette
        # cv2.waitKey(0)
        threshold = 0.45  # adjust as needed

        predictions = self.model.predict(input_tensor)
        #print(predictions)
        confidence = np.max(predictions[0])
        predicted_index = np.argmax(predictions[0])

        if confidence < threshold:
            return None

        predicted_label = self.classnames[predicted_index]
        return predicted_label





    @staticmethod
    def _sanitize_bbox(bbox):
        """
        Ensures bounding box values are integers.
        """
        return tuple(map(int, bbox))