"""一次性维护脚本：把数据库里已有文章 content/cover_image 的 base64 图片迁移到 GitHub 图床。

用法（在仓库根目录）：
    python scripts/migrate_images_to_github.py --dsn "mysql+pymysql://user:pass@host/db" ^
        --token ghp_xxx --repo "Richccccc/RBK-Images" --base-url "https://img.rbk.beauty"

- 已是外链（http 开头）的图片自动跳过
- 单张图上传失败保留原样，不中断整体迁移
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import create_engine, text  # noqa: E402

DATA_URL_RE = re.compile(r"data:image/([a-zA-Z0-9.+-]+);base64,([A-Za-z0-9+/=]+)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--base-url", required=True, help="如 https://img.rbk.beauty")
    args = parser.parse_args()

    # 让 backend settings 读到图床配置（在 import app.* 之前设置）
    os.environ["GITHUB_TOKEN"] = args.token
    os.environ["GITHUB_REPO"] = args.repo
    os.environ["GITHUB_BRANCH"] = args.branch
    os.environ["IMG_BASE_URL"] = args.base_url

    from app.utils.remote_images import DATA_URL_RE as APP_RE  # noqa: F401
    from app.utils.remote_images import upload_image_bytes

    engine = create_engine(
        args.dsn,
        pool_pre_ping=True,
        connect_args={"ssl": {"check_hostname": False}},
    )

    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, title, cover_image, content FROM posts")
        ).fetchall()

    for pid, title, cover, content in rows:
        uploaded = 0
        failed = 0

        def repl(m: "re.Match[str]") -> str:
            nonlocal uploaded, failed
            import base64

            try:
                raw = base64.b64decode(m.group(2))
                url = upload_image_bytes(raw, "image/%s" % m.group(1))
                uploaded += 1
                return url
            except Exception as e:  # noqa: BLE001
                failed += 1
                print("    [fail] %s" % e)
                return m.group(0)

        new_cover = DATA_URL_RE.sub(repl, cover or "")
        new_content = DATA_URL_RE.sub(repl, content or "")
        if uploaded == 0 and failed == 0:
            print("[skip] #%s %s (无内联图片)" % (pid, title))
            continue
        with engine.begin() as conn2:
            conn2.execute(
                text(
                    "UPDATE posts SET cover_image = :cover, content = :content WHERE id = :id"
                ),
                {"cover": new_cover, "content": new_content, "id": pid},
            )
        print(
            "[done] #%s %s: 迁移 %d 张%s"
            % (pid, title, uploaded, "，失败 %d 张" % failed if failed else "")
        )


if __name__ == "__main__":
    main()
