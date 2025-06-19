import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class TeamAssigner:
    team_colors = {}  # {team_name: color}
    default_colors = None #["#D0D2B5", "#00008B"]  # Default team colors
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

    def get_player_color(self, frame, bbox, tracking_id=0):
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
        # Uncomment the next line to visualize the clustering
        #TeamAssigner.visualize_player_color_clustering(top_half, kmeans, player_cluster, tracking_id)
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
            #print(color_distance(player_color, team1_color))
            team = "Team 2" if color_distance(player_color, team1_color) > threshold else "Team 1"
            self.team_colors.setdefault(team, player_color)

        else:
            #print(self.team_colors)
            distances = {team: color_distance(player_color, color)
                         for team, color in self.team_colors.items()}
            team = min(distances, key=distances.get)

        self.players[tracking_id] = team
        # Visualize
        #TeamAssigner.visualize_team_color_distances(player_color, self.team_colors, tracking_id)
        return team

    def assign_team_from_color(self, player_color, tracking_id):
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return np.array([int(hex_color[i:i + 2], 16) for i in (0, 2, 4)])

        player_color_rgb = player_color if isinstance(player_color, np.ndarray) else hex_to_rgb(player_color)

        distances = {team: np.linalg.norm(player_color_rgb - hex_to_rgb(color))
                     for team, color in self.team_colors.items()}
        #print(distances)
        closest_team = min(distances, key=distances.get)

        self.players[tracking_id] = closest_team
        return closest_team


    def visualize_player_color_clustering(image_crop, kmeans, player_cluster_index, tracking_id):
        """
        Visualize the color clusters from the KMeans model in 3D RGB space.
        """
        image_2d = image_crop.reshape(-1, 3)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Plot pixels in RGB space colored by cluster
        for cluster_idx in np.unique(labels):
            cluster_pixels = image_2d[labels == cluster_idx]
            ax.scatter(cluster_pixels[:, 0],
                       cluster_pixels[:, 1],
                       cluster_pixels[:, 2],
                       label=f"Cluster {cluster_idx}",
                       alpha=0.3)

        # Plot cluster centers
        ax.scatter(centers[:, 0], centers[:, 1], centers[:, 2],
                   s=200, c=centers / 255.0, edgecolors='k', marker='X', label='Centroids')

        # Highlight player cluster
        player_color = centers[player_cluster_index]
        ax.scatter(*player_color, s=300, c=[player_color / 255.0],
                   marker='*', edgecolors='black', linewidths=1.5, label='Assigned Player Color')

        ax.set_title(f"K-Means Clustering Player {tracking_id} in RGB Color Space")
        ax.set_xlabel("Red")
        ax.set_ylabel("Green")
        ax.set_zlabel("Blue")
        ax.legend()
        plt.show()

    def visualize_team_color_distances(player_color, team_colors, id):
        """
        Visualize the Euclidean distance between the player's color and each team's color.
        """

        def color_distance(c1, c2):
            return np.linalg.norm(c1 - c2)

        player_color = np.array(player_color)
        teams = []
        distances = []
        colors = []

        for team_name, team_color in team_colors.items():
            dist = color_distance(player_color, team_color)
            teams.append(team_name)
            distances.append(dist)
            colors.append(team_color / 255.0)  # Normalize for matplotlib

        plt.figure(figsize=(8, 4))
        bars = plt.bar(teams, distances, color=colors, edgecolor='black')

        for bar, dist in zip(bars, distances):
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 2, f"{dist:.1f}", ha='center', va='bottom')

        plt.title(f"Distance Between Player {id} Color and Team Colors")
        plt.ylabel("Euclidean Distance (RGB)")
        plt.xlabel("Team")
        plt.ylim(0, max(distances) * 1.2)
        plt.tight_layout()
        plt.show()

