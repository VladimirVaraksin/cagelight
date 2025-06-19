import cv2

clicked_points = []
path = '../images/1.jpg'  # Path to the image file
frame = cv2.imread(path)  # Load the image where you want to click points

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"Clicked: ({x}, {y})")
        if len(clicked_points) == 4:
            print(" All 4 points clicked successfully!")

            print("video_points = np.array([")
            for pt in clicked_points:
                print(f"    [{pt[0]}, {pt[1]}],")
            print("], dtype=np.float32)")
            cv2.destroyAllWindows()

# Show image and capture clicks
window_name = 'Click 4 Points: Top-Left, Top-Right, Bottom-Right, Bottom-Left'
cv2.imshow(window_name, frame) # show the image
cv2.setMouseCallback(window_name, click_event) # set mouse callback to capture clicks

cv2.waitKey(0)
cv2.destroyAllWindows()


"""
# Example output 1st camera:
video_points = np.array([
    [489, 149],
    [794, 148],
    [1167, 659],
    [125, 658],
], dtype=np.float32)
"""

"""
(x, y)
Clicked: (374, 313)
Clicked: (336, 265)
Clicked: (433, 227)
Clicked: (412, 182)
"""


"""
#Merged frames points.
#camera 1

#camera 2
video_points = np.array([
    [1770, 152],
    [2075, 150],
    [2447, 660],
    [1408, 658],
], dtype=np.float32)
"""

