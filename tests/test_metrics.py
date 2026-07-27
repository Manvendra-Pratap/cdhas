import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.monitoring.metrics import metrics_collector

class TestMonitoringMetrics(unittest.TestCase):
    def test_metrics_collection(self):
        metrics_collector.record_request(15.2)
        metrics_collector.record_request(550.0)
        self.assertGreaterEqual(metrics_collector.request_count, 2)
        self.assertGreaterEqual(metrics_collector.slow_request_count, 1)
        self.assertIsNotNone(metrics_collector.get_formatted_uptime())

if __name__ == "__main__":
    unittest.main()
