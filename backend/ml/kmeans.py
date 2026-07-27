import random
import math
from typing import List, Dict, Any, Tuple

ARCHETYPE_DESCRIPTIONS = {
    "Reconnaissance": "Automated port scanning and surface network probes with brief interactions.",
    "Credential Harvesting": "Brute-force authentication attempts targeting default system credentials.",
    "Malware Deployment": "Payload retrieval, script downloads (curl/wget), and binary execution.",
    "Persistence": "System modification, service creation, and backdooring key startup scripts.",
    "Privilege Escalation": "Sudo exploitation, shadow file access, or pty shell elevation attempts.",
    "Manual Exploration": "Interactive environment discovery, path listing, and human-driven command sequences.",
}

ARCHETYPE_COLORS = {
    "Reconnaissance": "#47a8ff",
    "Credential Harvesting": "#8d7cff",
    "Malware Deployment": "#61dcb0",
    "Persistence": "#f4bf75",
    "Privilege Escalation": "#ef7f88",
    "Manual Exploration": "#efb456",
}

def euclidean_distance(v1: List[float], v2: List[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

class KMeansEngine:
    def __init__(self, k: int = 5, max_iter: int = 100):
        self.k = k
        self.max_iter = max_iter
        self.centroids: List[List[float]] = []

    def fit_predict(self, X: List[List[float]]) -> Tuple[List[int], List[List[float]]]:
        if not X:
            return [], []

        n_samples = len(X)
        n_features = len(X[0])
        effective_k = min(self.k, n_samples)

        random.seed(42)
        initial_indices = random.sample(range(n_samples), effective_k)
        self.centroids = [X[i][:] for i in initial_indices]

        labels = [0] * n_samples

        for _ in range(self.max_iter):
            # Assign clusters
            new_labels = []
            for x in X:
                distances = [euclidean_distance(x, c) for c in self.centroids]
                min_idx = min(range(len(distances)), key=lambda i: distances[i])
                new_labels.append(min_idx)

            if new_labels == labels:
                break
            labels = new_labels

            # Recompute centroids
            for c_idx in range(effective_k):
                cluster_points = [X[i] for i in range(n_samples) if labels[i] == c_idx]
                if cluster_points:
                    self.centroids[c_idx] = [
                        sum(p[f_idx] for p in cluster_points) / len(cluster_points)
                        for f_idx in range(n_features)
                    ]

        return labels, self.centroids

def map_centroid_to_archetype(centroid: List[float]) -> str:
    """
    Features vector:
    0: duration_sec
    1: cmd_count
    2: unique_cmd_count
    3: failed_login_count
    4: priv_escalation_count
    5: download_file_count
    """
    if len(centroid) < 6:
        return "Reconnaissance"

    duration, cmd_count, unique_cmds, failed_login, priv_escalation, downloads = centroid

    if priv_escalation > 0.3:
        return "Privilege Escalation"
    if downloads > 0.3:
        return "Malware Deployment"
    if failed_login > 0.6 and cmd_count <= 2:
        return "Credential Harvesting"
    if cmd_count > 4 and duration > 60:
        return "Manual Exploration"
    if downloads > 0.1 or priv_escalation > 0.1:
        return "Persistence"
    
    return "Reconnaissance"
