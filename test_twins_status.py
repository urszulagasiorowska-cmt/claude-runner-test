"""Integration test against the real notification service on twins-test (no mocks)."""
import unittest

import twins_status


class TwinsStatusTest(unittest.TestCase):
    def test_notification_is_up_and_publisher_has_sources(self):
        status = twins_status.collect_status()
        self.assertEqual(status["notification"], "UP")
        self.assertTrue(status["sources"], "publisher has no sources")
        for source in status["sources"]:
            self.assertIn("id", source)
            self.assertIsInstance(source["isEnabled"], bool)


if __name__ == "__main__":
    unittest.main()
