import os
import logging
from typing import Tuple, Dict, Any
import requests

logger = logging.getLogger("gio_dashboard.inference_client")

DEFAULT_API_URL = "http://127.0.0.1:8000"
HEALTH_TIMEOUT = 5.0
PREDICT_TIMEOUT = 45.0


class InferenceClient:
    """
    Klien HTTP terpusat untuk berkomunikasi dengan backend FastAPI GIO Inference Service.
    Mendukung konfigurasi dinamis via environment variable INFERENCE_API_URL.
    """

    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv("INFERENCE_API_URL", DEFAULT_API_URL)
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Memeriksa ketersediaan dan status kesiapan model pada endpoint GET /.
        Mengembalikan tuple: (is_ready, details_dict)
        """
        url = f"{self.base_url}/"
        try:
            resp = requests.get(url, timeout=HEALTH_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                is_loaded = data.get("model_loaded", False)
                return is_loaded, data
            elif resp.status_code == 503:
                try:
                    data = resp.json()
                except Exception:
                    data = {"error": {"code": "MODEL_NOT_READY", "message": "Model belum dimuat pada server backend."}}
                return False, data
            else:
                return False, {
                    "error": {
                        "code": f"HTTP_{resp.status_code}",
                        "message": f"Server merespons dengan status HTTP {resp.status_code}."
                    }
                }
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout saat menghubungi health check endpoint: {url}")
            return False, {
                "error": {
                    "code": "CONNECTION_TIMEOUT",
                    "message": "Waktu koneksi ke backend habis (timeout)."
                }
            }
        except requests.exceptions.ConnectionError:
            logger.warning(f"Koneksi gagal ke health check endpoint: {url}")
            return False, {
                "error": {
                    "code": "CONNECTION_FAILED",
                    "message": "Tidak dapat terhubung ke server backend inferensi. Pastikan service FastAPI aktif."
                }
            }
        except Exception as e:
            logger.error(f"Error tak terduga saat health check: {e}")
            return False, {
                "error": {
                    "code": "CLIENT_ERROR",
                    "message": "Terjadi kesalahan internal saat memeriksa status backend."
                }
            }

    def predict(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str = "image/jpeg"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Mengirim file citra ke endpoint POST /predict untuk inferensi dan anotasi.
        Mengembalikan tuple: (is_success, response_or_error_dict)
        """
        if not file_bytes:
            return False, {
                "code": "EMPTY_FILE",
                "message": "Data citra yang dikirim kosong."
            }

        url = f"{self.base_url}/predict"
        files = {
            "file": (filename, file_bytes, mime_type)
        }

        try:
            resp = requests.post(url, files=files, timeout=PREDICT_TIMEOUT)

            # Coba parse respon JSON
            try:
                data = resp.json()
            except Exception:
                return False, {
                    "code": "INVALID_JSON_RESPONSE",
                    "message": f"Server merespons dengan status {resp.status_code}, namun respons bukan JSON valid."
                }

            if resp.status_code == 200:
                if data.get("success") is True and "summary" in data and "annotated_image" in data:
                    return True, data
                else:
                    return False, {
                        "code": "MALFORMED_SUCCESS_RESPONSE",
                        "message": "Respons server 200 tidak memuat atribut data yang diharapkan."
                    }

            # Respons error terstruktur dari FastAPI
            error_info = data.get("error", {})
            err_code = error_info.get("code", f"HTTP_{resp.status_code}")
            err_msg = error_info.get("message", f"Gagal memproses analisis (HTTP {resp.status_code}).")

            return False, {
                "code": err_code,
                "message": err_msg
            }

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout saat inferensi ke {url}")
            return False, {
                "code": "INFERENCE_TIMEOUT",
                "message": "Proses inferensi memakan waktu lebih lama dari batas waktu yang ditentukan. Silakan coba kembali."
            }
        except requests.exceptions.ConnectionError:
            logger.warning(f"Koneksi gagal ke {url}")
            return False, {
                "code": "CONNECTION_FAILED",
                "message": "Tidak dapat terhubung ke server backend inferensi. Pastikan backend FastAPI sedang berjalan."
            }
        except Exception as e:
            logger.error(f"Error tak terduga saat request inferensi: {e}")
            return False, {
                "code": "CLIENT_ERROR",
                "message": "Terjadi kesalahan internal pada klien dashboard saat mengirim request."
            }
