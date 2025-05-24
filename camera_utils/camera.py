import cv2
import platform

def check_resolutions_for_camera(cap, resolutions):
    """
    Try to set each resolution and check if the camera accepts it.
    """
    supported_res = [] # List to store supported resolutions
    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) # Set width
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) # Set height

        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # Get actual width
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # Get actual height

        if (actual_width, actual_height) == (width, height): # Check if the set resolution matches the actual resolution
            supported_res.append((width, height)) # Append supported resolution to the list
    return supported_res

def get_cameras_with_resolutions(max_tested_devices=4, override_os=None):
    """
    Detect cameras and test common resolutions based on OS.
    """
    common_resolutions = [(1920, 1080), (1280, 720)] # Common resolutions to test
    camera_data = [] # List to store camera data
    system = override_os if override_os else platform.system() # Get the current operating system

    if system == "Windows": # Windows
        try:
            from pygrabber.dshow_graph import FilterGraph # Import FilterGraph for camera detection
            devices = FilterGraph().get_input_devices() # Get input devices
        except ImportError:
            print(" pygrabber not installed. Run: pip install pygrabber") # Check if pygrabber is installed
            return []

        for index, name in enumerate(devices[:max_tested_devices]): # Iterate through devices
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) # Open camera using DirectShow
            if not cap.isOpened(): # Check if camera is opened successfully
                continue

            supported = check_resolutions_for_camera(cap, common_resolutions) # Check supported resolutions
            cap.release() # Release camera

            if supported: # If supported resolutions are found
                camera_data.append({ #build camera data
                    'index': index,
                    'name': name,
                    'resolutions': supported
                })

    elif system == "Linux": # Linux
        try:
            import pyudev # Import pyudev for camera detection
        except ImportError:
            print(" pyudev not installed. Run: pip install pyudev") # Check if pyudev is installed
            return []

        context = pyudev.Context()
        devices = [d.device_node for d in context.list_devices(subsystem='video4linux')] # List video devices

        for index, dev in enumerate(devices[:max_tested_devices]): # Iterate through devices
            cap = cv2.VideoCapture(dev) # Open camera
            if not cap.isOpened():
                continue # Check if camera is opened successfully

            supported = check_resolutions_for_camera(cap, common_resolutions) # Check supported resolutions
            cap.release() # Release camera

            if supported: # If supported resolutions are found
                camera_data.append({ #build camera data
                    'index': index, # Add the index of the camera
                    'name': dev, # Use device node as name
                    'resolutions': supported # Add supported resolutions
                }) # append to camera data

    elif system == "Darwin":  # macOS
        try:
            import AVFoundation # Import AVFoundation for camera detection
        except ImportError:
            print(" AVFoundation (macOS) not installed.") # Check if AVFoundation is installed
            return []

        devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)
        for index, dev in enumerate(devices): # Iterate through devices
            name = dev.localizedName() # Get camera name
            formats = dev.formats() # Get formats
            resolutions = set() # Set to store unique resolutions

            for fmt in formats:
                desc = fmt.formatDescription() # Get format description
                dims = AVFoundation.CMVideoFormatDescriptionGetDimensions(desc) # Get dimensions
                resolution = (dims.width, dims.height)
                if resolution in common_resolutions:
                    resolutions.add(resolution)

            sorted_res = sorted(resolutions, key=lambda r: r[0]) # Sort resolutions by width
            camera_data.append({ #build camera data
                'index': index, # Add the index of the camera
                'name': name,
                'resolutions': sorted_res # Add supported resolutions
            })

    else:
        print(f" Unsupported OS: {system}") # Unsupported OS

    return camera_data

def setup_camera(index=0, width=1280, height=720, override_os=None):
    """
    Initialize camera with platform-specific backend and resolution.
    """
    system = override_os if override_os else platform.system() # Get the current operating system

    if system == "Windows":
        backend = cv2.CAP_DSHOW
    elif system == "Linux":
        backend = cv2.CAP_V4L2
    elif system == "Darwin":
        backend = cv2.CAP_AVFOUNDATION
    else:
        backend = 0  # Default

    cap = cv2.VideoCapture(index, backend) # Open camera with specified backend
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) # Set width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) # Set height

    return cap if cap.isOpened() else None

def release_cameras(cameras):
    """
    Release a list of camera objects.
    """
    for l_cam in cameras:
        l_cam.release()

if __name__ == "__main__":
    print("🎥 Searching for cameras...\n")
    cams = get_cameras_with_resolutions() # Get cameras with resolutions
    for cam in cams:
        print(f"📸 Camera {cam['index']}: {cam['name']}") # Print camera name
        for res in cam['resolutions']:
            print(f"   - {res[0]}x{res[1]}") # Print supported resolutions
