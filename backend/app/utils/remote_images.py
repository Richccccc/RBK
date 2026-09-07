"""GitHub 图床：把图片字节上传到 GitHub 仓库，返回 CDN 外链 URL。

- 仅用标准库 urllib，不新增线上依赖（Vercel 免费版无 Pillow 等额外依赖也照常工作）
- 文件名带时间戳 + 随机后缀，可被 CDN 永久缓存
- 未配置 github_token/github_repo 时 externalize_data_urls 原样返回（降级 base64 模式）
"""
import base64
import json
import re
import secrets
from datetime import datetime, timezone
from urllib import request as urlreq

from ..config import settings

DATA_URL_RE = re.compile(r"data:image/([a-zA-Z0-9.+-]+);base64,([A-Za-z0-9+/=]+)")

_EXT_BY_MIME = {
    "jpeg": "jpg",
    "jpg": "jpg",
    "png": "png",
    "gif": "gif",
    "webp": "webp",
    "svg+xml": "svg",
}


def upload_image_bytes(data: bytes, mime: str = "image/jpeg", subdir: str = "images") -> str:
    """上传图片字节到 GitHub 仓库，返回外链 URL。未配置或失败抛异常，由调用方决定降级行为。"""
    if not (settings.github_token and settings.github_repo):
        raise RuntimeError("GitHub 图床未配置（缺少 GITHUB_TOKEN 或 GITHUB_REPO）")

    subtype = mime.split("/", 1)[1].lower() if "/" in mime else "jpg"
    ext = _EXT_BY_MIME.get(subtype, "jpg")
    now = datetime.now(timezone.utc)
    path = "%s/%s/%d-%s.%s" % (
        subdir.strip("/"),
        now.strftime("%Y%m"),
        int(now.timestamp()),
        secrets.token_hex(4),
        ext,
    )

    body = json.dumps(
        {
            "message": "upload %s" % path,
            "content": base64.b64encode(data).decode("ascii"),
            "branch": settings.github_branch,
        }
    ).encode("utf-8")

    req = urlreq.Request(
        "https://api.github.com/repos/%s/contents/%s" % (settings.github_repo, path),
        data=body,
        method="PUT",
        headers={
            "Authorization": "Bearer %s" % settings.github_token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "richpro-blog",
        },
    )
    with urlreq.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if settings.img_base_url:
        # 走 Cloudflare Worker 反代 + CDN（img.rbk.beauty）
        return "%s/%s" % (settings.img_base_url.rstrip("/"), path)
    return result["content"]["download_url"]  # raw.githubusercontent.com 直链


def externalize_data_urls(text: str) -> str:
    """把文本中所有 base64 图片 data URL 上传 GitHub 并替换为外链。

    任何一张图上传失败都保留原 data URL（不丢内容）；未配置图床时原样返回。
    """
    if not (settings.github_token and settings.github_repo) or not text:
        return text

    def repl(m: "re.Match[str]") -> str:
        try:
            data = base64.b64decode(m.group(2))
            url = upload_image_bytes(data, "image/%s" % m.group(1))
            return url
        except Exception:
            return m.group(0)

    return DATA_URL_RE.sub(repl, text)
