s=open('src.html').read()
def r(a,b):
    global s
    assert a in s,('MISSING',a[:80]); s=s.replace(a,b,1)
r('''<span class="mark" style="width:16px;background:#fff"></span>''','''<span class="mark" style="width:16px;background:#0A0A0B"></span>''')
old_start=s.index("  h+='<div class=\"nextw stack\" style=\"gap:14px\">")
old_end=s.index("\n",old_start)
new='''  h+='<div class="nextw stack" style="gap:14px"><div class="row between"><span class="eyebrow">'+esc(cardLbl())+'</span><span class="wpill">'+esc(nt.cat)+'</span></div><div><div class="hero-t">'+esc(nt.name)+'</div><div class="small" style="opacity:.7;margin-top:8px;font-weight:600">'+nt.ex.length+' '+pl(nt.ex.length,'cvik','cviky','cviků')+' · '+setCount(nt)+' sérií · '+(ld?'naposledy '+rel(ld):'zatím necvičeno')+'</div></div>'+(np.note?'<div class="small" style="background:rgba(10,10,11,.08);border-radius:14px;padding:9px 12px;line-height:1.4">„'+esc(np.note)+'“ <span style="opacity:.65">· '+esc(t.name.split(' ')[0])+'</span></div>':'')+'<div class="swipe" data-tid="'+nt.id+'"><div class="sw-tr"></div><div class="sw-t">PŘETÁHNI A ZAČNI<em>›››</em></div><div class="sw-th" role="button" aria-label="Přetáhni a začni trénink">'+ic('arrow',24)+'</div></div><div class="row" style="gap:8px"><button class="btn sm dk" style="flex:1" data-a="sheet" data-v="cpick">Vybrat jiný trénink</button><button class="btn sm dk" data-a="open" data-v="template:'+nt.id+'">Detail</button></div></div>';}'''
s=s[:old_start]+new+s[old_end:]
# swipe handling
r("/* bar chart: tap, hold or hover a bar to see its exact value */","""/* swipe to start: drag the lime knob to the end of the track */
app.addEventListener('pointerdown',e=>{const th=e.target.closest('.sw-th');if(!th)return;const sw=th.parentNode,tr=sw.querySelector('.sw-tr'),tx=sw.querySelector('.sw-t');
 const max=sw.clientWidth-62,x0=e.clientX;let dx=0,done=false;sw.classList.remove('back');try{th.setPointerCapture(e.pointerId);}catch(_){}
 const set=v=>{th.style.left=(5+v)+'px';tr.style.width=(v+52)+'px';tr.style.opacity=v>4?1:0;tr.textContent=v>max*.85?'PUSŤ':'JEŠTĚ KOUSEK';tx.style.opacity=Math.max(0,1-v/80);};
 const mv=ev=>{dx=Math.max(0,Math.min(max,ev.clientX-x0));set(dx);};
 const up=()=>{th.removeEventListener('pointermove',mv);th.removeEventListener('pointerup',up);th.removeEventListener('pointercancel',up);
  if(dx>max*.85){done=true;set(max);tr.textContent='JDEME NA TO';if(navigator.vibrate)navigator.vibrate(15);setTimeout(()=>A.wostart(sw.dataset.tid),220);}
  else{sw.classList.add('back');set(0);}};
 th.addEventListener('pointermove',mv);th.addEventListener('pointerup',up);th.addEventListener('pointercancel',up);e.preventDefault();});
/* bar chart: tap, hold or hover a bar to see its exact value */""")
open('src.html','w').write(s);print('ok')
