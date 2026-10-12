#!/usr/bin/env python3
# Workout logging, design B: finished exercises collapse, one exercise open, each set is one big button that opens a numpad sheet.
s=open('src.html').read()
def rep(old,new):
    global s
    assert s.count(old)==1, ('anchor',s.count(old),old[:70])
    s=s.replace(old,new)

css='''/* workout logging B */
.wohead{display:flex;align-items:center;gap:10px;padding:2px 4px 0}
.wohead .bar{flex:1;height:6px;border-radius:3px;background:var(--chip);overflow:hidden}
.wohead .bar b{display:block;height:100%;background:linear-gradient(90deg,#3D7BFF,#00C8FF);border-radius:3px;transition:width .3s}
.woex{display:flex;align-items:center;gap:12px;width:100%;text-align:left;padding:14px 16px}
.wonum{width:30px;height:30px;border-radius:50%;flex:none;display:grid;place-items:center;font-size:13px;font-weight:600;background:var(--chip);color:var(--ink2)}
.wonum.ok{background:var(--good);color:#06101F}
.wodots{display:flex;gap:4px;flex:none}.wodots i{width:7px;height:7px;border-radius:50%;background:var(--chip)}.wodots i.on{background:var(--good)}
.woopen{border-color:color-mix(in srgb,var(--accent) 45%,transparent)!important}
.wos{display:flex;align-items:center;gap:10px}
.wos .val{flex:1;min-width:0;height:48px;border-radius:15px;background:var(--chip);display:flex;align-items:center;gap:6px;padding:0 12px;font-size:16.5px;font-weight:600;white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--ink);text-align:left}
.wos .val .x{color:var(--ink3);font-weight:500}
.wos .val.ghost .v{color:var(--ink3)}
.wos.done .val{background:color-mix(in srgb,var(--good) 11%,transparent)}
.wos.cur .val{box-shadow:inset 0 0 0 2px var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent)}
.wos .chk{width:48px;height:48px;border-radius:15px}
.wopf{flex:1;border-radius:18px;padding:10px 14px;background:var(--chip);text-align:left}
.wopf.on{box-shadow:inset 0 0 0 2px var(--accent);background:color-mix(in srgb,var(--accent) 13%,transparent)}
.wopf .v{font-size:34px;font-weight:700;line-height:1.15;font-variant-numeric:tabular-nums;letter-spacing:-.02em;white-space:nowrap;overflow:hidden}
.wopf.on .v::after{content:'';display:inline-block;width:2px;height:28px;background:var(--accent);margin-left:3px;vertical-align:-3px;animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.woqc{display:flex;gap:6px;flex-wrap:wrap}.woqc button{height:34px;padding:0 12px;border-radius:999px;background:var(--chip);font-size:13.5px;font-weight:600;white-space:nowrap;color:var(--ink)}
.woqc button.ip{color:var(--h);background:color-mix(in srgb,var(--h) 13%,transparent)}.woqc button.on{box-shadow:inset 0 0 0 1.5px currentColor}
.wokp{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.wokp button{height:50px;border-radius:16px;background:var(--chip);display:grid;place-items:center;font-size:22px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.wokp button:active{transform:scale(.96)}
</style>'''
i=s.index('</style>');s=s[:i]+css+s[i+len('</style>'):]

