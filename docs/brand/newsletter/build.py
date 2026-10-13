"""Builds issue 1 of the سرد newsletter.

Gmail drops <style> blocks, classes, the `background` shorthand and (through the API) every <img>, so the issue is
built for the Gmail compose window: tables, inline styles, `bgcolor`, and images as data URIs that Gmail turns into
inline attachments when the page is copied and pasted into a new message. Output: issue-1.html (open, copy, paste).
"""
import base64, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(HERE, "..", "..", "tests")

INK, PAPER, FRAME, TINT, RUBRIC, MUTED, RULE = "#1E1A16", "#F6F1E7", "#E9E1D2", "#ECE3D3", "#A33B2B", "#6F675E", "#DED4C2"
DISPLAY = "'Thmanyah Serif Display','Geeza Pro',serif"
TEXT = "'Thmanyah Serif Text','Geeza Pro',serif"
SANS = "'Thmanyah Sans',Tahoma,sans-serif"
WPM = 180
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9 .,:?'\-]*[A-Za-z0-9?]|[A-Za-z]")


def data_uri(name, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(HERE, name), "rb").read()).decode()


def ltr(text):
    parts = re.split(r"(<[^>]+>)", text)
    return "".join(p if p.startswith("<") else LATIN.sub(lambda m: f'<span dir="ltr">{m.group(0)}</span>', p) for p in parts)


def inline(md):
    s = html.escape(md, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", rf'<a href="\2" dir="ltr" style="color:{RUBRIC};text-decoration:underline">\1</a>', s)
    # Bold connectors are rubricated, like the red «قال» and «فإن قيل» of the manuscripts.
    s = re.sub(r"\*\*(.+?)\*\*", rf'<b style="color:{RUBRIC};font-weight:700">\1</b>', s)
    parts = re.split(r'(<a [^>]+>.*?</a>)', s)
    return "".join(p if p.startswith("<a ") else ltr(p) for p in parts)


def p(text, size=18, color=INK, family=TEXT, margin="0 0 18px", lh="2"):
    return f'<p style="margin:{margin};font-family:{family};font-size:{size}px;line-height:{lh};color:{color};text-align:right">{text}</p>'


def box(label, content, size=18):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 22px">'
            f'<tr><td bgcolor="{TINT}" style="background-color:{TINT};border-radius:12px;padding:18px 22px;text-align:right">'
            f'<div style="font-family:{SANS};font-size:14px;font-weight:700;color:{RUBRIC};margin:0 0 6px">{label}</div>'
            f'<div style="font-family:{TEXT};font-size:{size}px;line-height:1.95;color:{INK}">{content}</div></td></tr></table>')


def aside(label, content):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 22px">'
            f'<tr><td style="border-right:3px solid {RUBRIC};padding:2px 18px 2px 0;text-align:right">'
            f'<div style="font-family:{SANS};font-size:14px;font-weight:700;color:{RUBRIC};margin:0 0 6px">{label}</div>'
            f'<div style="font-family:{TEXT};font-size:17px;line-height:1.95;color:{INK}">{content}</div></td></tr></table>')


def body(md_text):
    paras = [x.strip() for x in md_text.strip().split("\n\n") if x.strip()]
    out = []
    for i, x in enumerate(paras):
        if i == 0:
            out.append(p(inline(x), size=21, family=DISPLAY, margin="0 0 22px", lh="1.8"))
        elif x.startswith("**الرسالة باختصار:**"):
            out.append(box("الرسالة باختصار", inline(x.split(":**", 1)[1].strip())))
        elif x.startswith("**لفتة من عندي:**"):
            out.append(aside("لفتة من عندي", inline(x.split(":**", 1)[1].strip())))
        elif i == len(paras) - 1 and not x.startswith("**"):
            out.append(p(inline(x), size=14, color=MUTED, family=SANS, margin="4px 0 0", lh="1.9"))
        else:
            out.append(p(inline(x)))
    return "\n".join(out)


def minutes(md_text):
    m = max(1, round(len(md_text.split()) / WPM))
    return "دقيقة واحدة" if m == 1 else "دقيقتان" if m == 2 else f"{m} دقائق" if m <= 10 else f"{m} دقيقة"


def divider():
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:30px 0"><tr>'
            f'<td style="border-top:1px solid {RULE};font-size:0;line-height:0">&nbsp;</td>'
            f'<td width="36" align="center" style="width:36px;font-size:0;line-height:0">'
            f'<span style="display:inline-block;width:10px;height:10px;border:2px solid {RUBRIC};border-radius:50%"></span></td>'
            f'<td style="border-top:1px solid {RULE};font-size:0;line-height:0">&nbsp;</td></tr></table>')


def article(kicker, title, meta, md_text):
    return (f'<div style="font-family:{SANS};font-size:13px;font-weight:700;color:{RUBRIC};margin:0 0 8px;text-align:right">{kicker}</div>'
            f'<h2 style="margin:0 0 8px;font-family:{DISPLAY};font-size:26px;line-height:1.5;font-weight:700;color:{INK};text-align:right">{title}</h2>'
            f'<div style="font-family:{SANS};font-size:13px;color:{MUTED};margin:0 0 24px;text-align:right">{meta}</div>'
            + body(md_text))


ik = open(os.path.join(TESTS, "ibn-khaldun", "v3.7.md"), encoding="utf-8").read()
im = open(os.path.join(TESTS, "isomorphic-mimicry", "v3.7.md"), encoding="utf-8").read()
T1 = "كيف عرف ابن خلدون أن الظلم يهدم الدولة الظالمة؟"
T2 = "المحاكاة الشكلية: أن تشبه الناجحين ولا تعمل"

