"""Renders the newsletter's image blocks (header, Nasar ad) with the Thmanyah fonts via headless Chrome, at 2x."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BASE = """<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%dpx;height:%dpx;overflow:hidden}
%s</style></head><body>%s</body></html>"""

HEADER_CSS = """
body{background:#1E1A16;color:#F6F1E7;display:flex;align-items:center;padding:0 56px;gap:44px}
.logo{position:relative;width:330px;height:120px;flex:none}
.logo span{position:absolute;inset:0;font:700 104px/120px 'Thmanyah Serif Display';text-align:center;white-space:nowrap}
.logo .r{color:#E07A62}.logo .i{color:#F6F1E7;-webkit-text-stroke:.6px #F6F1E7}
.bar{width:1px;height:190px;background:rgba(246,241,231,.25);flex:none}
.meta{font:500 22px/1.4 'Thmanyah Sans';color:#E07A62;margin-bottom:12px}
h1{font:700 46px/1.45 'Thmanyah Serif Display';color:#F6F1E7}
.also{font:400 21px/1.5 'Thmanyah Sans';color:rgba(246,241,231,.7);margin-top:14px}
"""
HEADER = """<div class="logo"><span class="r">سَــــــرْد</span><span class="i">ســــــرد</span></div>
<div class="bar"></div>
<div><div class="meta">العدد 1 · السبت 10 أكتوبر 2026</div>
<h1>كيف عرف ابن خلدون أن الظلم<br>يهدم الدولة الظالمة؟</h1>
<div class="also">ومعه: المحاكاة الشكلية، أن تشبه الناجحين ولا تعمل</div></div>"""

AD_CSS = """
body{background:#F2EEE7;color:#111;position:relative;font-family:'Thmanyah Serif Text'}
.block{position:absolute;left:-30px;top:150px;width:150px;height:230px;background:#DDBE63}
.wrap{position:absolute;inset:0;padding:52px 64px;display:flex;flex-direction:column;justify-content:space-between}
.top{display:flex;align-items:center;gap:16px}
.mark{width:62px;height:62px}
.eyebrow{font:500 22px/1 'Thmanyah Sans';color:#444}
h2{font:700 118px/1.2 'Thmanyah Serif Display';margin-top:6px}
.rule{width:300px;height:14px;display:block;margin-top:-4px}
.hero{font:400 36px/1.5 'Thmanyah Serif Text';color:#111;margin-top:16px;max-width:820px}
.foot{display:flex;align-items:center;gap:22px}
.btn{background:#111;color:#F2EEE7;font:700 26px/1 'Thmanyah Sans';padding:18px 40px;border-radius:999px}
.url{font:500 24px/1 'Thmanyah Sans';color:#444;direction:ltr}
.grain{position:absolute;inset:0;opacity:.25;mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/></filter><rect width='120' height='120' filter='url(%23n)' opacity='.35'/></svg>")}
"""
AD = """<div class="block"></div>
<div class="wrap">
 <div class="top"><svg class="mark" viewBox="0 0 24 24" fill="none"><path d="M3.2 16.6 L12.4 16.6 C17.9 16.6, 20.1 13.5, 20.1 8.4" stroke="#111111" stroke-width="2.8" stroke-linecap="round"/><circle cx="17.3" cy="5.4" r="2" fill="#B4423E"/></svg>
 <span class="eyebrow">شريك سرد في إعداد المحتوى · نسج ومسار</span></div>
 <div><h2>نســار</h2>
 <svg class="rule" viewBox="0 0 120 10" fill="none" preserveAspectRatio="none"><path d="M2 6 C 22 2, 44 9, 62 5 C 80 1, 102 8, 118 4" stroke="#E56A67" stroke-width="3" stroke-linecap="round"/></svg>
 <div class="hero">إحساسك بنفسك صحيح، وما ينقصه إلا الكلمات</div></div>
 <div class="foot"><span class="btn">ابدأ</span><span class="url">nasar.me</span></div>
</div><div class="grain"></div>"""

def render(name, w, h, css, body):
    page = os.path.join(HERE, f".{name}.html")
    open(page, "w", encoding="utf-8").write(BASE % (w, h, css, body))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    f"--screenshot={os.path.join(HERE, name + '.png')}", "file://" + page],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(page)
    print("rendered", name)

render("header", 1200, 340, HEADER_CSS, HEADER)
render("nasar-ad", 1200, 600, AD_CSS, AD)
