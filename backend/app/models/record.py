import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    status = Column(String(20), default="completed")
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), default="1.0.0")
    total_objects = Column(Integer, default=0)
    detection_time = Column(Float, default=None)
    original_image_key = Column(String(500), default=None)
    result_image_key = Column(String(500), default=None)
    error_message = Column(Text, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    results = relationship("DetectionResult", back_populates="record", cascade="all, delete-orphan")


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("detection_records.id", ondelete="CASCADE"), nullable=False, index=True)
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(50), nullable=False)
    chinese_name = Column(String(50), default=None)

    record = relationship("DetectionRecord", back_populates="results")
