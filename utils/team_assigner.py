import cv2
import numpy as np
from sklearn.cluster import KMeans


class TeamAssigner:
    team_colors = None  # {"#B2A48A", "#154460"}  # {team_name: color}
    def __init__(self):
        self.players = {}      # {tracking_id: team_name}

    @staticmethod
    def get_clustering_model(image):
        image_2d = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
        kmeans.fit(image_2d)
        return kmeans

    def get_player_team(self, tracking_id):
        return self.players.get(tracking_id)

    def get_player_color(self, frame, bbox):
        x1, y1, x2, y2 = map(int, bbox)
        image = frame[y1:y2, x1:x2]
        width, height = x2 - x1, y2 - y1
        ratio = height / width
        if ratio < 1:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            height, width = image.shape[:2]  # Update width and height after rotation
        # Überprüfen, ob die Breite größer als 110 ist
        if width > frame.shape[1]/6:
            # Berechne die 20% der Breite und Höhe
            crop_width = int(width * 0.35)
            crop_height = int(height * 0.35)

            # Zuschneiden des Bildes: 20% von allen Seiten
            top_half = image[crop_height:height - crop_height, crop_width:width - crop_width]
        else:
            top_half = image[:int(height * 0.5), :]  # Use the top half of the image

        # cv2.imshow("Top Half", top_half)
        # cv2.waitKey(0)
        kmeans = self.get_clustering_model(top_half)
        labels = kmeans.labels_.reshape(top_half.shape[:2])

        corners = [labels[0, 0], labels[0, -1], labels[-1, 0], labels[-1, -1]]
        non_player_cluster = max(set(corners), key=corners.count)
        player_cluster = 1 - non_player_cluster

        return kmeans.cluster_centers_[player_cluster]

    def assign_team(self, player_color, tracking_id, threshold=50):
        def color_distance(c1, c2):
            return np.linalg.norm(c1 - c2)

        if not self.team_colors:
            team = "Team 1"
            self.team_colors[team] = player_color
            print(player_color)

        elif len(self.team_colors) == 1:
            team1_color = next(iter(self.team_colors.values()))
            team = "Team 2" if color_distance(player_color, team1_color) > threshold else "Team 1"
            self.team_colors.setdefault(team, player_color)

        else:
            distances = {team: color_distance(player_color, color)
                         for team, color in self.team_colors.items()}
            team = min(distances, key=distances.get)

        self.players[tracking_id] = team
        return team

    def assign_team_from_color(self, player_color, tracking_id):
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return np.array([int(hex_color[i:i + 2], 16) for i in (0, 2, 4)])

        player_color_rgb = player_color if isinstance(player_color, np.ndarray) else hex_to_rgb(player_color)

        distances = {team: np.linalg.norm(player_color_rgb - hex_to_rgb(color))
                     for team, color in self.team_colors.items()}
        print(distances)
        closest_team = min(distances, key=distances.get)

        self.players[tracking_id] = closest_team
        return closest_team