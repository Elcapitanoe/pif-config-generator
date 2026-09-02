import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from pif_generator.release import ReleaseManager


class TestReleaseManager(unittest.TestCase):
    def test_unauthenticated_init(self):
        with patch.dict("os.environ", {}, clear=True):
            manager = ReleaseManager(token=None)
            self.assertIsNone(manager.token)
            self.assertIsNotNone(manager.client)

    def test_publish_requires_token(self):
        with patch.dict("os.environ", {}, clear=True):
            manager = ReleaseManager(token=None)
            with self.assertRaises(ValueError):
                manager.publish_release(target_repo="dummy/repo", files=[])


if __name__ == "__main__":
    unittest.main()
