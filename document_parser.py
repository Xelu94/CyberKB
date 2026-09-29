import os
import io
from pathlib import Path


def parse_file(file_path: str, filename: str) -> str:
    """Extract text from PDF, ODT, DOCX, HTML or plain-text files."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext == ".odt":
        return _parse_odt(file_path)
    elif ext == ".docx":
        return _parse_docx(file_path)
    elif ext in (".html", ".htm"):
        return _parse_html(file_path)
    elif ext in (".txt", ".md", ".log"):
        return _parse_text(file_path)
    else:
        return _parse_text(file_path)


def _parse_pdf(path: str) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n\n".join(text_parts)
    except ImportError:
        return "[Error: pdfplumber not installed. Run: pip install pdfplumber]"
    except Exception as e:
        return f"[Error parsing PDF: {e}]"


def _parse_odt(path: str) -> str:
    try:
        from odf import text as odf_text, teletype
        from odf.opendocument import load as odf_load
        doc = odf_load(path)
        parts = []
        for para in doc.getElementsByType(odf_text.P):
            t = teletype.extractText(para)
            if t.strip():
                parts.append(t)
        return "\n\n".join(parts)
    except ImportError:
        return "[Error: odfpy not installed. Run: pip install odfpy]"
    except Exception as e:
        return f"[Error parsing ODT: {e}]"


def _parse_docx(path: str) -> str:
    """Un .docx es un ZIP con el texto en word/document.xml. Se lee con la
    librería estándar (zipfile + ElementTree), sin depender de python-docx:
    se recorre cada párrafo <w:p> y se concatenan sus <w:t>, respetando saltos
    de línea <w:br> y tabuladores <w:tab>."""
    try:
        import zipfile
        from xml.etree import ElementTree as ET
        W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        parrafos = []
        for p in root.iter(W + "p"):
            piezas = []
            for nodo in p.iter():
                tag = nodo.tag
                if tag == W + "t" and nodo.text:
                    piezas.append(nodo.text)
                elif tag == W + "tab":
                    piezas.append("\t")
                elif tag in (W + "br", W + "cr"):
                    piezas.append("\n")
            linea = "".join(piezas).strip()
            if linea:
                parrafos.append(linea)
        return "\n\n".join(parrafos)
    except Exception as e:
        return f"[Error parsing DOCX: {e}]"


def _parse_html(path: str) -> str:
    """Extrae el texto visible de un .html con el HTMLParser de la librería
    estándar: descarta <script>/<style> y mete saltos de línea en los bloques."""
    try:
        import re
        from html.parser import HTMLParser

        BLOQUES = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
                   "section", "article", "header", "footer", "ul", "ol", "table"}

        class _Extractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.trozos = []
                self._saltar = 0
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style"):
                    self._saltar += 1
                elif tag in BLOQUES:
                    self.trozos.append("\n")
            def handle_endtag(self, tag):
                if tag in ("script", "style") and self._saltar:
                    self._saltar -= 1
            def handle_data(self, data):
                if not self._saltar and data.strip():
                    self.trozos.append(data)

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        extractor = _Extractor()
        extractor.feed(html)
        texto = "".join(extractor.trozos)
        # Colapsa líneas en blanco de más para no inflar el recuento de caracteres.
        texto = re.sub(r"[ \t]+\n", "\n", texto)
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        return texto.strip()
    except Exception as e:
        return f"[Error parsing HTML: {e}]"


def _parse_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"
