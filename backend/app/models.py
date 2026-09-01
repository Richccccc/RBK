"""数据库表模型。"""
import enum

from sqlalchemy import BigInteger, Column, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PostType(str, enum.Enum):
    blog = "blog"   # 博客
    diary = "diary"  # 日记


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    summary = Column(String(500), default="")
    # 正文 HTML，图文以内联 data URL 存储，避免免费端文件系统重启丢失
    content = Column(LONGTEXT, nullable=False)
    type = Column(Enum(PostType), default=PostType.blog, nullable=False)
    category = Column(String(50), default="未分类")
    font_family = Column(String(100), default="")
    cover_image = Column(Text, default="")  # URL 或 data URL
    author_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())