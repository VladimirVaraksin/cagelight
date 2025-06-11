import cv2
import numpy as np
from sklearn.cluster import KMeans


class TeamAssigner:
    def __init__(self):
        self.team_colors = {}  # {team_name: color}
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
            top_half = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            start = int(height * 0.15)  # 15 % von oben
            end = int(height * 0.50)  # 50 % von oben

            start_width = int(width * 0.15)  # 15 % von links
            end_width = int(width * 0.85)

            top_half = image[start:end, start_width:end_width]

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