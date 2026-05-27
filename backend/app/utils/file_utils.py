import os
import uuid
from fastapi import UploadFile


def ensure_directories():
    from app.config import settings
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)


async def save_upload_file(file: UploadFile, directory: str) -> str:
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    filename = f"temp_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(directory, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    return filename


def get_file_url(filename: str, subdir: str) -> str:
    return f"http://localhost:8000/{subdir}/{filename}"