ABOUT = ("<b style=\"color:" + RUBRIC + "\">سرد</b> نشرة أسبوعية تأخذ نصًا صعبًا – فصلًا من كتاب تراثي، أو مفهومًا من علم حديث – "
         "وتشرحه كما يشرحه لك من يجلس معك: تبدأ من الأساس الذي لا يُفهم النص إلا به، ثم تمضي خطوة خطوة، كل فكرة "
         "تمسك بالتي بعدها، حتى تصل إلى المعنى في جملة واحدة. نكتب بلغة قارئ اليوم، ونفكّ كل لفظ قديم أو مصطلح في موضعه، "
         "وننسب كلام المؤلف إليه، ونفصل عنه ما نستنبطه نحن.")
NOTE = ("في هذا العدد فصل من مقدمة ابن خلدون يشرح لماذا يرتد الظلم على الدولة التي تمارسه، ومفهوم من اقتصاد التنمية "
        "يفسّر كيف تبدو مؤسسة ناجحة وهي لا تؤدي عملها. وإن قرأتهما معًا ستجد بينهما خيطًا واحدًا: كلاهما عن دولة تهدم – "
        "من حيث لا تشعر – ما تقوم عليه.")


def toc_row(kicker, title, mins, last=False):
    border = "" if last else f"border-bottom:1px solid {RULE};"
    return (f'<tr><td style="padding:12px 0;{border}text-align:right">'
            f'<div style="font-family:{SANS};font-size:12px;font-weight:700;color:{RUBRIC}">{kicker}</div>'
            f'<div style="font-family:{DISPLAY};font-size:19px;line-height:1.6;color:{INK}">{title}'
            f'<span style="font-family:{SANS};font-size:12px;color:{MUTED}"> · {mins}</span></div></td></tr>')


ad = (f'<div style="font-family:{SANS};font-size:11px;color:{MUTED};margin:0 0 8px;text-align:right">إعلان · شريك المحتوى</div>'
      f'<a href="https://www.nasar.me" style="display:block;text-decoration:none">'
      f'<img src="{data_uri("nasar-ad.jpg", "image/jpeg")}" width="528" alt="نسار: إحساسك بنفسك صحيح، وما ينقصه إلا الكلمات · nasar.me" '
      f'style="display:block;width:100%;max-width:528px;height:auto;border:0;border-radius:12px"></a>')

page = f'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>سرد · العدد 1</title></head>
<body style="margin:0;padding:0" bgcolor="{FRAME}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{FRAME}" style="background-color:{FRAME}" dir="rtl">
<tr><td align="center" style="padding:24px 10px 36px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAPER}" style="width:600px;max-width:100%;background-color:{PAPER};border-radius:16px" dir="rtl">

<tr><td style="padding:0;font-size:0;line-height:0">
<img src="{data_uri("header.png", "image/png")}" width="600" alt="سرد · العدد 1 · {T1}" style="display:block;width:100%;max-width:600px;height:auto;border:0;border-radius:16px 16px 0 0"></td></tr>

<tr><td style="padding:30px 36px 8px;text-align:right">
{box("ما سرد؟", ABOUT, size=17)}
{p("أهلًا بك في العدد الأول.", margin="0 0 10px")}
{p(NOTE, margin="0 0 22px")}
<div style="font-family:{SANS};font-size:13px;font-weight:700;color:{MUTED};margin:0 0 2px;text-align:right">في هذا العدد</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {RULE}">
{toc_row("فصل الأسبوع · مقدمة ابن خلدون", T1, minutes(ik))}
{toc_row("مفهوم الأسبوع · اقتصاد التنمية", T2, minutes(im), last=True)}
</table>
{divider()}
{article("فصل الأسبوع · مقدمة ابن خلدون", T1, "مدة القراءة: " + minutes(ik) + " · فصل «الظلم مؤذن بخراب العمران»", ik)}
{divider()}
{ad}
{divider()}
{article("مفهوم الأسبوع · اقتصاد التنمية", T2, "مدة القراءة: " + minutes(im), im)}
</td></tr>

<tr><td style="padding:14px 36px 32px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td bgcolor="{INK}" style="background-color:{INK};border-radius:14px;padding:24px 26px;text-align:right">
<div style="font-family:{DISPLAY};font-size:22px;line-height:1.5;color:{PAPER};margin:0 0 6px">ما فهمت؟</div>
<div style="font-family:{TEXT};font-size:16px;line-height:1.9;color:{PAPER}">أرسل لنا فصلًا أو مفهومًا لم يتضح لك بالرد على هذه الرسالة، ونسرده لك من الأساس في عدد قادم.</div>
</td></tr></table>
</td></tr>
</table>

<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%" dir="rtl"><tr>
<td style="padding:20px 12px 0;text-align:right;font-family:{SANS};font-size:12px;line-height:1.9;color:{MUTED}">
<b style="color:{INK}">لماذا «سرد»؟</b> السرد في أصل اللغة نسج الدروع: حلقة تدخل في حلقة. وكذلك نشرح؛ كل فكرة تمسك بالتي بعدها حتى المعنى.<br>
وصلتك هذه الرسالة لأنك مشترك في نشرة سرد. إن أعجبتك فأرسلها إلى من يقرأ معك.<br>
<a href="#" style="color:{MUTED};text-decoration:underline">إلغاء الاشتراك</a> · <a href="#" style="color:{MUTED};text-decoration:underline">عرض في المتصفح</a>
</td></tr></table>

</td></tr></table>
</body></html>'''

open(os.path.join(HERE, "issue-1.html"), "w", encoding="utf-8").write(page)
print("issue-1.html", len(page.encode()), "bytes")