# ---------- screen ----------
i=s.index("function scrWorkout(){");j=s.index("\n}\n",i)+3
s=s[:i]+r"""function woCur(e){return e.sets.findIndex(x=>!x.done);}
function woOpenIdx(){const w=S.active;if(UI.woOpen!=null&&w.ex[UI.woOpen])return UI.woOpen;const n=w.ex.findIndex(e=>e.sets.some(x=>!x.done));return n<0?w.ex.length-1:n;}
function woVal(e,x){if(e.timed)return '<span class="v">'+esc(repsTxt(x.plan))+'</span>';const kg=x.kg!==''&&x.kg!=null?x.kg:'0',r=x.reps||String(parseInt(x.plan)||'');return '<span class="v">'+esc(kg)+' '+U()+'</span><span class="x">×</span><span class="v">'+esc(r)+'</span>';}
function scrWorkout(){
 const w=S.active;if(!w)return scrMissing();const t=tpl(w.tid);
 const tot=w.ex.reduce((a,e)=>a+e.sets.length,0),done=w.ex.reduce((a,e)=>a+e.sets.filter(x=>x.done).length,0);const open=woOpenIdx();
 let h='<div class="view detail" id="view" style="padding-bottom:'+(w.restUntil?180:120)+'px">'+nav(t?t.name:'Trénink','<button class="btn ghost sm glass" data-a="wofinish">Dokončit</button>')+'<div class="stack" style="gap:10px">';
 h+='<div class="wohead"><span class="num" style="font-size:22px;font-weight:700;min-width:64px" data-tick="wo">'+fmtClock(elapsed())+'</span><div class="bar"><b style="width:'+(tot?done/tot*100:0)+'%"></b></div><span class="tiny muted num">'+done+' / '+tot+' sérií</span></div>';
 w.ex.forEach((e,i)=>{const nd=e.sets.filter(x=>x.done).length,all=nd===e.sets.length;
  const dots='<span class="wodots">'+e.sets.map(x=>'<i'+(x.done?' class="on"':'')+'></i>').join('')+'</span>';
  if(i!==open){
   let sub;if(all&&!e.timed){const b=e.sets.reduce((a,x)=>toKg(x.kg)>toKg(a.kg)||(toKg(x.kg)===toKg(a.kg)&&(+x.reps||0)>(+a.reps||0))?x:a,e.sets[0]);sub=e.sets.length+' '+pl(e.sets.length,'série','série','sérií')+' · nejvíc '+esc(b.kg||'0')+' '+U()+' × '+esc(b.reps||'')+(e.sets.some(x=>x.up)?' 🔥':'');}
   else sub=(nd?nd+' z ':'')+e.sets.length+' '+pl(e.sets.length,'série','série','sérií')+' · '+esc(repsTxt(e.sets[0].plan));
   h+='<button class="glass card woex" data-a="woopen" data-v="'+i+'"><span class="wonum'+(all?' ok':'')+'">'+(all?ic('check',16,3):(i+1))+'</span><span class="grow" style="min-width:0"><span class="ellip" style="display:block;font-weight:600">'+esc(e.name)+'</span><span class="tiny muted ellip" style="display:block">'+sub+'</span></span>'+dots+'</button>';
   return;}
  const cur=woCur(e),ls=!e.timed&&lastFor(S.cme,e.name);
  h+='<div class="glass card stack woopen" style="gap:8px">';
  h+='<div class="row" style="gap:10px;align-items:flex-start"><div class="grow" style="min-width:0"><div class="title-l" style="font-size:20px;line-height:1.2">'+esc(e.name)+'</div>'+(e.orig?'<div class="tiny faint row" style="gap:6px;margin-top:2px">místo '+esc(e.orig.name)+' <button class="tiny" style="color:var(--accent);font-weight:600" data-a="swapundo" data-v="'+i+'">Vrátit</button></div>':'')
   +'<div class="tiny muted row" style="gap:10px;margin-top:4px;flex-wrap:wrap">'+(e.rest?'<span class="row" style="gap:4px">'+ic('clock',13)+'<span class="num">'+fmtRest(e.rest)+'</span></span>':'')+(ls?'<span>Minule '+esc(ls.sets.map(fmtSet).join(' · '))+'</span>':'<span>Poprvé</span>')+'<button class="tiny" style="color:var(--accent);font-weight:600" data-a="exhist" data-v="'+esc(S.cme+'|'+e.name)+'">Historie</button></div></div>'
   +'<button class="iconbtn sm glass strong" style="flex:none" data-a="swapopen" data-v="'+i+'" aria-label="Vyměnit cvik">'+ic('swap',17)+'</button></div>';
  if(e.note)h+='<div class="small muted" style="line-height:1.4">'+esc(e.note)+'</div>';
  if(e.media&&e.media.length)h+='<div class="media">'+e.media.map(m=>mediaThumb(m)).join('')+'</div>';
  h+='<div class="stack" style="gap:8px;margin-top:2px">'+e.sets.map((x,k)=>{const cls=x.done?' done':k===cur?' cur':'';const ghost=!x.done&&k!==cur;
   const rir=x.int==='Rozcvička'?ipill('Rozcvička'):x.rir?ipill(x.rir):'';
   return '<div class="wos'+cls+'"><span class="setno" style="width:28px;height:28px;font-size:13px;flex:none">'+(k+1)+'</span><button class="val'+(ghost?' ghost':'')+'" data-a="wopad" data-v="'+i+':'+k+'" aria-label="Zapsat sérii '+(k+1)+'">'+woVal(e,x)+'<span class="grow"></span>'+(x.up?'<span class="upflame">🔥</span>':'')+rir+'</button><button class="chk'+(x.done?' on':'')+'" data-a="woset" data-v="'+i+':'+k+'" aria-label="Série '+(k+1)+' hotová">'+ic('check',20,2.6)+'</button></div>';}).join('')+'</div>';
  h+='<button class="small" style="color:var(--accent);font-weight:600;align-self:flex-start;padding:4px 2px" data-a="woaddset" data-v="'+i+'">'+ic('plus',15,2.4)+' Přidat sérii</button>';
  h+='</div>';});
 h+='<button class="btn ghost block" data-a="lockprev">'+ic('lock',18)+' Náhled zamknuté obrazovky</button><button class="btn ink block" data-a="wofinish">'+ic('check',18,2.4)+' Dokončit trénink</button><button class="btn ghost block" data-a="wocancel" style="color:var(--bad)">Zrušit trénink</button>';
 h+='<p class="tiny faint" style="text-align:center;margin:0 20px">Klepni na sérii a zapiš váhu a opakování. Hodnoty jsou předvyplněné z minula, takže často stačí jen odškrtnout. '+(S.restOn!==false?'Po odškrtnutí série se spustí odpočet pauzy.':'Odpočet pauzy máš vypnutý v Nastavení.')+'</p>';
 h+='</div></div>';
 if(w.restUntil)h+='<div class="restbar glass strong"><div class="grow stack" style="gap:0;min-width:0"><span class="tiny muted ellip">Pauza · '+esc(w.restEx||'')+'</span><span class="num" style="font-size:26px;font-weight:700;line-height:1.15" data-tick="rest">'+fmtClock(Math.max(0,Math.ceil((w.restUntil-Date.now())/1000)))+'</span></div><button class="btn ghost sm" data-a="worest" data-v="15">+15 s</button><button class="btn ink sm" data-a="worest" data-v="skip">Přeskočit</button></div>';
 return h;
}
"""+s[j:]

