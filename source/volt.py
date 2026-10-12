import re
s=open('src.html').read()
def r(a,b,cnt=1):
    global s
    assert a in s,('MISSING',a[:80]); s=s.replace(a,b) if cnt==0 else s.replace(a,b,cnt)
pat=r'linear-gradient\((?:\d+deg,)?#(?:3D7BFF|2F6BFF)(?: 0%)?,#00(?:B8F0|C8FF|A8E0)(?: 100%)?\)'
# fix text colors on the gradient first
s=re.sub(pat+r';color:#fff',r'var(--grad);color:var(--grad-ink)',s)
s=re.sub(pat,'var(--grad)',s)
r('.cal .d.has small{color:rgba(255,255,255,.8)}','.cal .d.has small{color:rgba(10,10,11,.6)}')
r('.wkd.on{background:var(--grad);color:var(--grad-ink)}.wkd.on .l,.wkd.on .m{color:rgba(255,255,255,.9)}.wkd.on .m i{background:#fff!important}','.wkd.on{background:var(--ink);color:var(--bg)}.wkd.on .l,.wkd.on .m{color:var(--bg);opacity:.85}.wkd.on .m i{background:var(--bg)!important}')
r('.pkbox.on{border:0;background:var(--grad)}','.pkbox.on{border:0;background:var(--grad);color:var(--grad-ink)}')
s=s.replace('background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent','color:var(--acc-text)',1)
s=s.replace('rgba(61,123,255,','rgba(0,0,0,')
# nextw hero
r('.nextw{border-radius:28px;padding:20px;color:#fff;background:var(--grad);box-shadow:0 14px 34px rgba(0,0,0,.32)}\n.nextw .title-l{color:#fff}\n.wpill{display:inline-flex;align-items:center;height:24px;padding:0 10px;border-radius:999px;font-size:12px;font-weight:600;background:rgba(255,255,255,.2);color:#fff}',
 '.nextw{border-radius:26px;padding:20px;color:var(--grad-ink);background:var(--grad);box-shadow:0 14px 34px rgba(150,190,0,.18)}\n.nextw .title-l{color:var(--grad-ink)}\n.nextw .eyebrow{color:rgba(10,10,11,.62)!important;font-weight:700}\n.nextw .hero-t{font-size:36px;font-weight:900;line-height:.95;letter-spacing:-.025em;text-transform:uppercase;margin:4px 0 0;text-wrap:balance}\n.wpill{display:inline-flex;align-items:center;height:24px;padding:0 10px;border-radius:999px;font-size:12px;font-weight:700;background:rgba(10,10,11,.1);color:var(--grad-ink)}\n'
 '.swipe{position:relative;height:62px;border-radius:31px;background:#0A0A0B;overflow:hidden;touch-action:pan-y;user-select:none;-webkit-user-select:none}\n.swipe .sw-t{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding-left:52px;font-weight:800;font-size:13.5px;letter-spacing:.14em;color:#D4FF3A;pointer-events:none;transition:opacity .2s}\n.swipe .sw-t em{font-style:normal;opacity:.4;margin-left:8px;letter-spacing:-.04em;animation:swh 1.6s ease-in-out infinite}\n@keyframes swh{50%{opacity:.9;transform:translateX(3px)}}\n.swipe .sw-tr{position:absolute;left:5px;top:5px;bottom:5px;width:52px;border-radius:26px;background:linear-gradient(90deg,rgba(212,255,58,.12),rgba(212,255,58,.5));display:flex;align-items:center;padding-left:20px;font-weight:800;font-size:13.5px;letter-spacing:.14em;color:#D4FF3A;white-space:nowrap;overflow:hidden;opacity:0;pointer-events:none}\n.swipe .sw-th{position:absolute;left:5px;top:5px;width:52px;height:52px;border-radius:50%;background:#D4FF3A;color:#0A0A0B;display:grid;place-items:center;box-shadow:0 4px 14px rgba(0,0,0,.35);cursor:grab;touch-action:none}\n.swipe.back .sw-th,.swipe.back .sw-tr{transition:left .35s cubic-bezier(.34,1.3,.5,1),width .35s cubic-bezier(.34,1.3,.5,1)}\n.nextw .btn.dk{background:rgba(10,10,11,.1);color:var(--grad-ink)}\n.wmark{position:absolute;left:50%;top:56%;width:82%;transform:translate(-50%,-50%);opacity:.075;z-index:0;pointer-events:none}')
