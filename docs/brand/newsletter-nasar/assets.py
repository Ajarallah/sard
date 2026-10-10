"""Image blocks for the Nasar-sent newsletter, issue 1, rendered at 2x with the Thmanyah fonts in headless Chrome.

Gmail cannot load web fonts, so everything that carries the identity (header, titles, subheads, pull quotes, the
partner card, the closing panel) is drawn here with Thmanyah's own features: the tatweel kashida on the issue title,
the `swsh`/`salt` tail on the last eligible word (as Nasar's withTail does), the coral hand-drawn line, and the mustard
marker behind one phrase. Body text stays live text in the email.
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INK, SOFT, CREAM, CORAL, CORAL_INK, MUSTARD = "#111111", "#444444", "#F2EEE7", "#E56A67", "#B4423E", "#DDBE63"
TAIL = "font-feature-settings:'swsh' 1,'salt' 1"
WAVE = ('<svg viewBox="0 0 120 10" fill="none" preserveAspectRatio="none" style="display:block;width:{w}px;height:16px">'
        '<path d="M2 6 C 22 2, 44 9, 62 5 C 80 1, 102 8, 118 4" stroke="#E56A67" stroke-width="3" stroke-linecap="round"/></svg>')
MARK = ('<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px;display:block">'
        '<path d="M3.2 16.6 L12.4 16.6 C17.9 16.6, 20.1 13.5, 20.1 8.4" stroke="{ink}" stroke-width="2.8" stroke-linecap="round"/>'
        '<circle cx="17.3" cy="5.4" r="2" fill="{dot}"/></svg>')
PAGE = """<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}html,body{width:%dpx;overflow:hidden;background:%s}%s</style></head>
<body><div id="r">%s</div></body></html>"""
MARKER = f"background:{MUSTARD};color:{INK};padding:0 .18em;border-radius:.12em;box-decoration-break:clone;-webkit-box-decoration-break:clone"


def render(name, width, body, css="", bg="#FFFFFF", height=None, fmt="png"):
    """Renders body at a fixed width; height is measured from the content unless given."""
    page = os.path.join(HERE, f".{name}.html")
    open(page, "w", encoding="utf-8").write(PAGE % (width, bg, css, body))
    if height is None:
        import re
        open(page, "w", encoding="utf-8").write((PAGE % (width, bg, css, body)).replace(
            "</body>", "<script>document.title=document.getElementById('r').getBoundingClientRect().height</script></body>"))
        out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--dump-dom", f"--window-size={width},4000",
                              "file://" + page], capture_output=True, text=True).stdout
        height = int(float(re.search(r"<title>([\d.]+)</title>", out).group(1))) + 2
        open(page, "w", encoding="utf-8").write(PAGE % (width, bg, css, body))
    target = os.path.join(HERE, f"{name}.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={width},{height}",
                    f"--screenshot={target}", "file://" + page], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(page)
    if fmt == "jpg":
        subprocess.run(["magick", target, "-strip", "-quality", "86", target[:-4] + ".jpg"], check=True)
        os.remove(target)
    else:
        subprocess.run(["magick", target, "-strip", "-colors", "96", "PNG8:" + target], check=True)
    return height


# Header: the top of the white card. Cream band, mustard block, mark + wordmark, the issue title with its kashidas.
render("header", 1200, f"""
<div style="position:relative;height:500px;background:{CREAM}">
 <div style="position:absolute;left:0;top:0;width:110px;height:100%;background:{MUSTARD}"></div>
 <div style="position:absolute;inset:0;padding:48px 64px 44px 170px;display:flex;flex-direction:column;justify-content:space-between">
  <div style="display:flex;align-items:center;justify-content:space-between">
   <div style="display:flex;align-items:center;gap:14px">{MARK.format(s=58, ink=INK, dot=CORAL_INK)}
    <span style="font:700 56px/1 'Thmanyah Serif Display';color:{INK}">نســار</span></div>
   <div style="font:500 21px/1.5 'Thmanyah Sans';color:{SOFT};text-align:left">النشرة · العدد 1<br>السبت 10 أكتوبر 2026</div>
  </div>
  <div>
   <div style="font:700 86px/1.3 'Thmanyah Serif Display';color:{INK}">هـــل تتغير الشخصيــة؟</div>
   <div style="margin:4px 0 0 0;padding-right:330px">{WAVE.format(w=300)}</div>
  </div>
  <div style="font:500 22px/1.4 'Thmanyah Sans';color:{SOFT}">ومعه: المصلح أم المتقن؟ · الشروح بالشراكة مع
   <b style="font:700 26px 'Thmanyah Serif Display';color:{INK}">سرد</b></div>
 </div>
</div>""", bg=CREAM, height=500)


def title(name, html_text, size=60, wave=320):
    render(name, 1056, f"""<div style="padding:4px 0 6px">
<div style="font:700 {size}px/1.45 'Thmanyah Serif Display';color:{INK}">{html_text}</div>
<div style="margin-top:2px">{WAVE.format(w=wave)}</div></div>""")


def subhead(name, text):
    render(name, 1056, f"""<div style="padding:6px 0 4px;display:flex;align-items:center;gap:18px">
