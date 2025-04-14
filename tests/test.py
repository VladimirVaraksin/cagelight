from main import get_cameras_with_resolutions

if __name__ == "__main__":
    for cam in get_cameras_with_resolutions():
        print(f"{cam['name']} ({cam['index']}):")
        for w, h in cam['resolutions']:
            print(f"  - {w}x{h}")