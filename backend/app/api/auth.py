import os
import uuid as uuid_lib
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.record import DetectionRecord
from app.models.schemas import (
    LoginRequest, RegisterRequest, Token, UserRead,
    UpdateProfileRequest, ChangePasswordRequest,
    UserStats, ProfileResponse,
)
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

AVATAR_DIR = os.path.join(settings.STATIC_DIR, "avatars")


def _ensure_avatar_dir():
    os.makedirs(AVATAR_DIR, exist_ok=True)


def _compute_user_stats(user_id, db):
    records = db.query(DetectionRecord).filter(DetectionRecord.user_id == user_id)

    total_detections = records.count()
    total_objects = db.query(func.coalesce(func.sum(DetectionRecord.total_objects), 0)).filter(
        DetectionRecord.user_id == user_id
    ).scalar()

    completed = records.filter(DetectionRecord.status == "completed").count()
    success_rate = round(completed / total_detections * 100, 1) if total_detections > 0 else 0.0

    first = records.order_by(DetectionRecord.created_at.asc()).first()
    if first and first.created_at:
        active_days = (datetime.utcnow() - first.created_at).days + 1
    else:
        active_days = 0

    now = datetime.utcnow()
    this_month = records.filter(
        func.extract("month", DetectionRecord.created_at) == now.month,
        func.extract("year", DetectionRecord.created_at) == now.year,
    ).count()

    avg_objects = round(total_objects / total_detections, 1) if total_detections > 0 else 0.0

    return UserStats(
        total_detections=total_detections,
        total_objects=total_objects,
        success_rate=success_rate,
        active_days=active_days,
        this_month=this_month,
        avg_objects_per_detection=avg_objects,
    )


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.post("/register", response_model=Token)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已注册"
        )

    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        nickname=req.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stats = _compute_user_stats(current_user.id, db)
    return ProfileResponse(
        code=200,
        message="获取成功",
        user=UserRead.model_validate(current_user),
        stats=stats,
    )


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.nickname is not None:
        current_user.nickname = req.nickname
    if req.email is not None:
        existing = db.query(User).filter(User.email == req.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被使用")
        current_user.email = req.email

    db.commit()
    db.refresh(current_user)

    stats = _compute_user_stats(current_user.id, db)
    return ProfileResponse(
        code=200,
        message="更新成功",
        user=UserRead.model_validate(current_user),
        stats=stats,
    )


@router.put("/password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")

    current_user.password_hash = hash_password(req.new_password)
    db.commit()

    return {"code": 200, "message": "密码修改成功"}


@router.post("/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_avatar_dir()

    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "png"
    if ext.lower() not in ("png", "jpg", "jpeg", "gif", "webp"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的图片格式")

    filename = f"{uuid_lib.uuid4().hex}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    avatar_url = f"http://localhost:8000/static/avatars/{filename}"

    # Clean up old avatar if exists
    if current_user.avatar_url:
        old_path = current_user.avatar_url.replace("http://localhost:8000/static/", "")
        old_full = os.path.join(settings.STATIC_DIR, old_path)
        if os.path.isfile(old_full):
            os.remove(old_full)

    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)

    return {"code": 200, "message": "头像上传成功", "avatar_url": avatar_url}