# ---------- numpad sheet ----------
rep(" if(sh.type==='confirm'){",r""" if(sh.type==='wopad'&&S.active&&S.active.ex[sh.i]&&S.active.ex[sh.i].sets[sh.k]){const e=S.active.ex[sh.i],x=e.sets[sh.k],warm=x.int==='Rozcvička',st=lbsStep();
  const fld=(f,l)=>'<button class="wopf'+(sh.f===f?' on':'')+'" data-a="wopadf" data-v="'+f+'"><div class="tiny muted">'+l+'</div><div class="v">'+esc(sh.buf[f]||'0')+'</div></button>';
  const qc=sh.f==='kg'?[['last','Jako minule'],['-'+st,'−'+String(st).replace('.',',')],['+'+st,'+'+String(st).replace('.',',')],['+'+st*2,'+'+String(st*2).replace('.',',')]]:[['last','Jako minule'],['-1','−1'],['+1','+1'],['plan','Cíl '+(parseInt(x.plan)||'')]];
  b='<div class="stack" style="gap:12px"><div class="row between" style="align-items:flex-start"><div style="min-width:0"><div class="tiny muted ellip">'+esc(e.name)+'</div><div class="title-l">Série '+(sh.k+1)+' z '+e.sets.length+'</div></div><span class="ip '+(ICLS[x.int]||'')+'">Cíl '+esc(repsTxt(x.plan))+(x.int&&!warm?' · '+esc(x.int):'')+'</span></div>'
   +'<div class="row" style="gap:8px">'+fld('kg',U())+fld('reps','opakování')+'</div>'
   +'<div class="woqc">'+qc.map(q=>'<button data-a="wopadq" data-v="'+q[0]+'">'+q[1]+'</button>').join('')+'</div>'
   +(warm?'':'<div class="woqc">'+['Selhání','1 RIR','2 RIR','3 RIR'].map(o=>'<button class="ip '+ICLS[o]+(sh.buf.rir===o?' on':'')+'" style="height:34px;padding:0 12px;font-size:13.5px" data-a="wopadr" data-v="'+o+'">'+o+'</button>').join('')+'</div>')
   +'<div class="wokp">'+['1','2','3','4','5','6','7','8','9',',','0','del'].map(k=>'<button data-a="wokey" data-v="'+k+'"'+(k===','&&sh.f==='reps'?' disabled style="opacity:.3"':'')+'>'+(k==='del'?ic('del',24):k)+'</button>').join('')+'</div>'
   +'<button class="btn ink block" data-a="wopadsave">'+ic('check',20,2.6)+' '+(x.done?'Uložit změny':'Uložit sérii')+'</button>'
   +(!x.done&&e.sets.length>1?'<button class="small" style="color:var(--bad);align-self:center;padding:4px" data-a="wodelset">Odebrat tuto sérii</button>':'')+'</div>';}
 if(sh.type==='confirm'){""")

