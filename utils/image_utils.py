import numpy as np
import cv2

def blacken_image(image):
    """
    Converts an image to black by setting all pixel values to zero.

    Args:
        image (numpy.ndarray): The input image array.

    Returns:
        numpy.ndarray: The blackened image array.
    """
    # Your image (merged_frame must be a 720p image)
    height, width = image.shape[:2]

    # To get the area to the right of the line, we extend to the bottom-right and top-right corners
    polygon_right = np.array([
        (1169, 660),
        (799, 151),
        (834, 0),
        (width - 1, 0),
        (width - 1, height - 1)
    ], dtype=np.int32)

    # Create a black mask
    mask = np.zeros((height, width), dtype=np.uint8)

    # Fill the area to the right of the line with white on the mask
    cv2.fillPoly(mask, [polygon_right], 255)

    # Invert the mask to keep left side, or use directly to black out right side
    image[mask == 255] = 0  # Set right-side pixels to black
    return image


def merge_frames(frame_left, frame_right):
    """
    Merges two frames horizontally and applies the blackening effect to the right side.

    Args:
        frame_left (numpy.ndarray): The left frame.
        frame_right (numpy.ndarray): The right frame.

    Returns:
        numpy.ndarray: The merged frame with the right side blackened.
    """
    # Resize just in case (optional safety check)
    frame_left = cv2.resize(frame_left, (1280, 720))
    frame_right = cv2.resize(frame_right, (1280, 720))

    # Merge horizontally
    merged_frame = np.concatenate((frame_left, frame_right), axis=1)

    # Blacken the right side of the merged frame
    return merged_frame
