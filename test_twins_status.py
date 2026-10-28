"""Integration tests against the real notification service on twins-test (no mocks)."""
import os
import unittest

import twins_status

PUBLISHER_ID = os.environ.get("PUBLISHER_ID", twins_status.DEFAULT_PUBLISHER_ID)


class TwinsStatusTest(unittest.TestCase):
    def test_health_is_up(self):
        self.assertEqual(twins_status.fetch_health(), "UP")

    def test_publisher_has_sources(self):
        sources = twins_status.fetch_sources(PUBLISHER_ID)
        self.assertTrue(sources, "source list is empty")
        for s in sources:
            self.assertIn("id", s)
            self.assertIsInstance(s["isEnabled"], bool)


if __name__ == "__main__":
    unittest.main()
