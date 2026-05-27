import os
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.detection_service import detection_service
from app.utils.file_utils import save_upload_file, ensure_directories
from app.config import settings
from app.models.schemas import (
    SingleDetectionResponse, BatchDetectionResponse, BatchItem,
    HistoryResponse, TargetListResponse, TargetItem,
)
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.record import DetectionRecord as DetectionRecordModel, DetectionResult as DetectionResultModel

router = APIRouter(prefix="/detection", tags=["detection"])

ensure_directories()


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("yolo11n"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        image_path = os.path.join(settings.UPLOAD_DIR, filename)

        result = detection_service.detect_single_image(image_path, model_name)

        # Persist to database
        record = DetectionRecordModel(
            user_id=user.id,
            type="single",
            status="completed",
            model_name=model_name,
            model_version="1.0.0",
            total_objects=result.total_objects,
            detection_time=result.detection_time,
            original_image_key=result.image_url,
            result_image_key=result.result_image_url,
        )
        db.add(record)
        db.flush()

        for box in result.boxes:
            db.add(DetectionResultModel(
                record_id=record.id,
                x1=box.x1, y1=box.y1, x2=box.x2, y2=box.y2,
                confidence=box.confidence,
                class_id=box.class_id,
                class_name=box.class_name,
                chinese_name=box.chinese_name,
            ))

        db.commit()

        return SingleDetectionResponse(
            code=200,
            message="检测成功",
            data=result
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.post("/batch", response_model=BatchDetectionResponse)
async def detect_batch_images(
    files: List[UploadFile] = File(...),
    model_name: str = Form("yolo11n"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = []
    success = 0

    for file in files:
        try:
            filename = await save_upload_file(file, settings.UPLOAD_DIR)
            image_path = os.path.join(settings.UPLOAD_DIR, filename)

            result = detection_service.detect_single_image(image_path, model_name)

            record = DetectionRecordModel(
                user_id=user.id,
                type="batch",
                status="completed",
                model_name=model_name,
                model_version="1.0.0",
                total_objects=result.total_objects,
                detection_time=result.detection_time,
                original_image_key=result.image_url,
                result_image_key=result.result_image_url,
            )
            db.add(record)
            db.flush()

            for box in result.boxes:
                db.add(DetectionResultModel(
                    record_id=record.id,
                    x1=box.x1, y1=box.y1, x2=box.x2, y2=box.y2,
                    confidence=box.confidence,
                    class_id=box.class_id,
                    class_name=box.class_name,
                    chinese_name=box.chinese_name,
                ))

            db.commit()
            results.append(BatchItem(filename=file.filename, result=result))
            success += 1
        except Exception:
            db.rollback()

    return BatchDetectionResponse(
        code=200,
        message=f"批量检测完成：{success}/{len(files)}",
        data=results,
        total=len(files),
        success=success,
    )


@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    targets = [
        TargetItem(id=0, name="Raw_Banana", chinese_name="生香蕉", description="未成熟青色香蕉"),
        TargetItem(id=1, name="Raw_Mango", chinese_name="生芒果", description="未成熟青色芒果"),
        TargetItem(id=2, name="Ripe_Banana", chinese_name="熟香蕉", description="成熟黄色香蕉"),
        TargetItem(id=3, name="Ripe_Mango", chinese_name="熟芒果", description="成熟黄色芒果"),
    ]
    return TargetListResponse(
        code=200,
        message="获取成功",
        data=targets
    )
