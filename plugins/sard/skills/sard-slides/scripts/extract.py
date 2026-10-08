#!/usr/bin/env python3
"""Inventory a slide deck (PPTX or PDF) for sard-slides.

Per slide: text, speaker notes, comments (legacy + modern, with replies),
PDF annotations, and flags for ink/images that must be read visually.
Renders every slide to PNG when possible (PDF: PyMuPDF; PPTX: LibreOffice).

usage: extract.py DECK [-o OUTDIR]      |      extract.py --self-check
"""
import json, os, posixpath, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
NOTE_SKIP = {"sldNum", "sldImg", "hdr", "ftr", "dt"}
MARKUP = {"Highlight", "Underline", "StrikeOut", "Squiggly"}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def find_all(node, name):
    return [e for e in node.iter() if local(e.tag) == name]


def paras(node):
    lines = ("".join(t.text or "" for t in find_all(p, "t")).strip() for p in find_all(node, "p"))
    return [l for l in lines if l]


class Pkg:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self.names = set(self.z.namelist())

    def xml(self, name):
        return ET.fromstring(self.z.read(name)) if name in self.names else None

    def rels(self, part):
        d, f = posixpath.split(part)
        root = self.xml(posixpath.join(d, "_rels", f + ".rels"))
        out = []
        for r in [] if root is None else root:
            t = r.get("Target", "")
            if r.get("TargetMode") == "External":
                continue
            t = t.lstrip("/") if t.startswith("/") else posixpath.normpath(posixpath.join(d, t))
            out.append((r.get("Id"), r.get("Type", ""), t))
        return out


def notes_text(root):
    out = []
    for sp in find_all(root, "sp"):
        ph = find_all(sp, "ph")
        if not (ph and ph[0].get("type") in NOTE_SKIP):
            out += paras(sp)
    return out


def comments(root, authors):
    out = []
    for cm in root.iter():
        if local(cm.tag) not in ("cm", "reply"):
            continue
        body = next((c for c in cm if local(c.tag) in ("text", "txBody")), None)
        if body is None:
            continue
        text = (body.text or "").strip() if local(body.tag) == "text" else "\n".join(paras(body))
        out.append({"author": authors.get(cm.get("authorId"), "?"), "text": text, "reply": local(cm.tag) == "reply"})
    return out


def extract_pptx(path):
    pkg = Pkg(path)
    targets = {rid: t for rid, _, t in pkg.rels("ppt/presentation.xml")}
    order = [targets[s.get(R_ID)] for s in find_all(pkg.xml("ppt/presentation.xml"), "sldId")]
    authors = {}
    for part in ("ppt/commentAuthors.xml", "ppt/authors.xml"):
        root = pkg.xml(part)
        for a in [] if root is None else root.iter():
            if local(a.tag) in ("cmAuthor", "author"):
                authors[a.get("id")] = a.get("name")
    slides = []
    for n, part in enumerate(order, 1):
        root = pkg.xml(part)
        s = {"n": n, "text": paras(root), "notes": [], "comments": [], "annotations": [],
             "ink": bool(find_all(root, "contentPart")), "has_images": bool(find_all(root, "pic")),
             "hidden": root.get("show") == "0", "image": None}
        for _, typ, target in pkg.rels(part):
            if typ.endswith("/notesSlide"):
                s["notes"] = notes_text(pkg.xml(target))
            elif "comments/" in target:
                s["comments"] += comments(pkg.xml(target), authors)
            elif "/ink/" in target:
                s["ink"] = True
        slides.append(s)
    return slides


def extract_pdf(path):
    slides = []
    for n, page in enumerate(fitz.open(path), 1):
        text = page.get_text().strip()
        anns, ink = [], False
        for a in page.annots():
            kind = a.type[1]
            ink |= kind == "Ink"
            body = (a.info.get("content") or "").strip()
            marked = page.get_textbox(a.rect).strip() if kind in MARKUP else ""
            if body or marked:
                anns.append({"type": kind, "text": body, "marked": marked})
        imgs = bool(page.get_images())
        slides.append({"n": n, "text": [l.strip() for l in text.splitlines() if l.strip()], "notes": [],
                       "comments": [], "annotations": anns, "ink": ink, "has_images": imgs,
                       "scanned": not text and imgs, "image": None})
    return slides


