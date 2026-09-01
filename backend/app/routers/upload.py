"""上传：图片（转 data URL）、Word 文档（转 HTML）。"""
import base64

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..config import settings
from ..deps import get_current_user
from ..models import User
from ..services.word_parser import parse_docx_to_html

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    if len(data) > settings.max_image_bytes:
        raise HTTPException(status_code=400, detail="图片过大（上限 5MB）")
    content_type = file.content_type or "image/png"
    if not content_type.startswith("image/"):
        content_type = "image/png"
    url = "data:%s;base64,%s" % (content_type, base64.b64encode(data).decode("ascii"))
    return {"url": url}


@router.post("/word")
async def upload_word(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    try:
        html = parse_docx_to_html(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Word 文档解析失败，请上传有效的 .docx 文件")
    return {"html": html}