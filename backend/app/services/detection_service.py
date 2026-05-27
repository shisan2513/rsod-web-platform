import os
import time
import uuid
from datetime import datetime
from ultralytics import YOLO
import cv2

from app.config import settings
from app.models.schemas import DetectionBox, DetectionResult


class DetectionService:
    YOLO_CLASS_NAMES = {
        0: "Raw_Banana",
        1: "Raw_Mango",
        2: "Ripe_Banana",
        3: "Ripe_Mango",
    }

    YOLO_CLASS_ZH = {
        0: "生香蕉",
        1: "生芒果",
        2: "熟香蕉",
        3: "熟芒果",
    }

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(settings.YOLO_MODEL_PATH):
            self.model = YOLO(settings.YOLO_MODEL_PATH)
        else:
            raise FileNotFoundError(f"Model file not found: {settings.YOLO_MODEL_PATH}")

    def get_class_name(self, class_id: int) -> str:
        return self.YOLO_CLASS_NAMES.get(class_id, f"class_{class_id}")

    def detect_single_image(self, image_path: str, model_name: str = "yolo11n") -> DetectionResult:
        start_time = time.time()
        detection_id = str(uuid.uuid4())

        results = self.model.predict(
            source=image_path,
            conf=settings.CONFIDENCE_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            save=False
        )

        boxes = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.get_class_name(class_id)

                boxes.append(DetectionBox(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                    chinese_name=self.YOLO_CLASS_ZH.get(class_id, f"类别{class_id}")
                ))

        result_filename = f"result_{uuid.uuid4().hex}.jpg"
        result_path = os.path.join(settings.RESULT_DIR, result_filename)

        annotated = results[0].plot()
        cv2.imwrite(result_path, annotated)

        detection_time = time.time() - start_time
        image_filename = os.path.basename(image_path)

        return DetectionResult(
            detection_id=detection_id,
            image_url=f"http://localhost:8000/static/uploads/{image_filename}",
            result_image_url=f"http://localhost:8000/static/results/{result_filename}",
            boxes=boxes,
            total_objects=len(boxes),
            detection_time=round(detection_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )


detection_service = DetectionService()
