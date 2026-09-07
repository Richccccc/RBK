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
    pinned: bool = False


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = None
    summary: Optional[str] = None
    type: Optional[PostType] = None
    category: Optional[str] = None
    font_family: Optional[str] = None
    cover_image: Optional[str] = None
    pinned: Optional[bool] = None


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
    pinned: bool
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
    pinned: bool
    created_at: datetime
    updated_at: datetime


class PostListOut(BaseModel):
    total: int
    items: list[PostListItem]


class PostStatsOut(BaseModel):
    all: int
    blog: int
    diary: int
    sheets: int = 0
    messages: int = 0


# ---------- 表格参考 ----------

class SheetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=500)


class SheetMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    file_name: str
    sheet_count: int
    rows_count: int
    created_at: datetime
    updated_at: datetime


class SheetListOut(BaseModel):
    total: int
    items: list[SheetMeta]


class SheetTable(BaseModel):
    """单个工作表的解析结果。"""

    name: str
    headers: list[str]
    rows: list[list[str]]


class SheetOut(SheetMeta):
    tables: list[SheetTable]


# ---------- 留言板 ----------

class MessageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    content: str = Field(min_length=1, max_length=1000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    content: str
    created_at: datetime


class MessageListOut(BaseModel):
    total: int
    items: list[MessageOut]