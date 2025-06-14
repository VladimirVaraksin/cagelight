from datetime import datetime, timedelta

class IDManager:
    def __init__(self, max_age_seconds=5):
        self.id_map = {}  # yolo_id → (persistent_id, last_seen_time)
        self.persistent_id_counter = 1
        self.max_age = timedelta(seconds=max_age_seconds)

    def _parse_timestamp(self, ts_str):
        # Beispiel: "12:34:567" → timedelta
        minutes, seconds, millis = map(int, ts_str.split(":"))
        return timedelta(minutes=minutes, seconds=seconds, milliseconds=millis)

    def _euclidean_distance(self, pos1, pos2):
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

    def _try_reidentify(self, new_entry, recent_entries, max_position_dist=2.5):
        #print(self.id_map)
        if not recent_entries:
            return None  # Kein Re-ID im ersten Frame möglich

        new_time = self._parse_timestamp(new_entry["timestamp"])
        best_match = None
        best_distance = float("inf")

        for past in recent_entries:
            if (
                past["object_type"] == "player" and
                past["team"] == new_entry["team"] and
                past["camera_id"] != new_entry["camera_id"]
            ):
                past_time = self._parse_timestamp(past["timestamp"])
                time_diff = abs((new_time - past_time).total_seconds())

                if time_diff > self.max_age.total_seconds():
                    continue

                dist = self._euclidean_distance(new_entry["pitch_position"], past["pitch_position"])

                if dist < max_position_dist and dist < best_distance:
                    best_match = past
                    best_distance = dist

        return best_match["tracking_id"] if best_match else None

    def get_persistent_id(self, yolo_id, entry, recent_entries, first_frame=False):
        current_time = self._parse_timestamp(entry["timestamp"])
        reid_id = None

        # Vergessenslogik: alte YOLO-IDs entfernen
        self._cleanup_old_ids(current_time)

        if entry["object_type"] == "ball":
            return 0  # Ball bekommt immer ID 0

        if yolo_id in self.id_map:
            # YOLO-ID bekannt → Update Zeitstempel und zurückgeben
            self.id_map[yolo_id] = (self.id_map[yolo_id][0], current_time)
            return self.id_map[yolo_id][0]

        # Re-ID nur für Spieler
        if not first_frame:
            # Versuche, den Spieler zu re-identifizieren
            reid_id = self._try_reidentify(entry, recent_entries)

        if reid_id is not None:
            persistent_id = reid_id
        else:
            persistent_id = entry["tracking_id"]
            self.persistent_id_counter += 1

        # Neu zuordnen
        self.id_map[yolo_id] = (persistent_id, current_time)
        return persistent_id

    def _cleanup_old_ids(self, current_time):
        expired = [yolo_id for yolo_id, (_, last_seen) in self.id_map.items()
                   if current_time - last_seen > self.max_age]
        for yolo_id in expired:
            del self.id_map[yolo_id]
