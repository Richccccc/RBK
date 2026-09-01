"""数据库连接与会话管理。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

connect_args: dict = {}
if settings.db_ssl_ca:
    # 有 CA 证书文件：校验服务器证书（最安全）
    connect_args["ssl"] = {"ca": settings.db_ssl_ca}
elif settings.db_ssl:
    # 无证书文件：启用 TLS 但不校验（TiDB Serverless 推荐，无需下载证书）
    connect_args["ssl"] = {"check_hostname": False}

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI 依赖：提供数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()