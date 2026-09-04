"""应用配置：通过环境变量或 .env 文件读取。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/blog?charset=utf8mb4"
    # 可选：TiDB Cloud Serverless 强制 TLS，把下载的 CA 证书路径填这里（本地 MySQL 留空即可）
    db_ssl_ca: str = ""
    # 无 CA 文件时启用 TLS（不校验证书，适合 TiDB Serverless，等价 --ssl-mode=REQUIRED）
    db_ssl: bool = False
    jwt_secret: str = "please-change-me-to-a-random-string"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 10080  # 7 天
    max_image_bytes: int = 5 * 1024 * 1024  # 5MB
    # GitHub 图床（可选）：配置后图片存 GitHub 仓库，经 Cloudflare Worker 反代 + CDN 加速；
    # 留空则回退为 base64 内联模式（功能不受影响，只是文章体积大）
    github_token: str = ""  # PAT，需 repo 权限
    github_repo: str = ""  # 如 "Richccccc/RBK-Images"
    github_branch: str = "main"  # 存储分支
    img_base_url: str = ""  # CDN 前缀，如 "https://img.rbk.beauty"；留空用 raw.githubusercontent.com


settings = Settings()