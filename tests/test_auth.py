import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

class TestAuthSecurity(unittest.TestCase):
    def test_password_hashing(self):
        raw = "MySecretPass123"
        hashed = hash_password(raw)
        self.assertTrue(verify_password(raw, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_tokens(self):
        token = create_access_token("admin", role="admin")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], "admin")
        self.assertEqual(payload["role"], "admin")

if __name__ == "__main__":
    unittest.main()
