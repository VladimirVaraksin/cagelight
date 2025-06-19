import numpy as np
import cv2


class ViewTransformer:
    """
    A class to transform image coordinates (pixel) to real-world coordinates (meters)
    using perspective transformation, based on known court dimensions and corner mappings.
    """

    def __init__(self):
        """
        Initializes the ViewTransformer by defining real-world dimensions, pixel coordinates,
        and computing the perspective transformation matrix.
        """
        # Real-world dimensions of the court in meters
        court_width = 13.0  # Width of the court (meters)
        court_length = 20.0  # Length of the court (meters)

        #Pixel coordinates of the court corners in the input image
        self.pixel_vertices = np.array([
            [490, 150],
            [822, 149],
            [1266, 658],
            [126, 659],
        ], dtype=np.float32)
        # self.pixel_vertices = np.array([
        #     [244, 674],
        #     [1050, 675],
        #     [1067, 1180],
        #     [0, 1204],
        # ], dtype=np.float32)

        # Corresponding real-world coordinates (in meters) for camera 1
        self.target_vertices = np.array([
            [0, 0],  # Top-left in the real world
            [court_length / 2 + 1, 0],  # Top-middle
            [court_length / 2 + 1, court_width],  # Bottom-middle
            [0, court_width]  # Bottom-left
        ], dtype=np.float32)
        # self.target_vertices = np.array([
        #     [0, 0],  # Top-left in the real world
        #     [10, 0],  # Top-middle
        #     [5, 11],  # Bottom-middle
        #     [0.5, 11]  # Bottom-left
        # ], dtype=np.float32)

        # Corresponding real-world coordinates (in meters) for camera 2
        self.target_vertices_2 = np.array([
            [court_length, court_width],  # Top-left in the real world
            [court_length / 2 - 1, court_width],  # Top-middle
            [court_length / 2 - 1, 0],  # Bottom-middle
            [court_length, 0]  # Bottom-left
        ], dtype=np.float32)

        # Compute the perspective transformation matrix
        self.perspective_transformer = cv2.getPerspectiveTransform(
            self.pixel_vertices,
            self.target_vertices
        )

        self.perspective_transformer_2 = cv2.getPerspectiveTransform(
            self.pixel_vertices,
            self.target_vertices_2
        )

    def transform_point(self, point, camera_id=0):
        """
        Transforms a point from pixel coordinates to real-world coordinates.

        Parameters:
        - point: A NumPy array of shape (1, 2), representing the (x, y) pixel coordinates.

        Returns:
        - A NumPy array of the shape (1, 2) with the transformed real-world coordinates,
          or None if the point lies outside the defined court polygon.
        """
        # Convert to integer coordinates for point-in-polygon test
        p = (int(point[0]), int(point[1]))
        # Reshape point to a required format for cv2.perspectiveTransform and convert to float32
        reshaped_point = point.reshape(-1, 1, 2).astype(np.float32)
        is_inside = cv2.pointPolygonTest(self.pixel_vertices, p, False) >= 0
        # Check if the point lies within the defined court polygon
        if is_inside:
            if camera_id == 0:
                transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer)
            else:
                transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer_2)
        else:
            return None

        return transformed_point.reshape(-1, 2)
