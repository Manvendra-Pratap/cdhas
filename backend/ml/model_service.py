from typing import List, Dict, Any, Tuple
from backend.ml.features import extract_features_from_session, normalize_features, FEATURE_NAMES
from backend.ml.isolation_forest import IsolationForestEngine
from backend.ml.kmeans import (
    KMeansEngine,
    map_centroid_to_archetype,
    ARCHETYPE_DESCRIPTIONS,
    ARCHETYPE_COLORS,
)
from backend.utils.logger import get_logger

logger = get_logger("ml.service")

class MLIntelligenceService:
    def __init__(self):
        self.iso_forest = IsolationForestEngine(n_estimators=50, max_samples=256)
        self.kmeans = KMeansEngine(k=5, max_iter=100)

    def analyze_sessions(self, sessions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Runs ML inference pipeline over sessions:
        1. Feature extraction
        2. Isolation Forest anomaly scoring (0.0 to 1.0)
        3. K-Means clustering & Archetype classification
        4. Replaces severity and archetype with model-assisted scoring
        """
        if not sessions:
            logger.info("No sessions provided for ML analysis.")
            return [], []

        raw_vectors = [extract_features_from_session(s) for s in sessions]
        norm_vectors = normalize_features(raw_vectors)
        n_samples = len(sessions)

        # 1. Fit Isolation Forest & score anomalies
        self.iso_forest.fit(norm_vectors)
        anomaly_scores = [
            self.iso_forest.compute_anomaly_score(vec, n_samples)
            for vec in norm_vectors
        ]

        # 2. Fit K-Means & compute clusters
        cluster_labels, centroids = self.kmeans.fit_predict(norm_vectors)

        # Map centroids to archetypes
        centroid_archetypes = [map_centroid_to_archetype(c) for c in centroids]

        enriched_sessions = []
        cluster_counts: Dict[str, int] = {}

        for idx, s in enumerate(sessions):
            if hasattr(s, "model_dump"):
                s_dict = s.model_dump()
            elif isinstance(s, dict):
                s_dict = dict(s)
            else:
                s_dict = s.__dict__.copy()

            score = anomaly_scores[idx]
            cluster_id = cluster_labels[idx] if idx < len(cluster_labels) else 0
            model_archetype = centroid_archetypes[cluster_id] if cluster_id < len(centroid_archetypes) else "Reconnaissance"

            # Model-assisted severity calculation
            if score >= 0.85:
                severity = "Critical"
            elif score >= 0.65:
                severity = "High"
            elif score >= 0.40:
                severity = "Medium"
            else:
                severity = "Low"

            s_dict["score"] = round(score, 2)
            s_dict["severity"] = severity
            s_dict["archetype"] = model_archetype

            enriched_sessions.append(s_dict)
            cluster_counts[model_archetype] = cluster_counts.get(model_archetype, 0) + 1

        # Build Cluster Analytics
        cluster_analytics = []
        total_analyzed = len(enriched_sessions)
        for idx, (arch, count) in enumerate(cluster_counts.items()):
            share = round((count / max(1, total_analyzed)) * 100)
            centroid_vec = centroids[idx] if idx < len(centroids) else [0.0] * len(FEATURE_NAMES)
            feature_map = {name: round(val, 2) for name, val in zip(FEATURE_NAMES, centroid_vec)}
            
            cluster_analytics.append({
                "cluster_id": idx + 1,
                "archetype": arch,
                "sessions_count": count,
                "share_percentage": share,
                "color": ARCHETYPE_COLORS.get(arch, "#47a8ff"),
                "centroid_features": feature_map,
                "description": ARCHETYPE_DESCRIPTIONS.get(arch, "Behavioral cluster grouping."),
            })

        logger.info(f"ML Intelligence Pipeline completed for {total_analyzed} sessions across {len(cluster_analytics)} behavioral clusters.")
        return enriched_sessions, cluster_analytics

ml_service = MLIntelligenceService()
