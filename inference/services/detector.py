import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
from ultralytics import YOLO

logger = logging.getLogger(__name__)

CLASS_ID_MOTOR = 0
CLASS_ID_ORANG = 1
CLASS_NAME_MOTOR = "motor"
CLASS_NAME_ORANG = "orang"

DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "yolo26m_candidate.pt")
)

class YOLODetector:
    """
    Wrapper untuk model YOLO26m dengan pemetaan kelas riil:
    - ID 0: 'motor'
    - ID 1: 'orang'
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH)
        self.model: Optional[YOLO] = None
        self.is_loaded: bool = False
        self._load_model()

    def _load_model(self) -> None:
        if not os.path.exists(self.model_path):
            logger.error(f"Checkpoint model tidak ditemukan di path: {self.model_path}")
            self.is_loaded = False
            return

        try:
            logger.info(f"Memuat checkpoint model YOLO26m dari: {self.model_path}")
            self.model = YOLO(self.model_path)
            self.is_loaded = True
            logger.info(f"Model berhasil dimuat! Task: {self.model.task}, Classes: {self.model.names}")
        except Exception as e:
            logger.error(f"Gagal memuat model YOLO26m: {e}", exc_info=True)
            self.is_loaded = False

    def detect(
        self,
        image: Image.Image,
        conf_threshold: float = 0.25
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Menjalankan inferensi pada satu objek PIL Image.
        Mengembalikan: (motorcycles, persons)
        
        Format setiap elemen:
        {
            "id": int,
            "bbox": [x1, y1, x2, y2],
            "confidence": float
        }
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model detector belum berhasil dimuat.")

        results = self.model(image, conf=conf_threshold, verbose=False)
        
        motorcycles: List[Dict[str, Any]] = []
        persons: List[Dict[str, Any]] = []

        if not results or len(results) == 0:
            return motorcycles, persons

        res = results[0]
        if res.boxes is None or len(res.boxes) == 0:
            return motorcycles, persons

        motor_counter = 1
        person_counter = 1

        for box in res.boxes:
            cls_id = int(box.cls.item())
            conf = float(box.conf.item())
            xyxy = [float(round(coord, 2)) for coord in box.xyxy[0].tolist()]

            if cls_id == CLASS_ID_MOTOR:
                motorcycles.append({
                    "id": motor_counter,
                    "bbox": xyxy,
                    "confidence": round(conf, 4)
                })
                motor_counter += 1
            elif cls_id == CLASS_ID_ORANG:
                persons.append({
                    "id": person_counter,
                    "bbox": xyxy,
                    "confidence": round(conf, 4)
                })
                person_counter += 1

        return motorcycles, persons
