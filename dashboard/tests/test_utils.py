import base64
import unittest
from io import BytesIO

from dashboard.utils.image_utils import decode_base64_data_uri, validate_uploaded_file


class DummyUpload:
    def __init__(self, name: str, size: int, content: bytes = b""):
        self.name = name
        self.size = size
        self.content = content

    def getvalue(self):
        return self.content


class TestImageUtils(unittest.TestCase):

    def test_decode_base64_valid(self):
        original = b"HELLOWORLD_JPEG_BINARY"
        b64_str = base64.b64encode(original).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_str}"

        decoded = decode_base64_data_uri(data_uri)
        self.assertEqual(decoded, original)

    def test_decode_base64_invalid_format(self):
        with self.assertRaises(ValueError):
            decode_base64_data_uri("not_a_valid_data_uri")

        with self.assertRaises(ValueError):
            decode_base64_data_uri("")

        with self.assertRaises(ValueError):
            decode_base64_data_uri("data:image/jpeg;plain,hello")

    def test_validate_uploaded_file_valid_jpg(self):
        dummy = DummyUpload("motor.jpg", 1024 * 500)
        valid, err = validate_uploaded_file(dummy)
        self.assertTrue(valid)
        self.assertIsNone(err)

    def test_validate_uploaded_file_valid_png(self):
        dummy = DummyUpload("motor.png", 1024 * 500)
        valid, err = validate_uploaded_file(dummy)
        self.assertTrue(valid)
        self.assertIsNone(err)

    def test_validate_uploaded_file_invalid_ext(self):
        dummy = DummyUpload("motor.gif", 1024 * 500)
        valid, err = validate_uploaded_file(dummy)
        self.assertFalse(valid)
        self.assertIn("tidak didukung", err)

    def test_validate_uploaded_file_oversized(self):
        dummy = DummyUpload("large.jpg", 11 * 1024 * 1024)  # 11 MB > 10 MB limit
        valid, err = validate_uploaded_file(dummy)
        self.assertFalse(valid)
        self.assertIn("melebihi batas", err)

    def test_validate_uploaded_file_empty(self):
        dummy = DummyUpload("empty.jpg", 0)
        valid, err = validate_uploaded_file(dummy)
        self.assertFalse(valid)
        self.assertIn("kosong", err)

    def test_validate_uploaded_file_none(self):
        valid, err = validate_uploaded_file(None)
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
