"""数据库表模型。"""
import enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMTEXT
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
    nickname = Column(String(50), default="")  # 平台昵称（展示用，空则回退 username）
    phone = Column(String(20), default="")
    email = Column(String(120), default="")
    avatar_url = Column(String(500), default="")  # 头像（GitHub 图床外链或 data URL）
    created_at = Column(DateTime, server_default=func.now())


class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    summary = Column(String(500), default="")
    # 正文 HTML，图片已外置 GitHub 图床（未配置图床时内联 data URL）
    content = Column(LONGTEXT, nullable=False)
    type = Column(Enum(PostType), default=PostType.blog, nullable=False)
    category = Column(String(50), default="未分类")
    font_family = Column(String(100), default="")
    cover_image = Column(Text, default="")  # URL 或 data URL
    pinned = Column(Boolean, default=False, nullable=False)  # 置顶（仅博客列表生效）
    author_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Sheet(Base):
    """表格参考：上传 xlsx/csv 解析为 JSON 预览，原文件 base64 入库供下载。"""

    __tablename__ = "sheets"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # 展示名称
    description = Column(String(500), default="")  # 备注
    file_name = Column(String(255), nullable=False)  # 原始文件名（含扩展名，用于下载）
    file_content = Column(MEDIUMTEXT, nullable=False)  # 原始文件 base64（≤16MB）
    data_json = Column(LONGTEXT, nullable=False)  # 解析结果：[{name, headers, rows}, ...]
    sheet_count = Column(Integer, default=1)
    rows_count = Column(Integer, default=0)  # 所有 sheet 数据行总数
    cols_count = Column(Integer, default=0)  # 所有 sheet 中最大列数
    author_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class GuestbookMessage(Base):
    """留言板：游客可留言，登录用户可删除。"""

    __tablename__ = "guestbook_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)  # 留言者昵称
    content = Column(String(1000), nullable=False)  # 留言内容
    created_at = Column(DateTime, server_default=func.now())