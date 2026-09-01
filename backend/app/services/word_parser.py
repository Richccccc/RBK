"""Word(.docx) 解析：把文档内容/图片/基本样式转成带内联图片的 HTML。

保真范围：标题、正文段落、粗体/斜体/下划线、字体、字号、颜色、高亮、
对齐方式、项目符号/编号列表、表格、内联图片（以 data URL 内联）。
"""
import base64
import re
from io import BytesIO

from docx import Document
from docx.oxml.ns import qn


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _image_to_data_url(doc: Document, rid: str) -> str:
    """根据关系 id 读取图片二进制并转为 data URL。"""
    try:
        part = doc.part.rels[rid].target_part
        blob = part.blob
        content_type = part.content_type or "image/png"
        if "image" not in content_type:
            content_type = "image/png"
        return "data:%s;base64,%s" % (content_type, base64.b64encode(blob).decode("ascii"))
    except Exception:
        return ""


def _parse_run_props(r) -> dict:
    """解析 run 的字体/字号/颜色/粗斜体下划线等属性。"""
    props: dict = {}
    r_pr = r.find(qn("w:rPr"))
    if r_pr is None:
        return props

    b = r_pr.find(qn("w:b"))
    if b is not None and b.get(qn("w:val")) not in ("0", "false"):
        props["bold"] = True
    i = r_pr.find(qn("w:i"))
    if i is not None and i.get(qn("w:val")) not in ("0", "false"):
        props["italic"] = True
    u = r_pr.find(qn("w:u"))
    if u is not None and u.get(qn("w:val")) not in ("none", None):
        props["underline"] = True

    fonts = r_pr.find(qn("w:rFonts"))
    if fonts is not None:
        font = (
            fonts.get(qn("w:eastAsia"))
            or fonts.get(qn("w:ascii"))
            or fonts.get(qn("w:hAnsi"))
        )
        if font:
            props["font"] = font

    sz = r_pr.find(qn("w:sz"))
    if sz is not None and sz.get(qn("w:val")):
        try:
            props["size"] = "%spt" % (int(sz.get(qn("w:val"))) / 2)
        except ValueError:
            pass

    color = r_pr.find(qn("w:color"))
    if color is not None and color.get(qn("w:val")):
        props["color"] = "#" + color.get(qn("w:val"))

    highlight = r_pr.find(qn("w:highlight"))
    if highlight is not None and highlight.get(qn("w:val")):
        props["highlight"] = highlight.get(qn("w:val"))

    return props


def _run_text(r) -> str:
    return "".join((t.text or "") for t in r.iter(qn("w:t")))


def _image_urls_in_run(r, doc: Document) -> list[str]:
    """返回该 run 内所有内联图片的 data URL。"""
    urls = []
    for blip in r.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            url = _image_to_data_url(doc, rid)
            if url:
                urls.append(url)
    for imagedata in r.iter("{urn:schemas-microsoft-com:vml}imagedata"):
        rid = imagedata.get(qn("r:id"))
        if rid:
            url = _image_to_data_url(doc, rid)
            if url:
                urls.append(url)
    return urls


def _render_runs(p_el, doc: Document) -> str:
    """渲染段落内的 run 序列（不含外层 p/h/li 标签）。"""
    parts = []
    for child in p_el:
        tag = child.tag
        if tag == qn("w:r"):
            images = _image_urls_in_run(child, doc)
            if images:
                for url in images:
                    parts.append(f'<img src="{url}" style="max-width:100%;" />')
                continue
            text = _run_text(child)
            if not text:
                continue
            props = _parse_run_props(child)
            html = _escape(text)
            if props.get("bold"):
                html = "<strong>%s</strong>" % html
            if props.get("italic"):
                html = "<em>%s</em>" % html
            if props.get("underline"):
                html = "<u>%s</u>" % html
            styles = []
            if props.get("font"):
                styles.append("font-family:'%s',sans-serif;" % props["font"])
            if props.get("size"):
                styles.append("font-size:%s;" % props["size"])
            if props.get("color"):
                styles.append("color:%s;" % props["color"])
            if props.get("highlight"):
                styles.append("background-color:%s;" % props["highlight"])
            if styles:
                html = '<span style="%s">%s</span>' % ("".join(styles), html)
            parts.append(html)
        elif tag == qn("w:tab"):
            parts.append("&nbsp;&nbsp;&nbsp;&nbsp;")
        elif tag == qn("w:br") or tag == qn("w:cr"):
            parts.append("<br/>")
    return "".join(parts)