<span style="font:700 46px/1.5 'Thmanyah Serif Display';color:{INK}">{text}</span>
<span style="flex:1;height:2px;background:#DDD6C9"></span></div>""")


def pull(name, html_text):
    render(name, 1056, f"""<div style="padding:26px 40px 30px;text-align:center">
<div style="font:700 50px/1.75 'Thmanyah Serif Display';color:{INK}"><span style="color:{CORAL}">«</span>{html_text}<span style="color:{CORAL}">»</span></div>
<div style="display:flex;justify-content:center;margin-top:18px">{WAVE.format(w=140)}</div></div>""")


title("t-intro", "افتتاحيــة العدد", size=52, wave=200)
title("t-change", "هـــل تتغير الشخصيــة؟")
title("t-restorative", f"المصلح أم <span style=\"{TAIL}\">المتقن</span>؟")
for key, text in [("before", "قبل المقال"), ("structure", "هيكل الحجة"), ("analysis", "التفكيك"), ("arrival", "الوصول")]:
    subhead(f"s-{key}", text)
pull("p-change", f"قبول التحدي لم يتنبأ بأي تغير،<br>والذي تنبأ به <span style=\"{MARKER}\">هو إنجازه فعلًا</span>")
pull("p-restorative", f"النظام واحد والأعطال واحدة،<br>وما هو <span style=\"{MARKER}\">دعوة</span> عند رائد هو عبء عند خالد")

# The سرد partner card, in سرد's own identity (ink, paper, rubric harakat).
render("sard-partner", 1056, f"""
<div style="background:#1E1A16;border-radius:24px;color:#F6F1E7;display:flex;align-items:center;padding:0 56px;gap:44px;height:330px">
 <div style="position:relative;width:320px;height:140px;flex:none">
  <span style="position:absolute;inset:0;font:700 104px/140px 'Thmanyah Serif Display';text-align:center;white-space:nowrap;color:#E07A62">سَــــــرْد</span>
  <span style="position:absolute;inset:0;font:700 104px/140px 'Thmanyah Serif Display';text-align:center;white-space:nowrap;color:#F6F1E7;-webkit-text-stroke:.6px #F6F1E7">ســــــرد</span>
 </div>
 <div style="width:1px;height:180px;background:rgba(246,241,231,.25);flex:none"></div>
 <div><div style="font:500 22px/1 'Thmanyah Sans';color:#E07A62;margin-bottom:16px">شريك المحتوى</div>
  <div style="font:700 42px/1.45 'Thmanyah Serif Display'">من الأساس إلى المعنى</div>
  <div style="font:400 24px/1.6 'Thmanyah Serif Text';color:rgba(246,241,231,.75);margin-top:10px">الشرحان في هذا العدد من سرد: يأخذ النص الصعب ويشرحه كأن أحدًا يجلس معك.</div></div>
</div>""", height=330)

# Closing panel: Nasar's statement band in ink, with its questions, Ali's hero line and the call to start.
render("cta", 1056, f"""
<div style="background:{INK};border-radius:24px;color:{CREAM};padding:56px 64px 54px">
 <div style="display:flex;align-items:center;gap:14px">{MARK.format(s=54, ink=CREAM, dot=CORAL)}
  <span style="font:700 50px/1 'Thmanyah Serif Display'">نســار</span></div>
 <div style="margin:44px 0 40px">
  {''.join(f'<div style="font:400 33px/1.6 Thmanyah Serif Text;color:rgba(242,238,231,.9);margin:0 0 12px"><i style="display:inline-block;width:11px;height:11px;border-radius:50%;background:{CORAL};margin-left:16px;vertical-align:middle"></i>{q}</div>' for q in [
      "هل أجريت اختبار شخصية بالإنجليزية ثم شعرت أن نتيجته لا تشبهك؟",
      "هل تعرف عن نفسك أكثر مما تستطيع أن تقوله؟",
      "هل تريد أن تفهم لماذا تشدّك أعمال وتنفر من أخرى؟"])}
 </div>
 <div style="font:700 54px/1.6 'Thmanyah Serif Display'">إحساسك <span style="{TAIL}">بنفسك</span> صحيح،<br><span style="{MARKER}">وما ينقصه إلا الكلمات</span></div>
 <div style="font:400 27px/1.5 'Thmanyah Serif Text';color:rgba(242,238,231,.7);margin-top:14px">أربعة مقاييس وقراءة واحدة تجمعها</div>
 <div style="display:flex;align-items:center;gap:24px;margin-top:40px">
  <span style="background:{CREAM};color:{INK};font:700 30px/1 'Thmanyah Sans';padding:22px 60px;border-radius:999px">ابدأ</span>
  <span style="font:500 26px/1 'Thmanyah Sans';color:rgba(242,238,231,.7);direction:ltr">nasar.me</span></div>
</div>""", fmt="jpg")

# Divider mark on white.
render("mark", 64, MARK.format(s=64, ink=INK, dot=CORAL_INK), height=64)
print("assets ok")
