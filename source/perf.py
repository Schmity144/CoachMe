#!/usr/bin/env python3
# Smoothness pass: cross-fading screen transitions, sheets that slide away, no replayed animations on re-render, lighter glass in scrolling content.
s=open('src.html').read()
def rep(old,new):
    global s
    assert s.count(old)==1, ('anchor',s.count(old),old[:70])
    s=s.replace(old,new)

css='''/* smoothness: transitions, no replayed animations, lighter scrolling */
button,a,input,select,textarea,label{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.view,.sheet{overscroll-behavior:contain}
.view .glass{-webkit-backdrop-filter:none;backdrop-filter:none}
.view .navbar .glass{-webkit-backdrop-filter:blur(26px) saturate(185%);backdrop-filter:blur(26px) saturate(185%)}
.iconbtn,.chip,button.card,button.kpi,.tab{transition:transform .14s ease}
.iconbtn:active,.chip:active,button.card:active,button.kpi:active{transform:scale(.97)}
.still{animation:none!important}
.view.enter{animation:vin .3s cubic-bezier(.2,.8,.2,1) both}
.view.enter-back{animation:vback .3s cubic-bezier(.2,.8,.2,1) both}
.view.enter-tab{animation:vfade .2s ease both}
.view.ghost{z-index:0;pointer-events:none}
.view.ghost.out-l{animation:voutl .18s ease-in both}
.view.ghost.out-r{animation:voutr .18s ease-in both}
.view.ghost.out-f{animation:voutf .16s ease both}
@keyframes vin{from{transform:translate3d(36px,0,0);opacity:0}to{transform:none;opacity:1}}
@keyframes vback{from{transform:translate3d(-28px,0,0);opacity:0}to{transform:none;opacity:1}}
@keyframes vfade{from{opacity:0}to{opacity:1}}
@keyframes voutl{to{transform:translate3d(-28px,0,0);opacity:0}}
@keyframes voutr{to{transform:translate3d(36px,0,0);opacity:0}}
@keyframes voutf{to{opacity:0}}
.sheet{animation:sheetin .34s cubic-bezier(.2,.85,.25,1)}
@keyframes sheetin{from{transform:translate3d(0,110%,0)}to{transform:none}}
.sheet.out{animation:sheetout .24s cubic-bezier(.4,0,1,1) forwards;pointer-events:none}
.scrim.out{animation:scrimout .24s ease forwards;pointer-events:none}
@keyframes sheetout{to{transform:translate3d(0,110%,0)}}
@keyframes scrimout{to{opacity:0}}
.toast{animation:toastin .28s cubic-bezier(.2,.8,.2,1)}
.toast.out{animation:toastout .2s ease forwards}
@keyframes toastin{from{transform:translate(-50%,-12px);opacity:0}to{transform:translate(-50%,0);opacity:1}}
@keyframes toastout{to{transform:translate(-50%,-8px);opacity:0}}
@media (prefers-reduced-motion:reduce){.view.enter,.view.enter-back,.view.enter-tab,.sheet,.toast{animation:none!important}}
</style>'''
i=s.index('</style>');s=s[:i]+css+s[i+len('</style>'):]

# render: keep elements that were already on screen still, cross-fade the old screen out, slide closed sheets away
rep("function render(anim){\n const prevView=document.getElementById('view');",
r"""const REDUCED=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
const KEEP=['.toast','.restbar','.notif','.calgrid','.lock','.scrim'];
function render(anim){
 const prevView=document.getElementById('view');
 const had=KEEP.filter(q=>app.querySelector(q));
 const oldSheet=app.querySelector('.sheet:not(.out)'),oldScrim=app.querySelector('.scrim:not(.out)');
 const sheetKey=UI.sheet?UI.sheet.type+':'+(UI.sheet.id||UI.sheet.mode||UI.sheet.i||''):null,prevKey=UI._sheetKey;UI._sheetKey=sheetKey;
 const sheetTop=oldSheet?oldSheet.scrollTop:0;
 let ghost=null,ghostTop=0;
 if(prevView&&!REDUCED&&(anim==='push'||anim==='pop'||anim==='tab')){ghost=prevView;ghostTop=prevView.scrollTop;}""")
rep(" app.innerHTML=h;\n glideTabs();",
r""" app.innerHTML=h;
 had.forEach(q=>{if(q==='.scrim'&&!(sheetKey&&sheetKey===prevKey))return;app.querySelectorAll(q).forEach(e=>e.classList.add('still'));});
 if(sheetKey&&sheetKey===prevKey){const ns=app.querySelector('.sheet');if(ns){ns.classList.add('still');ns.scrollTop=sheetTop;}}
 if(!sheetKey&&oldSheet&&!REDUCED){[oldScrim,oldSheet].forEach(e=>{if(!e)return;e.querySelectorAll('[id]').forEach(x=>x.removeAttribute('id'));e.classList.remove('still');e.classList.add('out');app.appendChild(e);setTimeout(()=>e.remove(),260);});}
 if(ghost){ghost.removeAttribute('id');ghost.querySelectorAll('[id]').forEach(x=>x.removeAttribute('id'));ghost.classList.remove('enter','enter-back','enter-tab');ghost.classList.add('ghost',anim==='push'?'out-l':anim==='pop'?'out-r':'out-f');app.appendChild(ghost);ghost.scrollTop=ghostTop;setTimeout(()=>ghost.remove(),300);}
 glideTabs();""")
rep("  if(anim==='push')v.classList.add('enter');else if(anim==='pop')v.classList.add('enter-back');",
    "  if(anim==='push')v.classList.add('enter');else if(anim==='pop')v.classList.add('enter-back');else if(anim==='tab')v.classList.add('enter-tab');")
rep("  else if(anim==='pop'&&UI.scroll[key]!=null)v.scrollTop=UI.scroll[key];",
    "  else if((anim==='pop'||anim==='tab')&&UI.scroll[key]!=null)v.scrollTop=UI.scroll[key];")
# tab bar switches cross-fade instead of sliding back
rep(" tab(v){UI.stack=[];UI.tab=v;if(v==='plan'&&UI.cplanSeg!=='history')UI.cplanSeg='plan';UI.sheet=null;render('pop');",
    " tab(v){if(UI.tab===v&&!UI.stack.length){const vw=document.getElementById('view');if(vw)vw.scrollTo({top:0,behavior:'smooth'});return;}UI.stack=[];UI.tab=v;if(v==='plan'&&UI.cplanSeg!=='history')UI.cplanSeg='plan';UI.sheet=null;render('tab');")
# toast fades out instead of vanishing
rep("toastT=setTimeout(()=>{UI.toast=null;const el=app.querySelector('.toast');if(el)el.remove();},1900);}",
    "toastT=setTimeout(()=>{UI.toast=null;const el=app.querySelector('.toast');if(el){el.classList.remove('still');el.classList.add('out');setTimeout(()=>el.remove(),220);}},1900);}")
open('src.html','w').write(s)
print('perf ok')
