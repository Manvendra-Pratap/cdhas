import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.services.health_service import get_system_health
from backend.database.mongo import check_mongo_health

class TestHealthService(unittest.TestCase):
    def test_health_telemetry(self):
        health = get_system_health()
        self.assertIn(health.api, ("online", "degraded"))
        self.assertIn(health.mongodb, ("online", "offline"))
        self.assertIn(health.cowrie, ("online", "offline"))
        self.assertGreaterEqual(health.latency_ms, 0.0)

    def test_mongo_health_check(self):
        status = check_mongo_health()
        self.assertIsInstance(status, bool)

if __name__ == "__main__":
    unittest.main()
