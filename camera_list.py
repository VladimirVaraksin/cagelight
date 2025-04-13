import AVFoundation
import cv2

def list_video_devices():
    devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)
    device_list = []
    print("Verfügbare Kameras:")
    for idx, device in enumerate(devices):
        print(f"[{idx}] {device.localizedName()}")
        device_list.append(device)
    return device_list

def list_camera_resolutions():
    devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)

    for index, device in enumerate(devices):
        print(f"[{index}] Name: {device.localizedName()}")
        formats = device.formats()
        resolutions = set()
        for fmt in formats:
            desc = fmt.formatDescription()
            dimensions = AVFoundation.CMVideoFormatDescriptionGetDimensions(desc)
            resolution = f"{dimensions.width}x{dimensions.height}"
            resolutions.add(resolution)
        for res in sorted(resolutions, key=lambda x: int(x.split('x')[0])):
            print(f"  - {res}")
    return devices

def choose_device(devices):
    while True:
        try:
            choice = int(input("Welche Kamera möchtest du verwenden? Gib die Nummer ein: "))
            if 0 <= choice < len(devices):
                return choice
        except ValueError:
            pass
        print("Ungültige Eingabe, bitte nochmal.")

def open_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print("Kamera konnte nicht geöffnet werden.")
        return
    print("Drücke 'q' zum Beenden.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Kamera-Vorschau", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def main():
    devices = list_video_devices()
    selected_index = choose_device(devices)
    print(f"Starte Kamera: {devices[selected_index].localizedName()}")
    open_camera(selected_index)

if __name__ == "__main__":
    main()
