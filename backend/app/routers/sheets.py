"""表格参考：上传 xlsx/csv → 解析存库 → 网页预览 + 原文件下载。"""
import base64
import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Sheet, User
from ..schemas import SheetListOut, SheetMeta, SheetOut
from ..utils.table_parser import SheetParseError, parse_table_file

router = APIRouter(prefix="/sheets", tags=["sheets"])

MAX_FILE_BYTES = 8 * 1024 * 1024  # 8MB，base64 后约 10.7MB < MEDIUMTEXT 16MB


@router.get("", response_model=SheetListOut)
def list_sheets(
    q: str = "",
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Sheet)
    if q:
        like = f"%{q}%"
        query = query.filter(Sheet.name.op("LIKE")(like) | Sheet.description.op("LIKE")(like))
    total = query.count()
    items = (
        query.order_by(Sheet.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return SheetListOut(total=total, items=[SheetMeta.model_validate(i) for i in items])


@router.post("", response_model=SheetMeta, status_code=201)
async def create_sheet(
    file: UploadFile = File(...),
    name: str = Form(""),
    description: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail="文件过大（上限 8MB）")

    filename = file.filename or "table.xlsx"
    try:
        tables, total_rows = parse_table_file(data, filename)
    except SheetParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    sheet = Sheet(
        name=(name or "").strip() or filename.rsplit(".", 1)[0],
        description=description.strip(),
        file_name=filename,
        file_content=base64.b64encode(data).decode("ascii"),
        data_json=json.dumps(tables, ensure_ascii=False),
        sheet_count=len(tables),
        rows_count=total_rows,
        author_id=user.id,
    )
    db.add(sheet)
    db.commit()
    db.refresh(sheet)
    return SheetMeta.model_validate(sheet)


@router.get("/{sheet_id}", response_model=SheetOut)
def get_sheet(sheet_id: int, db: Session = Depends(get_db)):
    sheet = db.get(Sheet, sheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="表格不存在")
    meta = SheetMeta.model_validate(sheet)
    tables = json.loads(sheet.data_json)
    return SheetOut(**meta.model_dump(), tables=tables)


@router.get("/{sheet_id}/download")
def download_sheet(sheet_id: int, db: Session = Depends(get_db)):
    """下载上传时的原始文件（xlsx/csv）。"""
    sheet = db.get(Sheet, sheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="表格不存在")
    raw = base64.b64decode(sheet.file_content)
    filename = (sheet.file_name or "table.xlsx").replace('"', "")
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
            "Cache-Control": "no-store",
        },
    )


@router.delete("/{sheet_id}", status_code=204)
def delete_sheet(
    sheet_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sheet = db.get(Sheet, sheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="表格不存在")
    if sheet.author_id != user.id:
        raise HTTPException(status_code=403, detail="无权删除该表格")
    db.delete(sheet)
    db.commit()
