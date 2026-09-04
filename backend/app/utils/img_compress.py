"""图片压缩：把上传/Word 里的图片缩放并转 JPEG，控制 base64 体积。

详情接口返回的 content 里内联 base64 图片是页面加载慢的主因，
统一在写入前压缩：最长边 1600px、JPEG 质量 82，单图通常从几 MB 降到 ~150KB。
"""
import base64
from io import BytesIO

from PIL import Image

MAX_DIMENSION = 1600
QUALITY = 82


def _fallback_data_url(data: bytes, content_type: str) -> str:
    ct = content_type if content_type.startswith("image/") else "image/png"
    return "data:%s;base64,%s" % (ct, base64.b64encode(data).decode("ascii"))


def compress_to_jpeg_data_url(data: bytes, content_type: str = "") -> str:
    """压缩图片并返回 JPEG data URL；解析失败时退回原始 data URL。"""
    try:
        img = Image.open(BytesIO(data))
        img.load()
    except Exception:
        return _fallback_data_url(data, content_type)

    # 透明通道贴白底转 RGB（JPEG 不支持透明）
    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # 等比缩小到最长边上限内
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        if w >= h:
            nh = max(1, int(h * MAX_DIMENSION / w))
            img = img.resize((MAX_DIMENSION, nh), Image.LANCZOS)
        else:
            nw = max(1, int(w * MAX_DIMENSION / h))
            img = img.resize((nw, MAX_DIMENSION), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, "JPEG", quality=QUALITY, optimize=True)
    compressed = buf.getvalue()

    # 小图压缩后反而更大时取较小者
    if len(compressed) >= len(data):
        return _fallback_data_url(data, content_type)
    return "data:image/jpeg;base64,%s" % base64.b64encode(compressed).decode("ascii")