def pptx_to_pdf(path, outdir):
    mac = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    soffice = shutil.which("soffice") or shutil.which("libreoffice") or (mac if os.path.exists(mac) else None)
    if not soffice:
        return None
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, path],
                   check=True, capture_output=True, timeout=600)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + ".pdf")
    return pdf if os.path.exists(pdf) else None


def render(pdf, imgdir, dpi=150):
    os.makedirs(imgdir, exist_ok=True)
    paths = []
    for n, page in enumerate(fitz.open(pdf), 1):
        p = os.path.join(imgdir, f"slide-{n:03d}.png")
        page.get_pixmap(dpi=dpi).save(p)
        paths.append(p)
    return paths


def run(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    warnings, pdf = [], None
    ext = path.lower().rsplit(".", 1)[-1]
    if ext == "pptx":
        slides = extract_pptx(path)
        pdf = pptx_to_pdf(path, outdir)
        if not pdf:
            warnings.append("LibreOffice not found, slides not rendered. Export the deck to PDF "
                            "(PowerPoint/Keynote: File > Export > PDF) and run this on the PDF too, "
                            "to read handwriting and diagrams. Notes and comments above are complete.")
    elif ext == "pdf":
        if not fitz:
            sys.exit("PyMuPDF missing: pip install pymupdf")
        slides, pdf = extract_pdf(path), path
    else:
        sys.exit("unsupported file: give .pptx or .pdf (for images, read them directly)")
    if pdf and not fitz:
        warnings.append("PyMuPDF missing (pip install pymupdf), slides not rendered.")
    elif pdf:
        imgs = render(pdf, os.path.join(outdir, "images"))
        if len(imgs) == len(slides):
            for s, p in zip(slides, imgs):
                s["image"] = os.path.relpath(p, outdir)
        else:
            warnings.append(f"rendered {len(imgs)} pages for {len(slides)} slides (hidden slides?), "
                            "images are not mapped 1:1, match them by content.")
    inv = {"source": os.path.abspath(path), "slides": slides, "warnings": warnings}
    with open(os.path.join(outdir, "inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=1)
    count = lambda k: sum(1 for s in slides if s.get(k))
    print(f"{len(slides)} slides | notes {count('notes')} | comments {count('comments')} | "
          f"annotations {count('annotations')} | ink {count('ink')} | images {count('has_images')} | "
          f"rendered {count('image')}")
    for w in warnings:
        print("WARNING:", w)
    print("inventory:", os.path.join(outdir, "inventory.json"))
    return inv


def self_check():
    ns = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
    p188 = 'xmlns:p188="http://schemas.microsoft.com/office/powerpoint/2018/8/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"

    def rels(*items):
        body = "".join(f'<Relationship Id="{i}" Type="{t}" Target="{g}"/>' for i, t, g in items)
        return f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{body}</Relationships>'

    def sp(text, ph=""):
        ph = f'<p:nvSpPr><p:nvPr><p:ph type="{ph}"/></p:nvPr></p:nvSpPr>' if ph else ""
        return f"<p:sp>{ph}<p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>"

    def run_text(t):
        return f"<p188:txBody><a:p><a:r><a:t>{t}</a:t></a:r></a:p></p188:txBody>"

    files = {
        "ppt/presentation.xml": f'<p:presentation {ns}><p:sldIdLst><p:sldId id="256" r:id="rId2"/><p:sldId id="257" r:id="rId1"/></p:sldIdLst></p:presentation>',
        "ppt/_rels/presentation.xml.rels": rels(("rId1", T + "slide", "slides/slide1.xml"), ("rId2", T + "slide", "slides/slide2.xml")),
        "ppt/slides/slide2.xml": f'<p:sld {ns}><p:cSld><p:spTree>{sp("مقدمة")}{sp("Intro")}</p:spTree></p:cSld></p:sld>',
        "ppt/slides/_rels/slide2.xml.rels": rels(("rId1", T + "notesSlide", "../notesSlides/notesSlide2.xml"), ("rId2", T + "comments", "../comments/comment1.xml")),
        "ppt/notesSlides/notesSlide2.xml": f'<p:notes {ns}><p:cSld><p:spTree>{sp("1", "sldNum")}{sp("ركّز هنا", "body")}</p:spTree></p:cSld></p:notes>',
        "ppt/comments/comment1.xml": f'<p:cmLst {ns}><p:cm authorId="0" idx="1"><p:pos x="0" y="0"/><p:text>سؤال الطالب</p:text></p:cm></p:cmLst>',
        "ppt/commentAuthors.xml": f'<p:cmAuthorLst {ns}><p:cmAuthor id="0" name="Ali"/></p:cmAuthorLst>',
        "ppt/slides/slide1.xml": f'<p:sld {ns} show="0"><p:cSld><p:spTree>{sp("Second")}<p:pic/><p14:contentPart xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" r:id="rId9"/></p:spTree></p:cSld></p:sld>',
        "ppt/slides/_rels/slide1.xml.rels": rels(("rId1", "http://schemas.microsoft.com/office/2018/10/relationships/comments", "../comments/modernComment_1.xml")),
        "ppt/comments/modernComment_1.xml": f'<p188:cmLst {p188}><p188:cm id="1" authorId="{{A}}">{run_text("Why?")}<p188:replyLst><p188:reply id="2" authorId="{{A}}">{run_text("Because")}</p188:reply></p188:replyLst></p188:cm></p188:cmLst>',
        "ppt/authors.xml": f'<p188:authorLst {p188}><p188:author id="{{A}}" name="Dr. X"/></p188:authorLst>',
    }
    with tempfile.TemporaryDirectory() as tmp:
        deck = os.path.join(tmp, "t.pptx")
        with zipfile.ZipFile(deck, "w") as z:
            for name, data in files.items():
                z.writestr(name, data)
        s = extract_pptx(deck)
        assert [x["text"] for x in s] == [["مقدمة", "Intro"], ["Second"]], s  # presentation order, not file order
        assert s[0]["notes"] == ["ركّز هنا"], s[0]["notes"]  # slide-number placeholder skipped
        assert s[0]["comments"] == [{"author": "Ali", "text": "سؤال الطالب", "reply": False}], s[0]["comments"]
        assert [(c["author"], c["text"], c["reply"]) for c in s[1]["comments"]] == [("Dr. X", "Why?", False), ("Dr. X", "Because", True)]
        assert s[1]["ink"] and s[1]["has_images"] and s[1]["hidden"] and not s[0]["ink"]
        inv = run(deck, os.path.join(tmp, "out"))
        assert os.path.exists(os.path.join(tmp, "out", "inventory.json")) and len(inv["slides"]) == 2
        if fitz:
            pdf = os.path.join(tmp, "t.pdf")
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), "Hello slide")
            page.add_text_annot((100, 100), "note here")
            page.add_ink_annot([[(10, 10), (20, 20), (30, 10)]])
            page.add_highlight_annot(page.search_for("Hello")[0])
            doc.save(pdf)
            inv = run(pdf, os.path.join(tmp, "pdf"))
            p = inv["slides"][0]
            assert p["text"] == ["Hello slide"] and p["ink"] and p["image"], p
            assert {"type": "Text", "text": "note here", "marked": ""} in p["annotations"], p["annotations"]
            assert any(a["type"] == "Highlight" and "Hello" in a["marked"] for a in p["annotations"]), p["annotations"]
        else:
            print("PyMuPDF not installed: PDF checks skipped")
    print("self-check OK")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--self-check"]:
        self_check()
    elif len(args) in (1, 3) and (len(args) == 1 or args[1] == "-o"):
        deck = args[0]
        run(deck, args[2] if len(args) == 3 else os.path.splitext(deck)[0] + "-sard")
    else:
        sys.exit(__doc__)