# Electric block -> Volt
a=s.index('/* Electric theme');b=s.index('/* smoothness')
L=':root{--bg:#EDEDE8;--bg2:#F7F7F4;--ink:#0A0A0B;--ink2:#55555A;--ink3:#8A8A8F;--line:rgba(0,0,0,.08);--chip:rgba(0,0,0,.055);--on-ink:#fff;--glass:rgba(255,255,255,.80);--glass-strong:rgba(255,255,255,.93);--glass-edge:rgba(255,255,255,.95);--glass-shade:rgba(0,0,0,.05);--shadow:0 8px 24px rgba(0,0,0,.07),0 0 0 .5px rgba(0,0,0,.06);--accent:#5E8C00;--grad:#D4FF3A;--grad-ink:#0A0A0B;--acc-text:#0A0A0B;--acc-soft:rgba(10,10,11,.10);--tabon:#0A0A0B;--page:#DCDCD6;color-scheme:light}'
D='--bg:#0A0A0B;--bg2:#141416;--ink:#F5F5F2;--ink2:#A1A1A6;--ink3:#6E6E73;--line:rgba(255,255,255,.08);--chip:rgba(255,255,255,.07);--on-ink:#0A0A0B;--glass:rgba(24,24,27,.78);--glass-strong:rgba(32,32,36,.92);--glass-edge:rgba(255,255,255,.10);--glass-shade:rgba(0,0,0,.4);--shadow:0 12px 32px rgba(0,0,0,.45);--accent:#D4FF3A;--good:#34E39A;--bad:#FF5D73;--warn:#FFC24B;--grad:#D4FF3A;--grad-ink:#0A0A0B;--acc-text:#D4FF3A;--acc-soft:rgba(212,255,58,.16);--tabon:#D4FF3A;--page:#050506;color-scheme:dark'
COMMON='''.screen{background:var(--bg)!important}
.ambient{background:var(--bg)!important;animation:none!important}
.glass::before{background:linear-gradient(160deg,rgba(255,255,255,.10),rgba(255,255,255,0) 40%)!important}
.btn.ink,.chip.on{background:var(--grad)!important;color:var(--grad-ink)!important;box-shadow:none!important;font-weight:700}
.title-xl{font-weight:900!important;letter-spacing:-.025em!important;text-transform:uppercase;line-height:1!important}
.title-l{font-weight:800}
.kpi .v{font-weight:900!important}
.eyebrow{color:var(--ink3)!important;font-weight:700;letter-spacing:.14em}
.code{color:var(--ink)}
.avatar{background:var(--ink)!important;color:var(--bg)!important;box-shadow:none!important}
.chart rect[opacity="1"]{fill:var(--acc-text)}
.tabbar{background:var(--glass)!important;-webkit-backdrop-filter:blur(30px) saturate(180%)!important;backdrop-filter:blur(30px) saturate(180%)!important}
.tab{font-weight:600}
.tab.on{color:var(--tabon)!important;font-weight:800}
.tabpill{background:var(--acc-soft)!important;border:1px solid var(--acc-soft);box-shadow:inset 0 1px 0 rgba(255,255,255,.18)!important}
'''
LX='''.tabbar{border:1px solid rgba(0,0,0,.16)!important;box-shadow:0 16px 36px rgba(0,0,0,.22),0 2px 8px rgba(0,0,0,.10),inset 0 1px 0 #fff!important;background:rgba(255,255,255,.84)!important}
.tab:not(.on){color:#0A0A0B!important;opacity:.62}
.glass{border-color:rgba(0,0,0,.06)!important}
'''
DX='.mark{background:#fff}\n'
def sc(css,sel):
    out=[]
    for line in css.strip().split('\n'):
        k,v=line.split('{',1); out.append(','.join(sel+' '+x.strip() for x in k.split(','))+'{'+v)
    return '\n'.join(out)+'\n'
blk='/* Volt theme: black and white base with one electric lime accent, heavy uppercase titles, frosted glass bars */\n'+L+'\n'+COMMON
blk+=sc(LX,':root[data-theme="light"]')+'@media (prefers-color-scheme: light){\n'+sc(LX,':root:not([data-theme="dark"])')+'}\n'
blk+='@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){'+D+'}\n'+sc(DX,':root:not([data-theme="light"])')+'}\n:root[data-theme="dark"]{'+D+'}\n'+sc(DX,':root[data-theme="dark"]')
s=s[:a]+blk+s[b:]

# fonts
r('family=Geist:wght@300;400;500;600;700&','family=Inter:opsz,wght@14..32,400..900&family=Geist:wght@300;400;500;600;700&')
r('--f-ui:"Geist",','--f-ui:"Inter","Geist",')
# watermark
r('<div class="ambient"></div>','<div class="ambient"></div>\n    <span class="mark wmark"></span>')
open('src.html','w').write(s)
print('ok')
