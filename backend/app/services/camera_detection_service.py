import time
import threading
import logging
from typing import Any, Dict, Optional
from enum import Enum

import numpy as np

from app.services.detection_service import detection_service

logger = logging.getLogger(__name__)


class DetectionStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class CameraDetectionService:
    """Singleton service for real-time camera detection.

    Shares the YOLO model from detection_service and adds state management,
    FPS tracking, and concurrency control for the camera stream use case.
    """

    _instance: Optional["CameraDetectionService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._lock = threading.Lock()
        self._status = DetectionStatus.STOPPED
        self._confidence_threshold = 0.5
        self._iou_threshold = 0.7
        self._model_image_size = 320

        self._frame_count = 0
        self._fps_frame_count = 0
        self._last_fps_time = time.time()
        self._current_fps = 0.0

        self._max_concurrent_requests = 5
        self._request_semaphore = threading.Semaphore(self._max_concurrent_requests)

        self._initialized = True

    @property
    def is_running(self) -> bool:
        return self._status == DetectionStatus.RUNNING

    @property
    def status(self) -> DetectionStatus:
        return self._status

    def start(self, confidence_threshold: float = 0.5, iou_threshold: float = 0.7):
        """Start the camera detection service (loads model if needed)."""
        with self._lock:
            if self._status == DetectionStatus.RUNNING:
                logger.info("Detection already running, restarting")
                self.stop()

            try:
                if detection_service.model is None:
                    detection_service._load_model()

                self._confidence_threshold = confidence_threshold
                self._iou_threshold = iou_threshold
                self._frame_count = 0
                self._fps_frame_count = 0
                self._last_fps_time = time.time()
                self._current_fps = 0.0
                self._status = DetectionStatus.RUNNING
                logger.info("Camera detection service started")
            except Exception as e:
                self._status = DetectionStatus.ERROR
                logger.error(f"Failed to start camera detection: {e}")
                raise

    def stop(self):
        """Stop the camera detection service."""
        with self._lock:
            self._status = DetectionStatus.STOPPED
            logger.info("Camera detection service stopped")

    def pause(self):
        with self._lock:
            if self._status == DetectionStatus.RUNNING:
                self._status = DetectionStatus.PAUSED

    def resume(self):
        with self._lock:
            if self._status == DetectionStatus.PAUSED:
                self._status = DetectionStatus.RUNNING

    def detect_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Run YOLO inference on a single frame.

        Args:
            image: BGR numpy array from cv2.imdecode.

        Returns:
            Dict with boxes, frame_index, fps, detection_time, total_objects.
        """
        with self._request_semaphore:
            start_time = time.time()

            results = detection_service.model.predict(
                source=image,
                conf=self._confidence_threshold,
                iou=self._iou_threshold,
                save=False,
                imgsz=self._model_image_size,
                half=False,
                verbose=False,
                stream=False,
            )

            boxes = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = detection_service.get_class_name(class_id)
                    chinese_name = detection_service.YOLO_CLASS_ZH.get(class_id, f"类别{class_id}")

                    boxes.append({
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "confidence": confidence,
                        "class_id": class_id,
                        "class_name": class_name,
                        "chinese_name": chinese_name,
                    })

            detection_time = time.time() - start_time

            self._frame_count += 1
            self._fps_frame_count += 1
            now = time.time()
            elapsed = now - self._last_fps_time
            fps = self._current_fps
            if elapsed >= 1.0:
                fps = self._fps_frame_count / elapsed
                self._fps_frame_count = 0
                self._last_fps_time = now
                self._current_fps = fps

            return {
                "boxes": boxes,
                "frame_index": self._frame_count,
                "fps": round(fps, 1),
                "detection_time": round(detection_time, 3),
                "total_objects": len(boxes),
            }


camera_detection_service = CameraDetectionService()