def _paragraph_style_name(p_el) -> str:
    p_pr = p_el.find(qn("w:pPr"))
    if p_pr is None:
        return ""
    p_style = p_pr.find(qn("w:pStyle"))
    if p_style is None:
        return ""
    return p_style.get(qn("w:val")) or ""


def _paragraph_alignment(p_el) -> str:
    p_pr = p_el.find(qn("w:pPr"))
    if p_pr is None:
        return ""
    jc = p_pr.find(qn("w:jc"))
    if jc is None:
        return ""
    return jc.get(qn("w:val")) or ""


def _detect_list_type(p_el) -> str | None:
    p_pr = p_el.find(qn("w:pPr"))
    if p_pr is None:
        return None
    num_pr = p_pr.find(qn("w:numPr"))
    style_name = _paragraph_style_name(p_el)
    if num_pr is not None or "list" in style_name.lower():
        if "number" in style_name.lower():
            return "ol"
        return "ul"
    return None


def _render_paragraph_block(p_el, doc: Document) -> str:
    """渲染一个普通段落（非列表），返回带 h/p 标签的 HTML。"""
    content = _render_runs(p_el, doc)
    align = _paragraph_alignment(p_el)
    style = ' style="text-align:%s;"' % align if align else ""
    style_name = _paragraph_style_name(p_el)
    if style_name.lower().startswith("heading"):
        m = re.search(r"(\d+)", style_name)
        level = int(m.group(1)) if m else 1
        level = max(1, min(6, level))
        return "<h%d%s>%s</h%d>" % (level, style, content, level)
    return "<p%s>%s</p>" % (style, content)


def _render_table(tbl_el, doc: Document) -> str:
    rows = []
    for tr in tbl_el.findall(qn("w:tr")):
        cells = []
        for tc in tr.findall(qn("w:tc")):
            cell_parts = []
            for p in tc.findall(qn("w:p")):
                cell_parts.append(_render_runs(p, doc))
            cells.append(
                '<td style="border:1px solid #ddd;padding:4px 8px;">%s</td>'
                % "".join(cell_parts)
            )
        rows.append("<tr>%s</tr>" % "".join(cells))
    return f'<table style="border-collapse:collapse;width:100%;">{"".join(rows)}</table>'


def parse_docx_to_html(data: bytes) -> str:
    """把 docx 二进制数据转换为 HTML 字符串。"""
    doc = Document(BytesIO(data))
    body = doc.element.body
    out: list[str] = []
    open_list: str | None = None

    for child in body.iterchildren():
        tag = child.tag
        if tag == qn("w:p"):
            list_type = _detect_list_type(child)
            if list_type:
                if open_list != list_type:
                    if open_list:
                        out.append("</%s>" % open_list)
                    out.append("<%s>" % list_type)
                    open_list = list_type
                out.append("<li>%s</li>" % _render_runs(child, doc))
            else:
                if open_list:
                    out.append("</%s>" % open_list)
                    open_list = None
                out.append(_render_paragraph_block(child, doc))
        elif tag == qn("w:tbl"):
            if open_list:
                out.append("</%s>" % open_list)
                open_list = None
            out.append(_render_table(child, doc))

    if open_list:
        out.append("</%s>" % open_list)

    html = "".join(out)
    return html or "<p></p>"