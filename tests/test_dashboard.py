import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.services.session_service import get_dashboard_data

class TestDashboardService(unittest.TestCase):
    def test_dashboard_payload(self):
        dash = get_dashboard_data()
        self.assertIsNotNone(dash.overview)
        self.assertGreater(len(dash.overview.metrics), 0)
        self.assertGreater(len(dash.overview.geography), 0)
        self.assertGreater(len(dash.sessions), 0)
        self.assertGreater(len(dash.timeline), 0)
        self.assertGreater(len(dash.intelligence), 0)

if __name__ == "__main__":
    unittest.main()
