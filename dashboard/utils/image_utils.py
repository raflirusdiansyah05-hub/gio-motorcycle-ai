import base64
import os
from typing import Tuple, Optional


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DEFAULT_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def decode_base64_data_uri(data_uri: str) -> bytes:
    """
    Mendekode Base64 Data URI (misal data:image/jpeg;base64,...) menjadi raw bytes.
    Menghasilkan ValueError jika format tidak valid atau gagal didekode.
    """
    if not data_uri or not isinstance(data_uri, str):
        raise ValueError("Data URI kosong atau bukan string.")

    if "," not in data_uri:
        raise ValueError("Format Data URI tidak valid, tidak memiliki pemisah koma.")

    header, encoded = data_uri.split(",", 1)
    if "base64" not in header.lower():
        raise ValueError("Data URI bukan merupakan encoding base64.")

    try:
        raw_bytes = base64.b64decode(encoded.strip())
        if not raw_bytes:
            raise ValueError("Hasil decoding menghasilkan biner kosong.")
        return raw_bytes
    except Exception as e:
        raise ValueError(f"Gagal mendekode data Base64: {e}")


def validate_uploaded_file(file, max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES) -> Tuple[bool, Optional[str]]:
    """
    Validasi awal file unggahan pada frontend Streamlit.
    Memeriksa nama file, ekstensi (.jpg, .jpeg, .png), dan ukuran maksimum.
    """
    if file is None:
        return False, "Tidak ada file yang dipilih."

    filename = getattr(file, "name", "")
    if not filename:
        return False, "Nama file tidak terdeteksi."

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Format file '{ext}' tidak didukung. Harap unggah file berformat JPG atau PNG."

    file_size = getattr(file, "size", 0)
    if file_size <= 0:
        return False, "File yang diunggah kosong (0 bytes)."

    if file_size > max_size_bytes:
        max_mb = max_size_bytes // (1024 * 1024)
        return False, f"Ukuran file melebihi batas maksimum {max_mb} MB."

    return True, None
