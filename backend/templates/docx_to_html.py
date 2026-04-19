"""
Convierte Formato 4x1.docx a HTML.
Uso: python docx_to_html.py
"""
from docx import Document
from lxml import etree
import base64, os

DOCX_PATH = os.path.join(os.path.dirname(__file__), "Formato 4x1.docx")
HTML_PATH  = os.path.join(os.path.dirname(__file__), "Formato 4x1.html")

NS_WP  = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
NS_A   = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_W   = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS_WPS = 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
NS_R   = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def emu_to_px(v):
    return round(int(v) / 9525)

def parse_color(val):
    if val and val != "auto" and len(val) == 6:
        return f"#{val}"
    return None

def parse_txbx(txbx_el, images_b64):
    html = ""
    for p in txbx_el.findall(f'{{{NS_W}}}p'):
        ppr   = p.find(f'{{{NS_W}}}pPr')
        align = "left"
        p_styles = ["margin:2px 0", "line-height:1.3"]
        if ppr is not None:
            jc = ppr.find(f'{{{NS_W}}}jc')
            if jc is not None:
                val   = jc.get(f'{{{NS_W}}}val', 'left')
                align = {'center':'center','right':'right','both':'justify'}.get(val, 'left')
        p_styles.append(f"text-align:{align}")

        content = ""
        for r in p.findall(f'.//{{{NS_W}}}r'):
            rpr = r.find(f'{{{NS_W}}}rPr')

            # Imagen inline dentro del run
            for inline in r.findall(f'.//{{{NS_WP}}}inline'):
                blip = inline.find(f'.//{{{NS_A}}}blip')
                if blip is not None:
                    rid = blip.get(f'{{{NS_R}}}embed')
                    if rid and rid in images_b64:
                        ext_el = inline.find(f'{{{NS_WP}}}extent')
                        w = h = ""
                        if ext_el is not None:
                            w = f"width:{emu_to_px(ext_el.get('cx', 0))}px;"
                            h = f"height:{emu_to_px(ext_el.get('cy', 0))}px;"
                        content += (
                            f'<img src="{images_b64[rid]}" '
                            f'style="{w}{h}max-width:100%;display:block;margin:auto"/>'
                        )

            text_el = r.find(f'{{{NS_W}}}t')
            if text_el is None or not (text_el.text or "").strip():
                continue
            text   = (text_el.text or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            styles = []
            if rpr is not None:
                if rpr.find(f'{{{NS_W}}}b')  is not None: styles.append("font-weight:bold")
                if rpr.find(f'{{{NS_W}}}i')  is not None: styles.append("font-style:italic")
                if rpr.find(f'{{{NS_W}}}u')  is not None: styles.append("text-decoration:underline")
                sz = rpr.find(f'{{{NS_W}}}sz')
                if sz is not None:
                    styles.append(f"font-size:{int(sz.get(f'{{{NS_W}}}val', 24)) / 2}pt")
                color = rpr.find(f'{{{NS_W}}}color')
                if color is not None:
                    c = parse_color(color.get(f'{{{NS_W}}}val'))
                    if c: styles.append(f"color:{c}")
                font = rpr.find(f'{{{NS_W}}}rFonts')
                if font is not None:
                    ff = font.get(f'{{{NS_W}}}ascii') or font.get(f'{{{NS_W}}}hAnsi')
                    if ff: styles.append(f"font-family:'{ff}'")
            if styles:
                content += f"<span style='{';'.join(styles)}'>{text}</span>"
            else:
                content += text

        html += f"<p style='{';'.join(p_styles)}'>{content if content else '&nbsp;'}</p>\n"
    return html


def convert():
    doc = Document(DOCX_PATH)

    # Extraer imágenes embebidas
    images_b64 = {}
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            mime = rel.target_part.content_type
            b64  = base64.b64encode(rel.target_part.blob).decode()
            images_b64[rel.rId] = f"data:{mime};base64,{b64}"

    # Anchors: 0-3 = página 1, 4-7 = página 2. Canónico top-left = índice 3 y 7
    anchors = doc.element.body.findall(f'.//{{{NS_WP}}}anchor')

    def get_afiche(anchor):
        txbx   = anchor.find(f'.//{{{NS_WPS}}}txbx/{{{NS_W}}}txbxContent')
        extent = anchor.find(f'{{{NS_WP}}}extent')
        cx     = emu_to_px(extent.get('cx', 0))
        cy     = emu_to_px(extent.get('cy', 0))
        return parse_txbx(txbx, images_b64), cx, cy

    afiche1, cx_px, cy_px = get_afiche(anchors[3])
    afiche2, _,     _     = get_afiche(anchors[7])

    def page_html(afiche):
        return f"""  <div class="page">
    <div class="afiche">{afiche}</div>
    <div class="afiche">{afiche}</div>
    <div class="afiche">{afiche}</div>
    <div class="afiche">{afiche}</div>
  </div>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Formato 4x1</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #d0d0d0;
      font-family: Arial, sans-serif;
      padding: 24px;
    }}
    h1 {{
      text-align: center;
      font-size: 13pt;
      color: #444;
      margin-bottom: 16px;
    }}
    h2 {{
      text-align: center;
      font-size: 11pt;
      color: #666;
      margin: 0 auto 10px;
      width: 794px;
    }}
    .page {{
      width: 794px;
      height: 1123px;
      background: white;
      margin: 0 auto 8px;
      display: grid;
      grid-template-columns: {cx_px}px {cx_px}px;
      grid-template-rows: {cy_px}px {cy_px}px;
      border: 1px solid #999;
      box-shadow: 0 3px 10px rgba(0,0,0,0.25);
      overflow: hidden;
    }}
    .afiche {{
      width: {cx_px}px;
      height: {cy_px}px;
      border: 1px dashed #ccc;
      padding: 6px;
      overflow: hidden;
    }}
    .afiche p {{ word-break: break-word; }}
    .page-sep {{ margin-bottom: 32px; }}
  </style>
</head>
<body>
  <h1>Formato 4x1 — Vista previa</h1>
  <h2>Página 1</h2>
{page_html(afiche1)}
  <div class="page-sep"></div>
  <h2>Página 2</h2>
{page_html(afiche2)}
</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generado: {HTML_PATH}")


if __name__ == "__main__":
    convert()
