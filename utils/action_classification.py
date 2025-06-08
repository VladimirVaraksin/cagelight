# this file contains functions for action classification based on bounding box coordinates
def classify_pose(x1, y1, x2, y2):
    width = x2 - x1
    height = y2 - y1
    aspect_ratio = height / width  # Verhältnis Höhe zu Breite

    if aspect_ratio < 0.5:
        return "lying"
    elif aspect_ratio < 1.5:
        return "sitting"
    else:
        return "standing"
