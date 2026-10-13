"""Builds issue 1 of the Nasar newsletter (sender: نسار, content partner: سرد).

Same delivery constraints as ../newsletter/build.py: tables, inline styles, bgcolor, data: images, pasted into Gmail
compose. Typography follows Nasar's DESIGN.md: Thmanyah Display / Text / Sans, ink on white «قصاصة» cards over the
cream board, readable coral (#B4423E) for small accents, mustard behind one phrase, no eyebrow above titles, no
coloured card borders. Output: issue-1.html.
"""
import base64, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "tests", "nasar")

INK, SOFT, CREAM, BOARD, WHITE, EDGE = "#111111", "#444444", "#F2EEE7", "#E9E4DA", "#FFFFFF", "#DDD6C9"
CORAL, MUSTARD = "#B4423E", "#DDBE63"
SYS = "system-ui,-apple-system,'SF Arabic','Segoe UI','Noto Sans Arabic',Tahoma,sans-serif"
DISPLAY = "'Thmanyah Serif Display'," + SYS
TEXT = "'Thmanyah Serif Text'," + SYS
SANS = "'Thmanyah Sans'," + SYS
WPM = 180
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9 .,:?'®\-]*[A-Za-z0-9?®]|[A-Za-z]")
TABLE = 'role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"'


def data_uri(name):
    mime = "image/png" if name.endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(HERE, name), "rb").read()).decode()


def img(name, alt, width=528, margin="0", radius=0):
    r = f"border-radius:{radius}px;" if radius else ""
    return (f'<img src="{data_uri(name)}" width="{width}" alt="{alt}" '
            f'style="display:block;width:100%;max-width:{width}px;height:auto;border:0;margin:{margin};{r}">')


HIGHLIGHT = {}  # anchor -> phrase to mark in the body (one per article)
SUBHEADS = {"قبل المقال": "s-before.png", "هيكل الحجة": "s-structure.png", "التفكيك": "s-analysis.png", "الوصول": "s-arrival.png"}


def ltr(text):
    parts = re.split(r"(<[^>]+>)", text)
    return "".join(p if p.startswith("<") else LATIN.sub(lambda m: f'<span dir="ltr">{m.group(0)}</span>', p) for p in parts)


def inline(md, bold_color=CORAL):
    s = html.escape(md, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", rf'<a href="\2" style="color:{CORAL};text-decoration:underline">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", rf'<b style="color:{bold_color};font-weight:700">\1</b>', s)
    parts = re.split(r'(<a [^>]+>.*?</a>)', s)
    return "".join(p if p.startswith("<a ") else ltr(p) for p in parts)


def prose(content, size=18, lh="2", margin="0 0 20px", color=INK, family=TEXT, justify=True):
    align = "text-align:justify;text-align-last:right" if justify else "text-align:right"
    return (f'<p style="margin:{margin};font-family:{family};font-size:{size}px;line-height:{lh};color:{color};{align}">'
            f'{content}</p>')


def marker(text):
    """Mustard behind one phrase, as Nasar's «خردليّ التظهير»."""
    return f'<span style="background-color:{MUSTARD};color:{INK};padding:1px 4px;border-radius:3px">{text}</span>'


def card(inner, bg=WHITE, border=True, pad="20px 24px", margin="8px 0 24px"):
    b = f"border:1px solid {EDGE};" if border else ""
    return (f'<table {TABLE} style="margin:{margin}"><tr><td bgcolor="{bg}" '
            f'style="background-color:{bg};{b}border-radius:12px;padding:{pad};text-align:right">{inner}</td></tr></table>')


def label(text, color=CORAL):
    return f'<div style="font-family:{SANS};font-size:13px;font-weight:700;color:{color};margin:0 0 8px">{text}</div>'


def divider():
    return (f'<table {TABLE} style="margin:34px 0"><tr>'
            f'<td style="border-top:1px solid {EDGE};font-size:0;line-height:0">&nbsp;</td>'
            f'<td width="56" align="center" style="width:56px"><img src="{data_uri("mark.png")}" width="26" height="26" alt="" '
            f'style="display:inline-block;width:26px;height:26px;border:0"></td>'
            f'<td style="border-top:1px solid {EDGE};font-size:0;line-height:0">&nbsp;</td></tr></table>')


def pull_quote(text):
    return (f'<table {TABLE} style="margin:10px 0 30px"><tr><td style="padding:6px 8px;text-align:center">'
            f'<div style="font-family:{DISPLAY};font-size:23px;line-height:1.7;color:{INK}">«{inline(text, INK)}»</div>'
            f'<div style="margin:12px auto 0;width:64px;border-top:2px solid {CORAL};font-size:0;line-height:0">&nbsp;</div>'
            f'</td></tr></table>')


def bullets(items):
    rows = "".join(
        f'<tr><td width="22" valign="top" style="width:22px;padding-top:2px;font-family:{TEXT};font-size:18px;color:{CORAL}">●</td>'
        f'<td style="padding:0 0 10px;font-family:{TEXT};font-size:18px;line-height:1.95;color:{INK};text-align:right">{inline(i)}</td></tr>'
        for i in items)
    return f'<table {TABLE} style="margin:0 0 20px">{rows}</table>'


