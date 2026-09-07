"""留言板：游客可留言，登录用户（作者）可删除。"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import GuestbookMessage, User
from ..schemas import MessageCreate, MessageListOut, MessageOut

router = APIRouter(prefix="/guestbook", tags=["guestbook"])


@router.get("", response_model=MessageListOut)
def list_messages(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(GuestbookMessage).order_by(GuestbookMessage.id.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return MessageListOut(total=total, items=[MessageOut.model_validate(i) for i in items])


@router.post("", response_model=MessageOut, status_code=201)
def create_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
):
    msg = GuestbookMessage(name=data.name.strip(), content=data.content.strip())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return MessageOut.model_validate(msg)


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.get(GuestbookMessage, message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="留言不存在")
    db.delete(msg)
    db.commit()
