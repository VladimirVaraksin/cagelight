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

        # Pixel coordinates of the court corners in the input image
        self.pixel_vertices = np.array([
            [489, 149],  # Top-left corner in image
            [794, 148],  # Top-middle/right
            [1167, 659],  # Bottom-right
            [125, 658]  # Bottom-left
        ], dtype=np.float32)

        # Corresponding real-world coordinates (in meters)
        self.target_vertices = np.array([
            [0, 0],  # Top-left in real world
            [court_length / 2, 0],  # Top-middle
            [court_length / 2, court_width],  # Bottom-middle
            [0, court_width]  # Bottom-left
        ], dtype=np.float32)

        # Compute the perspective transformation matrix
        self.perspective_transformer = cv2.getPerspectiveTransform(
            self.pixel_vertices,
            self.target_vertices
        )

    def transform_point(self, point):
        """
        Transforms a point from pixel coordinates to real-world coordinates.

        Parameters:
        - point: A NumPy array of shape (1, 2), representing the (x, y) pixel coordinates.

        Returns:
        - A NumPy array of shape (1, 2) with the transformed real-world coordinates,
          or None if the point lies outside the defined court polygon.
        """
        # Convert to integer coordinates for point-in-polygon test
        p = (int(point[0]), int(point[1]))

        # Check if the point lies within the defined court polygon
        is_inside = cv2.pointPolygonTest(self.pixel_vertices, p, False) >= 0
        if not is_inside:
            return None  # Return None if point is outside

        # Reshape point to required format for cv2.perspectiveTransform and convert to float32
        reshaped_point = point.reshape(-1, 1, 2).astype(np.float32)

        # Apply the perspective transformation
        transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer)

        # Reshape result back to (1, 2) and return
        return transformed_point.reshape(-1, 2)
