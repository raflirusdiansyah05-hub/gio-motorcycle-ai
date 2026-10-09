import unittest
from unittest.mock import patch, MagicMock
import requests

from dashboard.services.inference_client import InferenceClient


class TestInferenceClient(unittest.TestCase):

    def setUp(self):
        self.client = InferenceClient("http://testserver:8000")

    @patch("requests.get")
    def test_check_health_ready(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "ok",
            "model": "YOLO26m",
            "model_loaded": True
        }
        mock_get.return_value = mock_resp

        is_ready, data = self.client.check_health()
        self.assertTrue(is_ready)
        self.assertEqual(data["model"], "YOLO26m")
        mock_get.assert_called_once_with("http://testserver:8000/", timeout=5.0)

    @patch("requests.get")
    def test_check_health_not_ready(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.json.return_value = {
            "status": "unavailable",
            "model": "YOLO26m",
            "model_loaded": False,
            "error": {"code": "MODEL_NOT_READY", "message": "Model belum dimuat"}
        }
        mock_get.return_value = mock_resp

        is_ready, data = self.client.check_health()
        self.assertFalse(is_ready)
        self.assertEqual(data["error"]["code"], "MODEL_NOT_READY")

    @patch("requests.get")
    def test_check_health_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        is_ready, data = self.client.check_health()
        self.assertFalse(is_ready)
        self.assertEqual(data["error"]["code"], "CONNECTION_FAILED")

    @patch("requests.get")
    def test_check_health_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        is_ready, data = self.client.check_health()
        self.assertFalse(is_ready)
        self.assertEqual(data["error"]["code"], "CONNECTION_TIMEOUT")

    @patch("requests.post")
    def test_predict_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "success": True,
            "model": {"name": "YOLO26m"},
            "summary": {"motorcycles": 1, "persons": 2, "violations": 0, "safe": 1},
            "motorcycles": [
                {
                    "id": 1,
                    "bbox": [10.0, 10.0, 100.0, 100.0],
                    "confidence": 0.95,
                    "person_count": 2,
                    "status": "AMAN",
                    "associated_persons": []
                }
            ],
            "unassociated_persons": [],
            "annotated_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
            "processing_time_ms": 320.5
        }
        mock_post.return_value = mock_resp

        dummy_bytes = b"fake_jpeg_content"
        success, data = self.client.predict(dummy_bytes, "test.jpg", "image/jpeg")

        self.assertTrue(success)
        self.assertEqual(data["summary"]["motorcycles"], 1)
        self.assertEqual(data["motorcycles"][0]["status"], "AMAN")
        self.assertTrue(data["annotated_image"].startswith("data:image/jpeg;base64,"))

    @patch("requests.post")
    def test_predict_http_error_422(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 422
        mock_resp.json.return_value = {
            "success": False,
            "error": {
                "code": "CORRUPTED_IMAGE",
                "message": "Citra biner rusak atau tidak dapat didekode."
            }
        }
        mock_post.return_value = mock_resp

        success, err = self.client.predict(b"corrupt", "test.jpg", "image/jpeg")
        self.assertFalse(success)
        self.assertEqual(err["code"], "CORRUPTED_IMAGE")
        self.assertIn("Citra biner rusak", err["message"])

    @patch("requests.post")
    def test_predict_invalid_json(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 502
        mock_resp.json.side_effect = ValueError("No JSON object could be decoded")
        mock_post.return_value = mock_resp

        success, err = self.client.predict(b"bytes", "test.jpg")
        self.assertFalse(success)
        self.assertEqual(err["code"], "INVALID_JSON_RESPONSE")

    @patch("requests.post")
    def test_predict_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        success, err = self.client.predict(b"bytes", "test.jpg")
        self.assertFalse(success)
        self.assertEqual(err["code"], "INFERENCE_TIMEOUT")

    def test_predict_empty_bytes(self):
        success, err = self.client.predict(b"", "test.jpg")
        self.assertFalse(success)
        self.assertEqual(err["code"], "EMPTY_FILE")


if __name__ == "__main__":
    unittest.main()
