from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str
    chinese_name: str = ""


class DetectionResult(BaseModel):
    detection_id: str
    image_url: str
    result_image_url: str
    boxes: List[DetectionBox]
    total_objects: int
    detection_time: float
    model_name: str
    created_at: datetime


class SingleDetectionResponse(BaseModel):
    code: int = 200
    message: str = "检测成功"
    data: Optional[DetectionResult] = None


class HistoryItem(BaseModel):
    id: str
    type: str = "single"
    image_url: str
    result_image_url: str
    total_objects: int
    created_at: datetime
    model_name: str


class HistoryResponse(BaseModel):
    code: int = 200
    message: str
    data: List[HistoryItem]
    total: int


class TargetItem(BaseModel):
    id: int
    name: str
    chinese_name: str
    description: Optional[str] = None


class TargetListResponse(BaseModel):
    code: int = 200
    message: str
    data: List[TargetItem]


# --- Auth Schemas ---

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: str
    username: str
    email: str
    nickname: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)

    @field_validator("created_at", mode="before")
    @classmethod
    def coerce_created_at(cls, v):
        if v is None:
            return None
        return v.isoformat() if hasattr(v, "isoformat") else str(v)


# --- Batch Detection Schemas ---

class BatchItem(BaseModel):
    filename: str
    result: DetectionResult


class BatchDetectionResponse(BaseModel):
    code: int = 200
    message: str
    data: List[BatchItem]
    total: int
    success: int


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


# --- Account Management Schemas ---

class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserStats(BaseModel):
    total_detections: int
    total_objects: int
    success_rate: float
    active_days: int
    this_month: int
    avg_objects_per_detection: float


class ProfileResponse(BaseModel):
    code: int = 200
    message: str
    user: UserRead
    stats: UserStats


# --- Video Detection Schemas ---

class RealtimeDetectionResult(BaseModel):
    boxes: List[DetectionBox]
    total_objects: int
    detection_time: float
    image_width: int
    image_height: int


class RealtimeDetectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[RealtimeDetectionResult] = None
