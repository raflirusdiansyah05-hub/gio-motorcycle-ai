import io
import time
import os
import unittest
from PIL import Image

from dashboard.services.inference_client import InferenceClient
from dashboard.utils.image_utils import decode_base64_data_uri, validate_uploaded_file


class DummyUpload:
    def __init__(self, name: str, size: int, content: bytes):
        self.name = name
        self.size = size
        self.content = content
        self.type = "image/jpeg"

    def getvalue(self):
        return self.content


class TestLiveE2EIntegration(unittest.TestCase):
    """
    End-to-End Integration Tests terhadap service FastAPI yang sedang berjalan
    di http://127.0.0.1:8000.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = InferenceClient("http://127.0.0.1:8000")
        # Pastikan backend siap sebelum pengujian
        is_ready, data = cls.client.check_health()
        if not is_ready:
            raise RuntimeError(
                f"FastAPI backend di http://127.0.0.1:8000 tidak siap: {data}"
            )

    def test_scenario_1_health_and_readiness(self):
        """Skenario 1: Pemeriksaan konektivitas backend secara live."""
        is_ready, data = self.client.check_health()
        self.assertTrue(is_ready, "Backend harus siap dan model harus termuat")
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("model"), "YOLO26m")
        self.assertTrue(data.get("model_loaded"))

    def test_scenario_2_and_3_image_analysis_pipeline(self):
        """Skenario 2 & 3: Upload citra, inferensi live, dan verifikasi struktur hasil."""
        # Buat citra sintetis JPEG 640x640
        img = Image.new("RGB", (640, 640), color=(120, 160, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        img_bytes = buf.getvalue()

        # Validasi file pada sisi frontend
        dummy_file = DummyUpload("motorcycle_test.jpg", len(img_bytes), img_bytes)
        is_valid, err = validate_uploaded_file(dummy_file)
        self.assertTrue(is_valid, f"Validasi file gagal: {err}")

        # Jalankan inferensi via client
        start_t = time.time()
        success, res = self.client.predict(img_bytes, dummy_file.name, dummy_file.type)
        latency = (time.time() - start_t) * 1000

        self.assertTrue(success, f"Inferensi gagal: {res}")
        self.assertTrue(res.get("success"))
        self.assertIn("summary", res)
        self.assertIn("motorcycles", res)
        self.assertIn("annotated_image", res)
        self.assertIn("processing_time_ms", res)
        self.assertGreater(res["processing_time_ms"], 0)

        summary = res["summary"]
        self.assertIn("motorcycles", summary)
        self.assertIn("persons", summary)
        self.assertIn("safe", summary)
        self.assertIn("violations", summary)

    def test_scenario_4_download_annotated_image(self):
        """Skenario 4: Verifikasi dekode citra anotasi Base64 ke biner JPEG valid."""
        img = Image.new("RGB", (320, 320), color=(50, 80, 120))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        img_bytes = buf.getvalue()

        success, res = self.client.predict(img_bytes, "test.jpg", "image/jpeg")
        self.assertTrue(success)

        data_uri = res.get("annotated_image")
        self.assertTrue(data_uri.startswith("data:image/jpeg;base64,"))

        # Dekode ke biner
        raw_jpeg = decode_base64_data_uri(data_uri)
        self.assertGreater(len(raw_jpeg), 100)

        # Verifikasi header JPEG SOI (\xff\xd8)
        self.assertEqual(raw_jpeg[:2], b"\xff\xd8")

        # Verifikasi integritas dengan Pillow Image.open
        decoded_img = Image.open(io.BytesIO(raw_jpeg))
        self.assertEqual(decoded_img.size, (320, 320))
        self.assertEqual(decoded_img.format, "JPEG")

    def test_scenario_5_error_corrupted_image(self):
        """Skenario 5a: Citra korup menghasilkan error terstruktur 422 CORRUPTED_IMAGE."""
        corrupt_bytes = b"CORRUPTED_NON_IMAGE_DATA_STREAM"
        success, err = self.client.predict(corrupt_bytes, "corrupt.jpg", "image/jpeg")
        self.assertFalse(success)
        self.assertEqual(err.get("code"), "CORRUPTED_IMAGE")

    def test_scenario_5_error_oversized_image(self):
        """Skenario 5b: File > 10 MB ditolak dengan 413 FILE_TOO_LARGE."""
        huge_bytes = b"A" * (11 * 1024 * 1024)
        # Frontend check
        dummy = DummyUpload("huge.jpg", len(huge_bytes), huge_bytes)
        valid, err_msg = validate_uploaded_file(dummy)
        self.assertFalse(valid)
        self.assertIn("melebihi batas", err_msg)

        # Backend check via client
        success, err = self.client.predict(huge_bytes, "huge.jpg", "image/jpeg")
        self.assertFalse(success)
        self.assertEqual(err.get("code"), "FILE_TOO_LARGE")


if __name__ == "__main__":
    unittest.main()
