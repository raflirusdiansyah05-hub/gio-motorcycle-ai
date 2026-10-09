from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = "ok"
    model: str = "YOLO26m"
    model_loaded: bool = True

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class AssociatedPerson(BaseModel):
    person_id: int
    bbox: List[float] = Field(..., description="[x1, y1, x2, y2] bounding box koordinat")
    confidence: float
    ioa: float = Field(..., description="Intersection over Area terhadap motor terkait")

class UnassociatedPerson(BaseModel):
    person_id: int
    bbox: List[float]
    confidence: float

class MotorcycleResult(BaseModel):
    id: int
    bbox: List[float]
    confidence: float
    person_count: int
    status: str = Field(..., description="'AMAN' atau 'PELANGGARAN'")
    associated_persons: List[AssociatedPerson] = Field(default_factory=list)

class DetectionSummary(BaseModel):
    motorcycles: int
    persons: int
    violations: int
    safe: int

class ModelMeta(BaseModel):
    name: str = "YOLO26m"
    checkpoint: str = "artifacts/yolo26m_candidate.pt"

class ImageMeta(BaseModel):
    width: int
    height: int

class PredictionResponse(BaseModel):
    success: bool = True
    model: ModelMeta
    image: ImageMeta
    summary: DetectionSummary
    motorcycles: List[MotorcycleResult]
    unassociated_persons: List[UnassociatedPerson] = Field(default_factory=list)
    annotated_image: str = Field(..., description="Base64 encoded data URI (data:image/jpeg;base64,...)")
    processing_time_ms: float
