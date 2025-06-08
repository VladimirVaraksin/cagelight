class PoseClassifier:
    def __init__(self, lying_ratio_threshold=0.5, standing_ratio_threshold=1.5):
        """
        :param lying_ratio_threshold: Breiter als hoch = liegend
        :param standing_ratio_threshold: Deutlich höher als breit = stehend
        """
        self.lying_ratio_threshold = lying_ratio_threshold
        self.standing_ratio_threshold = standing_ratio_threshold

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