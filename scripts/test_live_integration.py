import io
import requests
from PIL import Image

def test_live_integration():
    base_url = "http://127.0.0.1:8000"
    
    print("=== 1. Test GET / (Health/Readiness) ===")
    r = requests.get(f"{base_url}/", timeout=5)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.json()}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    print("[OK] Health/Readiness test passed!")

    print("\n=== 2. Test POST /predict (Real Image Inference) ===")
    # Buat gambar sintetis 640x640 JPG
    img = Image.new("RGB", (640, 640), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    files = {"file": ("test_live.jpg", img_bytes, "image/jpeg")}
    r_pred = requests.post(f"{base_url}/predict", files=files, timeout=30)
    print(f"Status Code: {r_pred.status_code}")
    res = r_pred.json()
    print(f"Success: {res.get('success')}")
    print(f"Model: {res.get('model')}")
    print(f"Summary: {res.get('summary')}")
    print(f"Processing time ms: {res.get('processing_time_ms')}")
    assert r_pred.status_code == 200
    assert res["success"] is True
    assert "annotated_image" in res
    assert res["annotated_image"].startswith("data:image/jpeg;base64,")
    print("[OK] Real inference test passed!")

    print("\n=== 3. Test Error Conditions via Live HTTP ===")
    # 3a. File kosong
    r_empty = requests.post(f"{base_url}/predict", files={"file": ("empty.jpg", b"", "image/jpeg")})
    print(f"Empty file status: {r_empty.status_code}, error: {r_empty.json().get('error', {}).get('code')}")
    assert r_empty.status_code == 400
    assert r_empty.json()["error"]["code"] == "EMPTY_FILE"

    # 3b. Ekstensi ilegal (.gif)
    r_ext = requests.post(f"{base_url}/predict", files={"file": ("bad.gif", b"GIF89a", "image/gif")})
    print(f"Bad ext status: {r_ext.status_code}, error: {r_ext.json().get('error', {}).get('code')}")
    assert r_ext.status_code == 400
    assert r_ext.json()["error"]["code"] == "INVALID_FILE_TYPE"

    # 3c. Gambar korup
    r_corrupt = requests.post(f"{base_url}/predict", files={"file": ("corrupt.jpg", b"NOT_AN_IMAGE_CONTENT", "image/jpeg")})
    print(f"Corrupt image status: {r_corrupt.status_code}, error: {r_corrupt.json().get('error', {}).get('code')}")
    assert r_corrupt.status_code == 422
    assert r_corrupt.json()["error"]["code"] == "CORRUPTED_IMAGE"

    # 3d. File terlalu besar (>10 MB)
    large_bytes = b"0" * (11 * 1024 * 1024)
    r_large = requests.post(f"{base_url}/predict", files={"file": ("large.jpg", large_bytes, "image/jpeg")})
    print(f"Large file status: {r_large.status_code}, error: {r_large.json().get('error', {}).get('code')}")
    assert r_large.status_code == 413
    assert r_large.json()["error"]["code"] == "FILE_TOO_LARGE"

    print("\n=== 4. Test Streamlit HTTP Response ===")
    r_st = requests.get("http://localhost:8501", timeout=5)
    print(f"Streamlit HTTP status: {r_st.status_code}")
    assert r_st.status_code == 200
    print("[OK] Streamlit live HTTP responding!")

    print("\nALL LIVE INTEGRATION TESTS PASSED!")

if __name__ == "__main__":
    test_live_integration()