def subhead(text):
    if text in SUBHEADS:
        return img(SUBHEADS[text], text, margin="30px 0 16px")
    return f'<h3 style="margin:30px 0 14px;font-family:{DISPLAY};font-size:22px;color:{INK};text-align:right">{text}</h3>'


def table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if not re.match(r"^\|?\s*-{2,}", l.strip())]
    head, *data = rows
    th = "".join(f'<td bgcolor="{BOARD}" style="background-color:{BOARD};padding:10px 10px;border:1px solid {EDGE};font-family:{SANS};font-size:13px;font-weight:700;color:{INK};text-align:right;vertical-align:top">{inline(c, INK)}</td>' for c in head)
    trs = ""
    for r in data:
        tds = "".join(
            f'<td style="padding:10px 10px;border:1px solid {EDGE};font-family:{TEXT};font-size:15px;line-height:1.8;color:{INK};text-align:right;vertical-align:top;{"font-weight:700;" if j == 0 else ""}">{inline(c, INK)}</td>'
            for j, c in enumerate(r))
        trs += f"<tr>{tds}</tr>"
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="margin:6px 0 24px;border-collapse:collapse">{"<tr>" + th + "</tr>"}{trs}</table>')


def body(md_text, pull=None, hl=None):
    """Renders a sard answer. pull = (after_prose_paragraph_number, sentence) places a pull quote."""
    blocks = [x.strip() for x in md_text.strip().split("\n\n") if x.strip()]
    out, n, closing = [], 0, False
    for i, x in enumerate(blocks):
        if i == 0:
            x = re.sub(r"^\*\*سطر البوصلة:\*\*\s*", "", x)
            out.append(prose(inline(x, INK), size=22, lh="1.75", margin="0 0 26px", family=DISPLAY, justify=False))
        elif x.startswith("### "):
            out.append(subhead(x[4:].strip()))
        elif x.startswith("|"):
            out.append(table(x.splitlines()))
        elif x.startswith("**الرسالة باختصار:**"):
            closing = True
            out.append(card(label("الرسالة باختصار")
                            + f'<div style="font-family:{DISPLAY};font-size:20px;line-height:2.05;color:{INK}">'
                              f'{marker(inline(x.split(":**", 1)[1].strip(), INK))}</div>', bg=CREAM, border=False))
        elif x.startswith("**لفتة من عندي:**"):
            out.append(card(label("لفتة من عندي")
                            + prose(inline(x.split(":**", 1)[1].strip()), size=17, lh="1.95", margin="0"),
                            bg=BOARD, border=False))
        elif all(line.startswith("- ") for line in x.splitlines()):
            out.append(bullets([line[2:] for line in x.splitlines()]))
        elif closing or (x.startswith("*") and x.endswith("*") and not x.startswith("**")):
            out.append(prose(inline(x.strip("*")), size=14, lh="1.9", margin="6px 0 6px", color=SOFT, family=SANS, justify=False))
        else:
            # A paragraph whose text ends with a colon introduces the table or list after it: keep it tight.
            para = inline(x)
            if hl and hl in para:
                para = para.replace(hl, marker(hl), 1)
                hl = None
            out.append(prose(para))
            n += 1
            if pull and n == pull[0]:
                out.append(img(pull[1], pull[2], margin="6px 0 26px"))
    return "\n".join(out)


def minutes(md_text):
    m = max(1, round(len(md_text.split()) / WPM))
    return "دقيقة واحدة" if m == 1 else "دقيقتان" if m == 2 else f"{m} دقائق" if m <= 10 else f"{m} دقيقة"


def article(anchor, title, section, url, md_text, pull):
    meta = (f'<div style="font-family:{SANS};font-size:13px;line-height:1.8;color:{SOFT};margin:0 0 26px;text-align:right">'
            f'من قسم «{section}» · {minutes(md_text)} · '
            f'<a href="{url}" style="color:{CORAL};text-decoration:underline">المقال الأصلي في نسار</a></div>')
    head = img(f"t-{anchor}.png", title, margin="0 0 8px")
    return head + meta + body(md_text, pull, HIGHLIGHT.get(anchor))


ARTICLES = [
    dict(anchor="change", title="هل تتغير الشخصية؟", section="قراءات تسبق النتيجة",
         url="https://www.nasar.me/articles/can-personality-change", src="can-personality-change.sard.md"),
    dict(anchor="restorative", title="المصلح أم المتقن؟", section="كليفتون للقوى",
         url="https://www.nasar.me/articles/clifton/compare/restorative-vs-maximizer",
         src="restorative-vs-maximizer.sard.md"),
]
PULLS = {}  # anchor -> (after_paragraph_index, sentence quoted from the sard text)
exec(open(os.path.join(HERE, "pulls.py"), encoding="utf-8").read()) if os.path.exists(os.path.join(HERE, "pulls.py")) else None
for a in ARTICLES:
    a["md"] = open(os.path.join(SRC, a["src"]), encoding="utf-8").read()

