import os
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))


class TestVisualRendering(unittest.TestCase):
    """
    Memastikan tidak ada bug rendering HTML literal yang muncul sebagai blok kode
    atau teks mentah pada kelima halaman.
    """

    @patch("dashboard.services.inference_client.InferenceClient.check_health")
    def test_dashboard_no_html_leaks(self, mock_health):
        mock_health.return_value = (True, {"status": "ok", "model": "YOLO26m", "model_loaded": True})

        path = os.path.join(DASHBOARD_DIR, "app.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"Dashboard exception: {at.exception}")

        # Verifikasi tidak ada blok kode yang berisi tag HTML markup
        for code_elem in at.code:
            code_text = code_elem.value
            self.assertNotIn("<p style", code_text)
            self.assertNotIn('<div class="gio-card"', code_text)

    def test_detection_page_no_html_leaks(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "1_Detection.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"Detection exception: {at.exception}")

        for code_elem in at.code:
            code_text = code_elem.value
            self.assertNotIn("<p style", code_text)
            self.assertNotIn('<div class="gio-card"', code_text)

    def test_how_it_works_page_no_html_leaks(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "2_How_It_Works.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"How It Works exception: {at.exception}")

        for code_elem in at.code:
            code_text = code_elem.value
            self.assertNotIn("<p style", code_text)
            self.assertNotIn('<div class="gio-card"', code_text)

    def test_model_info_page_no_html_leaks(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "3_Model_Information.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"Model Information exception: {at.exception}")

        for code_elem in at.code:
            code_text = code_elem.value
            self.assertNotIn("<p style", code_text)
            self.assertNotIn('<div class="gio-card"', code_text)

    def test_about_page_no_html_leaks(self):
        path = os.path.join(DASHBOARD_DIR, "pages", "4_About.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"About exception: {at.exception}")

        for code_elem in at.code:
            code_text = code_elem.value
            self.assertNotIn("<p style", code_text)
            self.assertNotIn('<div class="gio-card"', code_text)


if __name__ == "__main__":
    unittest.main()
