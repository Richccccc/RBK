"""一次性维护脚本：把数据库里已有文章 content/cover_image 的 base64 图片重新压缩。

用法（在仓库根目录）：
    python scripts/compress_existing_images.py --dsn "mysql+pymysql://user:pass@host/db"

仅当压缩结果更小时才更新。逐行打印前后体积对比。
"""
import argparse
import base64
import re
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from PIL import Image as PILImage  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

DATA_URL_RE = re.compile(r"data:image/[a-zA-Z0-9.+-]+;base64,([A-Za-z0-9+/=]+)")
MAX_DIMENSION = 1280
QUALITY = 78


def compress_b64(raw_b64: str) -> str | None:
    """压缩一个 base64 图片，返回更小的新 base64；否则返回 None。"""
    try:
        data = base64.b64decode(raw_b64)
        img = PILImage.open(BytesIO(data))
        img.load()
    except Exception:
        return None

    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        bg = PILImage.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        if w >= h:
            nh = max(1, int(h * MAX_DIMENSION / w))
            img = img.resize((MAX_DIMENSION, nh), PILImage.LANCZOS)
        else:
            nw = max(1, int(w * MAX_DIMENSION / h))
            img = img.resize((nw, MAX_DIMENSION), PILImage.LANCZOS)

    buf = BytesIO()
    img.save(buf, "JPEG", quality=QUALITY, optimize=True)
    new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return new_b64 if len(new_b64) < len(raw_b64) else None


def shrink_text(value: str) -> tuple[str, int, int]:
    """压缩文本里所有 data URL，返回（新文本, 原字节, 新字节）。"""
    before = len(value)

    def repl(m: re.Match) -> str:
        new_b64 = compress_b64(m.group(1))
        if new_b64 is None:
            return m.group(0)
        return "data:image/jpeg;base64," + new_b64

    after_value = DATA_URL_RE.sub(repl, value)
    return after_value, before, len(after_value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", required=True, help="TiDB 连接串 mysql+pymysql://...")
    args = parser.parse_args()

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
        new_cover, c_before, c_after = shrink_text(cover or "")
        new_content, t_before, t_after = shrink_text(content or "")
        saved = (c_before - c_after) + (t_before - t_after)
        if saved <= 0:
            print(f"[skip] #{pid} {title} (无可压缩图片)")
            continue
        with engine.begin() as conn2:
            conn2.execute(
                text("UPDATE posts SET cover_image = :cover, content = :content WHERE id = :id"),
                {"cover": new_cover, "content": new_content, "id": pid},
            )
        print(
            f"[done] #{pid} {title}: "
            f"{(c_before + t_before) // 1024}KB -> {(c_after + t_after) // 1024}KB (省 {saved // 1024}KB)"
        )


if __name__ == "__main__":
    main()
