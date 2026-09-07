"""启动时初始化数据库：建库、建表、写入默认管理员账号（均幂等，只执行一次）。

- ensure_database: 若 blog 库不存在则自动创建
- create_tables: 若表不存在则自动建表
- seed_admin: 若 admin 用户不存在则写入默认管理员
"""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from .config import settings
from .database import SessionLocal, connect_args, engine
from .models import Base, User
from .utils.security import hash_password

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123456"


def ensure_database() -> None:
    """连接服务器并创建数据库（若不存在的）。"""
    url = make_url(settings.database_url)
    db_name = url.database
    if not db_name:
        return

    # 用不带库名的连接串先连上服务器
    server_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        query=url.query,
    )
    tmp_engine = create_engine(server_url, connect_args=connect_args, pool_pre_ping=True)
    try:
        with tmp_engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4" % db_name
                )
            )
            conn.commit()
    finally:
        tmp_engine.dispose()


def create_tables() -> None:
    """建表（幂等）。"""
    Base.metadata.create_all(bind=engine)


def ensure_columns() -> None:
    """给已存在的表补齐后加的列（幂等；create_all 不会 ALTER 旧表）。

    用 information_schema 判断列是否存在，兼容 TiDB 与本地 MySQL。
    """
    wanted = {
        "posts": {"pinned": "BOOL NOT NULL DEFAULT 0"},
        "sheets": {"cols_count": "INT NOT NULL DEFAULT 0"},
    }
    with engine.connect() as conn:
        for table, cols in wanted.items():
            for col, ddl in cols.items():
                exists = conn.execute(
                    text(
                        "SELECT COUNT(*) FROM information_schema.COLUMNS "
                        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t "
                        "AND COLUMN_NAME = :c"
                    ),
                    {"t": table, "c": col},
                ).scalar()
                if not exists:
                    try:
                        conn.execute(
                            text(f"ALTER TABLE `{table}` ADD COLUMN `{col}` {ddl}")
                        )
                        conn.commit()
                    except Exception:
                        # 并发竞争等场景下失败直接忽略
                        pass


def seed_admin() -> None:
    """写入默认管理员账户（仅当不存在时）。"""
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        if exists is None:
            db.add(
                User(
                    username=DEFAULT_ADMIN_USERNAME,
                    password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                )
            )
            db.commit()
    finally:
        db.close()


def init_db() -> None:
    """初始化入口：按顺序执行建库、建表、补列、写默认账号。"""
    ensure_database()
    create_tables()
    ensure_columns()
    seed_admin()