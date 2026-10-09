import io
import os
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from inference.schemas.response import (
    HealthResponse,
    ErrorResponse,
    PredictionResponse,
    ModelMeta,
    ImageMeta,
    DetectionSummary,
    MotorcycleResult,
    AssociatedPerson,
    UnassociatedPerson,
)
from inference.services.detector import YOLODetector
from inference.services.association import associate_persons_to_motorcycles, IOA_THRESHOLD
from inference.services.rules import apply_decision_rules
from inference.services.annotation import annotate_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("inference_api")

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
# Disable Ultralytics auto-installing background packages
os.environ["YOLO_AUTOINSTALL"] = "0"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/pjpeg", "image/x-png"}

# Singleton detector instance
detector: Optional[YOLODetector] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector
    if detector is None:
        logger.info("Menginisialisasi YOLODetector pada startup service...")
        try:
            detector = YOLODetector()
            if detector.is_loaded:
                logger.info("YOLODetector siap menerima request.")
            else:
                logger.warning("YOLODetector diinisialisasi tetapi model belum berhasil dimuat.")
        except Exception as e:
            logger.error(f"Gagal menginisialisasi YOLODetector: {e}", exc_info=True)
            detector = None
    yield
    logger.info("Mematikan service FastAPI...")


app = FastAPI(
    title="GIO YOLO26m Inference Service",
    description="Backend API untuk deteksi sepeda motor dan pelanggaran penumpang berbantuan AI",
    version="1.0.0",
    lifespan=lifespan
)

# Konfigurasi CORS
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [orig.strip() for orig in allowed_origins_raw.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get(
    "/",
    response_model=HealthResponse,
    responses={
        200: {"model": HealthResponse},
        503: {"model": ErrorResponse}
    },
    summary="Health and Readiness Check"
)
async def health_check():
    """
    Memeriksa kesehatan service dan kesiapan model YOLO26m.
    Mengembalikan 200 jika model siap, atau 503 jika model belum dimuat.
    """
    global detector
    is_ready = detector is not None and detector.is_loaded

    if not is_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "model": "YOLO26m",
                "model_loaded": False,
                "error": {
                    "code": "MODEL_NOT_READY",
                    "message": "Checkpoint model YOLO26m belum berhasil dimuat pada server."
                }
            }
        )

    return HealthResponse(
        status="ok",
        model="YOLO26m",
        model_loaded=True
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        200: {"model": PredictionResponse},
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Inference, Association, Counting, and Decision"
)
async def predict_image(file: UploadFile = File(...)):
    """
    Menerima satu citra (JPG atau PNG), menjalankan inferensi YOLO26m, asosiasi IoA,
    penentuan aturan status per-motor, dan menghasilkan gambar anotasi.
    """
    global detector
    start_time = time.perf_counter()

    # 1. Verifikasi kesiapan model
    if detector is None or not detector.is_loaded:
        logger.error("Request /predict ditolak: Model belum siap.")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": {
                    "code": "MODEL_UNAVAILABLE",
                    "message": "Service model belum siap memproses request inferensi."
                }
            }
        )

    # 2. Validasi nama file dan ekstensi
    filename = file.filename or ""
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": f"Ekstensi file '{ext}' tidak didukung. Harap unggah file JPG atau PNG."
                }
            }
        )

    # 3. Validasi MIME type awal
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_MIME_TYPE",
                    "message": f"MIME type '{content_type}' tidak diizinkan. Harap unggah citra image/jpeg atau image/png."
                }
            }
        )

    # 4. Validasi ukuran file bertahap (Streaming size check, max 10 MB)
    file_bytes = bytearray()
    chunk_size = 1024 * 1024  # 1 MB chunks
    try:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_bytes.extend(chunk)
            if len(file_bytes) > MAX_UPLOAD_BYTES:
                await file.close()
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "success": False,
                        "error": {
                            "code": "FILE_TOO_LARGE",
                            "message": f"Ukuran file melebihi batas maksimum {MAX_UPLOAD_MB} MB."
                        }
                    }
                )
    except Exception as e:
        logger.error(f"Error saat membaca stream upload: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "READ_ERROR",
                    "message": "Gagal membaca file unggahan."
                }
            }
        )
    finally:
        await file.close()

    # Pastikan file tidak kosong
    if len(file_bytes) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "EMPTY_FILE",
                    "message": "File yang diunggah kosong (0 bytes)."
                }
            }
        )

    # 5. Validasi integritas citra & decoding in-memory via Pillow
    try:
        image_stream = io.BytesIO(file_bytes)
        with Image.open(image_stream) as img_check:
            img_check.verify()  # Verifikasi header dan struktur biner

        # Buka kembali untuk rendering/inferensi
        image_stream.seek(0)
        image = Image.open(image_stream).convert("RGB")
        img_width, img_height = image.size
    except (UnidentifiedImageError, OSError, SyntaxError) as e:
        logger.warning(f"Decoding citra gagal: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "CORRUPTED_IMAGE",
                    "message": "File citra rusak, terpotong, atau bukan format JPG/PNG yang valid."
                }
            }
        )
    except Exception as e:
        logger.error(f"Error saat parsing citra: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "CORRUPTED_IMAGE",
                    "message": "File citra rusak, terpotong, atau bukan format JPG/PNG yang valid."
                }
            }
        )

    # 6. Jalankan inferensi detector YOLO26m
    try:
        motorcycles, persons = detector.detect(image, conf_threshold=0.25)
    except Exception as e:
        logger.error(f"Kesalahan saat inferensi model: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INFERENCE_FAILED",
                    "message": "Terjadi kesalahan internal saat inferensi model."
                }
            }
        )

    # 7. Jalankan asosiasi IoA (Threshold 0.60, Highest IoA)
    associated_motors, unassociated_persons = associate_persons_to_motorcycles(
        persons=persons,
        motorcycles=motorcycles,
        threshold=IOA_THRESHOLD
    )

    # 8. Terapkan aturan keputusan status (AMAN vs PELANGGARAN)
    motorcycle_results, summary_dict = apply_decision_rules(
        associated_motorcycles=associated_motors,
        total_persons_detected=len(persons)
    )

    # 9. Buat gambar anotasi in-memory (Base64 JPEG)
    try:
        annotated_b64 = annotate_image(
            original_image=image,
            motorcycles=motorcycle_results,
            unassociated_persons=unassociated_persons
        )
    except Exception as e:
        logger.error(f"Gagal membuat anotasi gambar: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "ANNOTATION_FAILED",
                    "message": "Gagal menghasilkan visual anotasi citra."
                }
            }
        )

    # 10. Hitung waktu pemrosesan total
    processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Format respon Pydantic
    return PredictionResponse(
        success=True,
        model=ModelMeta(
            name="YOLO26m",
            checkpoint=detector.model_path
        ),
        image=ImageMeta(
            width=img_width,
            height=img_height
        ),
        summary=DetectionSummary(**summary_dict),
        motorcycles=[
            MotorcycleResult(
                id=m["id"],
                bbox=m["bbox"],
                confidence=m["confidence"],
                person_count=m["person_count"],
                status=m["status"],
                associated_persons=[
                    AssociatedPerson(**p) for p in m.get("associated_persons", [])
                ]
            )
            for m in motorcycle_results
        ],
        unassociated_persons=[
            UnassociatedPerson(**p) for p in unassociated_persons
        ],
        annotated_image=annotated_b64,
        processing_time_ms=processing_time_ms
    )
