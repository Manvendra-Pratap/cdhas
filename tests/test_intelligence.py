import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.services.intelligence_service import (
    get_intelligence_overview,
    get_detected_anomalies,
    get_cluster_analytics,
)

class TestIntelligenceService(unittest.TestCase):
    def test_intelligence_overview(self):
        intel = get_intelligence_overview()
        self.assertGreater(intel.global_threat_score, 0)
        self.assertGreater(len(intel.dangerous_ips), 0)
        self.assertIsNotNone(intel.mitre_matrix)

    def test_anomalies_detection(self):
        anomalies = get_detected_anomalies()
        self.assertGreater(anomalies.total, 0)

    def test_kmeans_clusters(self):
        clusters = get_cluster_analytics()
        self.assertGreater(clusters.total_clusters, 0)

if __name__ == "__main__":
    unittest.main()
