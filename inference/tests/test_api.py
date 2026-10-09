import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from inference.app import app
import inference.app as app_module
from inference.services.detector import YOLODetector

def create_dummy_image_bytes(format="JPEG", size=(200, 200), color=(255, 0, 0)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


class MockDetector:
    def __init__(self, is_loaded=True, detections=None):
        self.is_loaded = is_loaded
        self.model_path = "artifacts/mock_model.pt"
        self.detections = detections or ([], [])

    def detect(self, image, conf_threshold=0.25):
        if not self.is_loaded:
            raise RuntimeError("Model belum dimuat.")
        return self.detections


@pytest.fixture
def client():
    # Gunakan MockDetector default siap
    app_module.detector = MockDetector(
        is_loaded=True,
        detections=(
            [{"id": 1, "bbox": [10.0, 10.0, 100.0, 100.0], "confidence": 0.9}],
            [{"id": 1, "bbox": [10.0, 10.0, 50.0, 50.0], "confidence": 0.85}] # IoA = 1.0 ke motor 1
        )
    )
    with TestClient(app) as test_client:
        yield test_client


def test_health_check_ready(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == "YOLO26m"
    assert data["model_loaded"] is True


def test_health_check_unavailable():
    app_module.detector = MockDetector(is_loaded=False)
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 503
        data = response.json()
        assert data["model_loaded"] is False
        assert data["error"]["code"] == "MODEL_NOT_READY"


def test_predict_success(client):
    img_bytes = create_dummy_image_bytes(format="JPEG")
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["model"]["name"] == "YOLO26m"
    assert data["image"]["width"] == 200
    assert data["image"]["height"] == 200
    assert data["summary"]["motorcycles"] == 1
    assert data["summary"]["persons"] == 1
    assert data["summary"]["violations"] == 0
    assert data["summary"]["safe"] == 1
    assert len(data["motorcycles"]) == 1
    assert data["motorcycles"][0]["status"] == "AMAN"
    assert len(data["motorcycles"][0]["associated_persons"]) == 1
    assert data["annotated_image"].startswith("data:image/jpeg;base64,")
    assert "processing_time_ms" in data


def test_predict_png_format(client):
    img_bytes = create_dummy_image_bytes(format="PNG")
    files = {"file": ("test.png", img_bytes, "image/png")}
    response = client.post("/predict", files=files)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_predict_invalid_extension(client):
    img_bytes = create_dummy_image_bytes()
    files = {"file": ("test.pdf", img_bytes, "application/pdf")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_FILE_TYPE"


def test_predict_invalid_mime(client):
    img_bytes = create_dummy_image_bytes()
    files = {"file": ("test.jpg", img_bytes, "text/plain")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_MIME_TYPE"


def test_predict_empty_file(client):
    files = {"file": ("test.jpg", b"", "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMPTY_FILE"


def test_predict_corrupted_image(client):
    corrupt_bytes = b"THIS IS NOT A VALID JPEG OR PNG IMAGE BUFFER"
    files = {"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "CORRUPTED_IMAGE"


def test_predict_file_too_large(client, monkeypatch):
    # Set MAX_UPLOAD_BYTES kecil (100 KB) untuk test
    monkeypatch.setattr(app_module, "MAX_UPLOAD_BYTES", 100 * 1024)
    large_bytes = b"0" * (120 * 1024) # 120 KB
    files = {"file": ("large.jpg", large_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "FILE_TOO_LARGE"


def test_predict_model_unavailable():
    app_module.detector = MockDetector(is_loaded=False)
    with TestClient(app) as client:
        img_bytes = create_dummy_image_bytes()
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
        response = client.post("/predict", files=files)
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "MODEL_UNAVAILABLE"


def test_predict_real_candidate_smoke():
    # Smoke test menggunakan YOLODetector asli dengan candidate model
    app_module.detector = YOLODetector("artifacts/yolo26m_candidate.pt")
    with TestClient(app) as client:
        img_bytes = create_dummy_image_bytes(size=(640, 640))
        files = {"file": ("smoke.jpg", img_bytes, "image/jpeg")}
        response = client.post("/predict", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model"]["name"] == "YOLO26m"
        assert data["annotated_image"].startswith("data:image/jpeg;base64,")
