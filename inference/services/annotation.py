import io
import base64
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

# Warna token sesuai design.md
COLOR_SAFE = (34, 197, 94)       # #22C55E (Hijau - AMAN)
COLOR_VIOLATION = (239, 68, 68)  # #EF4444 (Merah - PELANGGARAN)
COLOR_PERSON = (56, 189, 248)    # #38BDF8 (Biru muda - Orang terasosiasi)
COLOR_UNASSOCIATED = (156, 163, 175) # #9CA3AF (Abu-abu - Orang bebas)
COLOR_TEXT_BG = (18, 22, 27, 220)    # #12161B semitransparan
COLOR_TEXT = (245, 247, 250)         # #F5F7FA putih

def draw_rounded_rect(draw: ImageDraw.ImageDraw, bbox: List[float], color: tuple, width: int = 3):
    x1, y1, x2, y2 = bbox
    draw.rectangle([x1, y1, x2, y2], outline=color, width=width)

def draw_label(draw: ImageDraw.ImageDraw, text: str, x: float, y: float, bg_color: tuple, text_color: tuple = COLOR_TEXT, font=None):
    # Dapatkan ukuran teks
    if font:
        try:
            bbox = draw.textbbox((x, y), text, font=font)
        except AttributeError:
            bbox = (x, y, x + len(text) * 7, y + 14)
    else:
        bbox = (x, y, x + len(text) * 7, y + 14)

    pad = 3
    rect = [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad]
    draw.rectangle(rect, fill=bg_color)
    draw.text((x, y), text, fill=text_color, font=font)


def annotate_image(
    original_image: Image.Image,
    motorcycles: List[Dict[str, Any]],
    unassociated_persons: Optional[List[Dict[str, Any]]] = None,
    output_quality: int = 88
) -> str:
    """
    Menggambar visual bounding box motor dan orang pada citra asli secara in-memory,
    lalu mengembalikan string Base64 Data URI ('data:image/jpeg;base64,...').

    Tidak ada penulisan file ke filesystem disk.
    """
    unassociated_persons = unassociated_persons or []

    # Salin gambar asli agar tidak memutasi input
    annotated = original_image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)

    # Coba muat font default PIL
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # 1. Gambar Bounding Box Motor
    for m in motorcycles:
        status = m.get("status", "AMAN")
        color = COLOR_VIOLATION if status == "PELANGGARAN" else COLOR_SAFE
        bbox = m["bbox"]
        m_id = m["id"]
        p_count = m.get("person_count", 0)

        # Bounding box motor
        draw_rounded_rect(draw, bbox, color, width=4)

        # Label status motor
        label = f"Motor #{m_id}: {status} ({p_count} org)"
        draw_label(draw, label, bbox[0], max(0, bbox[1] - 16), bg_color=color, font=font)

        # 2. Gambar Orang yang terasosiasi ke motor ini
        for p in m.get("associated_persons", []):
            p_bbox = p["bbox"]
            p_id = p["person_id"]
            p_ioa = p.get("ioa", 0.0)

            draw_rounded_rect(draw, p_bbox, COLOR_PERSON, width=2)
            p_label = f"Orang #{p_id} -> M#{m_id} (IoA:{p_ioa:.2f})"
            draw_label(draw, p_label, p_bbox[0], max(0, p_bbox[1] - 14), bg_color=COLOR_PERSON, text_color=(10, 10, 10), font=font)

    # 3. Gambar Orang yang tidak terasosiasi
    for p in unassociated_persons:
        p_bbox = p["bbox"]
        p_id = p["person_id"]

        draw_rounded_rect(draw, p_bbox, COLOR_UNASSOCIATED, width=2)
        p_label = f"Orang #{p_id} (Unassociated)"
        draw_label(draw, p_label, p_bbox[0], max(0, p_bbox[1] - 14), bg_color=COLOR_UNASSOCIATED, text_color=(10, 10, 10), font=font)

    # Encode ke JPEG in-memory
    buffer = io.BytesIO()
    annotated.save(buffer, format="JPEG", quality=output_quality, optimize=True)
    buffer.seek(0)

    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"
