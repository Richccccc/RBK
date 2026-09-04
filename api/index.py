"""Vercel Python Serverless 函数入口：把请求交给 FastAPI 应用处理。

Vercel 会自动把 api/ 下的 Python 文件识别为 serverless 函数，
并使用本模块中名为 `app` 的 ASGI 应用。
"""
import os
import sys

# 将 backend 目录加入模块搜索路径，使 `app` 包（backend/app）可导入
BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend")
)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app  # noqa: E402
from app.init_db import init_db  # noqa: E402

# serverless 冷启动时 FastAPI lifespan 可能不会执行，
# 这里在模块加载时手动初始化一次数据库（建库/建表/默认管理员，全部幂等）
init_db()
