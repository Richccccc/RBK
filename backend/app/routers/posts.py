"""博客 CRUD。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Post, PostType, User
from ..schemas import PostCreate, PostListOut, PostListItem, PostOut, PostStatsOut, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])

# 注意：/stats 必须定义在 /{post_id} 之前，否则会被动态路由吞掉
@router.get("/stats", response_model=PostStatsOut)
def post_stats(db: Session = Depends(get_db)):
    rows = db.query(Post.type, func.count(Post.id)).group_by(Post.type).all()
    counts = {t: n for t, n in rows}
    blog = counts.get(PostType.blog, 0)
    diary = counts.get(PostType.diary, 0)
    return PostStatsOut(all=blog + diary, blog=blog, diary=diary)


@router.get("", response_model=PostListOut)
def list_posts(
    type: Optional[PostType] = Query(default=None),
    category: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    if type is not None:
        query = query.filter(Post.type == type)
    if category:
        query = query.filter(Post.category == category)
    if q:
        query = query.filter(or_(Post.title.contains(q), Post.summary.contains(q)))
    total = query.count()
    items = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return PostListOut(total=total, items=[PostListItem.model_validate(i) for i in items])


@router.post("", response_model=PostOut, status_code=201)
def create_post(
    data: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = Post(**data.model_dump(), author_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="博客不存在")
    return post


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    data: PostUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="博客不存在")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="无权修改该博客")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="博客不存在")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="无权删除该博客")
    db.delete(post)
    db.commit()
    return Response(status_code=204)