INTRO = [
    "أهلًا بك في العدد الأول من نشرة نسار. في كل عدد نختار من مقالات نسار ما يستحق أن يُقرأ بتمهّل، ونقدّمه مشروحًا "
    "بالشراكة مع سرد: من الأساس إلى المعنى، بلغة يفهمها القارئ دون معجم، مع رابط المقال الأصلي لمن أراد التوسع.",
    "ويجمع مقالَي هذا العدد سؤال واحد: " + marker("ماذا يبقى منك، وماذا يتغير؟") + " الأول من «قراءات تسبق النتيجة» "
    "يعرض ما تقوله الدراسات الطويلة عن تغيّر الشخصية مع العمر وبالقصد، والثاني من «كليفتون للقوى» يضع سمتين "
    "متجاورتين – المصلح والمتقن – ويسأل: من أين تبدأ حين تريد أن تجعل العمل أفضل؟",
]


def toc_row(a, last=False):
    border = "" if last else f"border-bottom:1px solid {EDGE};"
    return (f'<tr><td style="padding:14px 0;{border}text-align:right">'
            f'<div style="font-family:{DISPLAY};font-size:20px;line-height:1.55;color:{INK}">{a["title"]}</div>'
            f'<div style="font-family:{SANS};font-size:12px;color:{SOFT};margin-top:2px">{a["section"]} · {minutes(a["md"])}</div>'
            f'</td></tr>')


partner = (f'<div style="font-family:{SANS};font-size:11px;color:{SOFT};margin:0 0 8px;text-align:right">إعلان · شريك المحتوى</div>'
           f'<a href="https://github.com/Ajarallah/sard" style="display:block;text-decoration:none">'
           + img("sard-partner.png", "سرد، شريك المحتوى: من الأساس إلى المعنى") + '</a>')

closing = ('<a href="https://www.nasar.me" style="display:block;text-decoration:none">'
           + img("cta.jpg", "نسار: هل أجريت اختبار شخصية بالإنجليزية ثم شعرت أن نتيجته لا تشبهك؟ هل تعرف عن نفسك أكثر "
                 "مما تستطيع أن تقوله؟ هل تريد أن تفهم لماذا تشدّك أعمال وتنفر من أخرى؟ إحساسك بنفسك صحيح، وما ينقصه إلا "
                 "الكلمات. أربعة مقاييس وقراءة واحدة تجمعها. ابدأ · nasar.me") + '</a>')

page = f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>نشرة نسار · العدد 1</title></head>
<body style="margin:0;padding:0" bgcolor="{WHITE}">
<table {TABLE} bgcolor="{WHITE}" style="background-color:{WHITE}" dir="rtl">
<tr><td align="center" style="padding:16px 8px 36px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="{WHITE}" style="width:600px;max-width:100%;background-color:{WHITE};border:1px solid {EDGE};border-radius:18px" dir="rtl">

<tr><td style="padding:0;font-size:0;line-height:0">
<img src="{data_uri("header.png")}" width="600" alt="نسار · النشرة · العدد 1 · هل تتغير الشخصية؟ · ومعه: المصلح أم المتقن؟" style="display:block;width:100%;max-width:600px;height:auto;border:0;border-radius:18px 18px 0 0"></td></tr>

<tr><td style="padding:34px 36px 10px;text-align:right">
{img("t-intro.png", "افتتاحية العدد", margin="0 0 12px")}
{"".join(prose(t, margin="0 0 16px") for t in INTRO)}

<div style="font-family:{SANS};font-size:13px;font-weight:700;color:{SOFT};margin:22px 0 2px">في هذا العدد</div>
<table {TABLE} style="border-top:1px solid {EDGE}">
{toc_row(ARTICLES[0])}
{toc_row(ARTICLES[1], last=True)}
</table>
{divider()}
{article(**{k: ARTICLES[0][k] for k in ("anchor", "title", "section", "url")}, md_text=ARTICLES[0]["md"], pull=PULLS.get("change"))}
{divider()}
{partner}
{divider()}
{article(**{k: ARTICLES[1][k] for k in ("anchor", "title", "section", "url")}, md_text=ARTICLES[1]["md"], pull=PULLS.get("restorative"))}
</td></tr>

<tr><td style="padding:18px 36px 36px">{closing}</td></tr>
</table>

<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%" dir="rtl"><tr>
<td style="padding:20px 14px 0;text-align:right;font-family:{SANS};font-size:12px;line-height:1.9;color:{SOFT}">
<b style="color:{INK}">نسار · نسج ومسار.</b> المقالات الأصلية في نسار، والشروح في هذا العدد من سرد.<br>
وصلتك هذه الرسالة لأنك مشترك في نشرة نسار. إن أعجبتك فأرسلها إلى صديق.<br>
<a href="#" style="color:{SOFT};text-decoration:underline">إلغاء الاشتراك</a> · <a href="#" style="color:{SOFT};text-decoration:underline">عرض في المتصفح</a>
</td></tr></table>

</td></tr></table>
</body></html>"""

open(os.path.join(HERE, "issue-1.html"), "w", encoding="utf-8").write(page)
print("issue-1.html", len(page.encode()), "bytes")
