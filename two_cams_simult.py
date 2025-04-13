import cv2

# Öffne zwei Kameras (z. B. Index 0 und 1)
cam1 = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
cam2 = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

if not cam1.isOpened() or not cam2.isOpened():
    print("Eine oder beide Kameras konnten nicht geöffnet werden.")
    exit()

print("Drücke 'q' zum Beenden.")

while True:
    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    if ret1:
        cv2.imshow("Kamera 1", frame1)
    if ret2:
        cv2.imshow("Kamera 2", frame2)

    # Warten auf 'q' zum Beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Alles sauber beenden
cam1.release()
cam2.release()
cv2.destroyAllWindows()