"""Pydantic 请求/响应模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import PostType


class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str
    summary: str = ""
    type: PostType = PostType.blog
    category: str = "未分类"
    font_family: str = ""
    cover_image: str = ""


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = None
    summary: Optional[str] = None
    type: Optional[PostType] = None
    category: Optional[str] = None
    font_family: Optional[str] = None
    cover_image: Optional[str] = None


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    summary: str
    content: str
    type: PostType
    category: str
    font_family: str
    cover_image: str
    author_id: int
    created_at: datetime
    updated_at: datetime


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    summary: str
    type: PostType
    category: str
    cover_image: str
    created_at: datetime
    updated_at: datetime


class PostListOut(BaseModel):
    total: int
    items: list[PostListItem]


class PostStatsOut(BaseModel):
    all: int
    blog: int
    diary: int