from scipy.spatial import KDTree
from math import hypot
from collections import defaultdict

def parse_time(ts):
    """Convert HH:MM:SS.s to seconds."""
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def merge_and_clean_entries_kdtree(camera1_entries, camera2_entries, distance_threshold=0.5, time_threshold=0.1):
    combined = camera1_entries + camera2_entries
    cleaned = []
    id_counter = 1

    # Store entries by object type for separate trees (e.g., "player", "referee", etc.)
    spatial_data = defaultdict(list)
    spatial_entries = defaultdict(list)  # mirrors spatial_data with full entry references
    spatial_kdtrees = {}

    for entry in combined:
        timestamp_sec = parse_time(entry["timestamp"])
        entry["timestamp_sec"] = timestamp_sec  # store for reuse

    for entry in combined:
        obj_type = entry["object_type"]

        if obj_type == "ball":
            entry["tracking_id"] = 0
            cleaned.append(entry)
            continue

        pos = entry["pitch_position"]
        timestamp = entry["timestamp_sec"]

        # Build tree on-the-fly if there are candidates
        candidates = []
        if spatial_data[obj_type]:
            spatial_kdtrees[obj_type] = KDTree(spatial_data[obj_type])
            idxs = spatial_kdtrees[obj_type].query_ball_point(pos, r=distance_threshold)
            candidates = [spatial_entries[obj_type][i] for i in idxs]

        matched = False
        for candidate in candidates:
            time_diff = abs(candidate["timestamp_sec"] - timestamp)
            if time_diff < time_threshold:
                entry["tracking_id"] = candidate["tracking_id"]
                matched = True
                break

        if not matched:
            entry["tracking_id"] = id_counter
            id_counter += 1

        # Add to index
        spatial_data[obj_type].append(pos)
        spatial_entries[obj_type].append(entry)
        cleaned.append(entry)

    # Optional: sort by timestamp
    cleaned.sort(key=lambda x: x["timestamp_sec"])
    for e in cleaned:
        e.pop("timestamp_sec", None)  # remove helper field
    return cleaned