# ---------- actions ----------
rep(" worest(v){",r""" woopen(v){UI.woOpen=+v;rerender();},
 woaddset(v){const e=S.active.ex[+v];const l=e.sets[e.sets.length-1]||{plan:'10',int:'',rir:'',kg:'',reps:''};e.sets.push({plan:l.plan,int:l.int==='Rozcvička'?'':l.int,rir:l.int==='Rozcvička'?'':l.rir,kg:l.kg,reps:l.reps,done:false});save();rerender();},
 wopad(v){const [i,k]=v.split(':').map(Number);const e=S.active.ex[i],x=e.sets[k];if(e.timed)return A.woset(v);
  UI.sheet={type:'wopad',i:i,k:k,f:'kg',fresh:true,buf:{kg:x.kg||'',reps:x.reps||String(parseInt(x.plan)||''),rir:x.int==='Rozcvička'?'':x.rir||''}};rerender();},
 wopadf(v){UI.sheet.f=v;UI.sheet.fresh=true;rerender();},
 wokey(v){const sh=UI.sheet,f=sh.f;let cur=sh.fresh?'':String(sh.buf[f]||'');sh.fresh=false;
  if(v==='del')cur=cur.slice(0,-1);else if(v===','){if(f==='reps'||cur.includes(','))return;cur=(cur||'0')+',';}else{if(cur.replace(',','').length>=5)return;cur=cur==='0'?v:cur+v;if(/,\d\d$/.test(cur))cur=cur.slice(0,-1);}
  sh.buf[f]=cur;rerender();},
 wopadq(v){const sh=UI.sheet,e=S.active.ex[sh.i],x=e.sets[sh.k],f=sh.f;sh.fresh=true;
  if(v==='last'){const ls=lastFor(S.cme,e.name),p=ls&&(ls.sets[sh.k]||ls.sets[ls.sets.length-1]);if(!p){toast('Tenhle cvik děláš poprvé');return;}sh.buf.kg=p.kg?wnum(p.kg):'';sh.buf.reps=String(p.reps||'');if(p.rir&&x.int!=='Rozcvička')sh.buf.rir=p.rir;}
  else if(v==='plan')sh.buf.reps=String(parseInt(x.plan)||sh.buf.reps);
  else{const d=parseFloat(v);if(f==='kg'){const n=Math.max(0,(parseFloat(String(sh.buf.kg||'0').replace(',','.'))||0)+d);sh.buf.kg=String(Math.round(n*100)/100).replace('.',',');}else sh.buf.reps=String(Math.max(0,(parseInt(sh.buf.reps)||0)+d));}
  rerender();},
 wopadr(v){UI.sheet.buf.rir=UI.sheet.buf.rir===v?'':v;rerender();},
 wopadsave(){const sh=UI.sheet,e=S.active.ex[sh.i],x=e.sets[sh.k];x.kg=String(sh.buf.kg||'').replace(/,$/,'');x.reps=sh.buf.reps||'';if(x.int!=='Rozcvička')x.rir=sh.buf.rir;UI.sheet=null;
  if(!x.done)A.woset(sh.i+':'+sh.k);else{const ls=lastFor(S.cme,e.name);x.up=!!(ls&&improvement(x,ls.sets[sh.k]));save();rerender();}},
 wodelset(){const sh=UI.sheet,e=S.active.ex[sh.i];e.sets.splice(sh.k,1);UI.sheet=null;save();rerender();},
 worest(v){""")
# after the last set of the open exercise, move on to the next unfinished one
rep("  save();rerender();if(up)setTimeout(()=>fireAt(app.querySelector('[data-a=woset][data-v=\"'+i+':'+k+'\"]'),up),30);},",
    "  if(x.done&&e.sets.every(q=>q.done)){setTimeout(()=>{if(!S.active||current()!=='workout'||UI.sheet)return;const n=S.active.ex.findIndex(q=>q.sets.some(z=>!z.done));if(n>=0&&UI.woOpen!==n){UI.woOpen=n;rerender();}},up?1300:650);}\n  save();rerender();if(up)setTimeout(()=>fireAt(app.querySelector('[data-a=woset][data-v=\"'+i+':'+k+'\"]'),up),30);},")
# a new workout starts at its first exercise
rep("  save();UI.sheet=null;push('workout');toast('Časomíra běží');},","  UI.woOpen=null;save();UI.sheet=null;push('workout');toast('Časomíra běží');},")
rep(" swap:'<path"," del:'<path d=\"M9 6.5 3.5 12 9 17.5h11.5v-11z\"/><path d=\"M12.5 9.8l4.4 4.4M16.9 9.8l-4.4 4.4\"/>',swap:'<path")
rep("function toKg(v){","function lbsStep(){return S.units==='lbs'?5:2.5;}\nfunction toKg(v){")
open('src.html','w').write(s)
print('workout ok')
