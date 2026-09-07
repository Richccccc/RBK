"""用户中心：个人资料查看/更新、头像上传。"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import UserOut, UserUpdateIn
from ..utils.img_compress import compress_to_jpeg_data_url
from ..utils.remote_images import upload_image_bytes

router = APIRouter(prefix="/users", tags=["users"])

MAX_AVATAR_BYTES = 3 * 1024 * 1024  # 3MB（前端已压缩到 256px，一般远小于此）


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.nickname = data.nickname.strip()
    user.phone = data.phone.strip()
    user.email = data.email.strip()
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=400, detail="头像过大（上限 3MB）")
    content_type = file.content_type or "image/png"
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")

    # 优先 GitHub 图床（avatars/ 目录，走 CDN）；未配置或失败时降级 base64
    if settings.github_token and settings.github_repo:
        try:
            user.avatar_url = upload_image_bytes(data, content_type, subdir="avatars")
        except Exception:
            user.avatar_url = compress_to_jpeg_data_url(data, content_type)
    else:
        user.avatar_url = compress_to_jpeg_data_url(data, content_type)

    db.commit()
    db.refresh(user)
    return user
