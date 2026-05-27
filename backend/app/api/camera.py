import base64
import logging
from typing import Any, Dict

import cv2
import numpy as np
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.deps import get_current_user
from app.models.user import User
from app.services.camera_detection_service import camera_detection_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/detection/camera", tags=["camera"])


class CameraDetectRequest(BaseModel):
    image: str = Field(..., description="Base64-encoded JPEG image (data URL or raw)")


@router.post("/detect")
async def detect_frame(
    request: CameraDetectRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Receive a camera frame, run YOLO inference, return detection results."""
    if not camera_detection_service.is_running:
        return {"success": False, "message": "摄像头检测未启动"}

    image_data = request.image
    if not image_data:
        return {"success": False, "message": "缺少图像数据"}

    try:
        if "," in image_data:
            image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return {"success": False, "message": "图像解码失败"}

        result = camera_detection_service.detect_image(image)

        return {
            "success": True,
            "message": "检测成功",
            "data": result,
        }
    except Exception as e:
        logger.error(f"摄像头帧检测异常: {e}")
        return {"success": False, "message": f"检测失败: {str(e)}"}


@router.get("/status")
async def get_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the current camera detection service status."""
    return {
        "success": True,
        "status": camera_detection_service.status.value,
    }


class StartRequest(BaseModel):
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    iou_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


@router.post("/start")
async def start_detection(
    request: StartRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Start the camera detection service."""
    try:
        camera_detection_service.start(
            confidence_threshold=request.confidence_threshold,
            iou_threshold=request.iou_threshold,
        )
        return {"success": True, "message": "摄像头检测已启动"}
    except Exception as e:
        return {"success": False, "message": f"启动失败: {str(e)}"}


@router.post("/stop")
async def stop_detection(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Stop the camera detection service."""
    camera_detection_service.stop()
    return {"success": True, "message": "摄像头检测已停止"}
