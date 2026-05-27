from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.record import DetectionRecord
from app.models.schemas import (
    HistoryItem, HistoryResponse, SingleDetectionResponse,
    DetectionBox, DetectionResult,
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/detection", tags=["history"])


@router.get("/history", response_model=HistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str = Query(None),
    type: str = Query(None),
    search: str = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(DetectionRecord).filter(DetectionRecord.user_id == user.id)

    if status:
        query = query.filter(DetectionRecord.status == status)
    if type:
        query = query.filter(DetectionRecord.type == type)
    if search:
        query = query.filter(
            DetectionRecord.original_image_key.ilike(f"%{search}%")
        )

    total = query.count()
    records = (
        query.order_by(DetectionRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        HistoryItem(
            id=str(r.id),
            type=r.type,
            image_url=r.original_image_key or "",
            result_image_url=r.result_image_key or "",
            total_objects=r.total_objects,
            created_at=r.created_at,
            model_name=r.model_name,
        )
        for r in records
    ]

    return HistoryResponse(code=200, message="获取成功", data=items, total=total)


@router.get("/detail/{record_id}", response_model=SingleDetectionResponse)
def get_detail(
    record_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(DetectionRecord)
        .options(joinedload(DetectionRecord.results))
        .filter(DetectionRecord.id == record_id, DetectionRecord.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    boxes = [
        DetectionBox(
            x1=r.x1, y1=r.y1, x2=r.x2, y2=r.y2,
            confidence=r.confidence,
            class_id=r.class_id,
            class_name=r.class_name,
            chinese_name=r.chinese_name or "",
        )
        for r in record.results
    ]

    result = DetectionResult(
        detection_id=str(record.id),
        image_url=record.original_image_key or "",
        result_image_url=record.result_image_key or "",
        boxes=boxes,
        total_objects=record.total_objects,
        detection_time=record.detection_time or 0,
        model_name=record.model_name,
        created_at=record.created_at,
    )

    return SingleDetectionResponse(code=200, message="获取成功", data=result)
