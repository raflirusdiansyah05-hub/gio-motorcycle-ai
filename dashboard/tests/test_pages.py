import os
import unittest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))


class TestStreamlitPages(unittest.TestCase):

    @patch("dashboard.services.inference_client.InferenceClient.check_health")
    def test_app_dashboard_runs(self, mock_health):
        mock_health.return_value = (True, {"status": "ok", "model": "YOLO26m", "model_loaded": True})

        path = os.path.join(DASHBOARD_DIR, "app.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"App raised exception: {at.exception}")

    def test_page_how_it_works_runs(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "2_How_It_Works.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"How It Works raised exception: {at.exception}")

    def test_page_model_info_runs(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "3_Model_Information.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"Model Information raised exception: {at.exception}")

    def test_page_about_runs(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "4_About.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"About raised exception: {at.exception}")

    def test_page_detection_initial_render(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "1_Detection.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"Detection page initial render raised exception: {at.exception}")


if __name__ == "__main__":
    unittest.main()
