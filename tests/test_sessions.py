import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.services.session_service import fetch_sessions_from_db, filter_sessions, get_session_by_id

class TestSessionsService(unittest.TestCase):
    def test_fetch_sessions(self):
        sessions = fetch_sessions_from_db()
        self.assertGreater(len(sessions), 0)
        s1 = sessions[0]
        self.assertIsNotNone(s1.id)
        self.assertIsNotNone(s1.ip)

    def test_filter_sessions(self):
        res = filter_sessions(severity="High")
        self.assertIsNotNone(res.items)
        self.assertIsInstance(res.total, int)

    def test_get_session_by_id(self):
        sessions = fetch_sessions_from_db()
        target_id = sessions[0].id
        found = get_session_by_id(target_id)
        self.assertEqual(found.id, target_id)

if __name__ == "__main__":
    unittest.main()
