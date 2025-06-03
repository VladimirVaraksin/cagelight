import numpy as np
from sklearn.cluster import KMeans


class TeamAssigner:
    def __init__(self):
        self.team_colors = {}  # {team1: color1, team2: color2}

    @staticmethod
    def get_clustering_model(image):
        image_2d = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
        kmeans.fit(image_2d)
        return kmeans

    def get_player_color(self, frame, bbox):
        image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
        top_half_image = image[0:int(image.shape[0] / 2), :]
        kmeans = self.get_clustering_model(top_half_image)
        labels = kmeans.labels_
        clustered_image = labels.reshape(top_half_image.shape[0], top_half_image.shape[1])

        corners = [clustered_image[0, 0], clustered_image[0, -1], clustered_image[-1, 0], clustered_image[-1, -1]]
        non_player_cluster = max(set(corners), key=corners.count)
        player_cluster = 1 - non_player_cluster

        return kmeans.cluster_centers_[player_cluster]

    def assign_team(self, player_color):
        if not self.team_colors:
            # Initialisiere beide Teams mit der ersten Spielerfarbe
            self.team_colors["Team 1"] = player_color
            return "Team 1"

        elif "Team 2" not in self.team_colors:
            color1 = self.team_colors["Team 1"]
            distance = np.linalg.norm(player_color - color1)
            if distance > 50:  # Schwellwert: anpassbar je nach Kontrast der Trikots
                self.team_colors["Team 2"] = player_color
                return "Team 2"
            else:
                return "Team 1"
        else:
            # Beide Farben sind bekannt – vergleiche und gib das nächste Team zurück
            color1 = self.team_colors["Team 1"]
            color2 = self.team_colors["Team 2"]
            dist1 = np.linalg.norm(player_color - color1)
            dist2 = np.linalg.norm(player_color - color2)
            return "Team 1" if dist1 < dist2 else "Team 2"
