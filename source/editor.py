#!/usr/bin/env python3
# Template editor, design A: short exercise list, each exercise edited in a sheet; pick several exercises at once; sets may have no rep target (only RIR).
s=open('src.html').read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old)
    assert (n==cnt if cnt else n>=1), ('anchor',n,old[:70])
    s=s.replace(old,new)

css='''/* template editor A */
.edrow{display:flex;align-items:center;gap:12px;width:100%;text-align:left;padding:13px 14px;border-top:.5px solid var(--line)}
.edrow:first-child{border-top:0}
.idots{display:flex;gap:3px;flex:none}.idots i{width:8px;height:8px;border-radius:50%;background:var(--chip);display:block}
.edstp{flex:1;display:flex;align-items:center;gap:6px;padding:8px 10px;border-radius:18px;background:var(--chip)}
.edstp .b{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:color-mix(in srgb,var(--accent) 12%,transparent);flex:none}
.edstp .v{flex:1;text-align:center;min-width:0}.edstp .v b{display:block;font-size:28px;line-height:1.1;font-variant-numeric:tabular-nums;white-space:nowrap}
.edsets{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.edsets button{display:flex;flex-direction:column;align-items:center;gap:4px}
.edsets .ip{width:100%;justify-content:center;height:34px;font-size:12.5px}
.edsets .ip.none{--h:var(--ink3)}
.edrest{display:flex;gap:6px;flex-wrap:wrap}
.edadv{display:grid;grid-template-columns:28px 1fr auto;gap:8px;align-items:center}
.edadv input{height:38px;border-radius:11px;border:0;background:var(--chip);text-align:center;font-size:15px;font-weight:600;color:var(--ink);outline:none;font-family:inherit;width:100%}
.pkbox{width:26px;height:26px;border-radius:8px;border:2px solid var(--ink3);display:grid;place-items:center;flex:none;color:#fff}
.pkbox.on{border:0;background:linear-gradient(120deg,#3D7BFF,#00C8FF)}
</style>'''
i=s.index('</style>');s=s[:i]+css+s[i+len('</style>'):]

# sets without a rep target read as "Do selhání" / "Do 1 RIR"
rep("function repsTxt(r){return /^\\d+$/.test(String(r).trim())?r+' opak.':String(r);}",
    "function repsTxt(r,int){r=String(r==null?'':r).trim();if(!r)return int==='Selhání'?'Do selhání':int&&int!=='Rozcvička'?'Do '+int:'Bez počtu';return /^\\d+$/.test(r)?r+' opak.':r;}")
rep("repsTxt(x.reps)","repsTxt(x.reps,x.int)",0)
rep("repsTxt(x.plan)","repsTxt(x.plan,x.int)",0)
rep("repsTxt(e.sets[0].plan)","repsTxt(e.sets[0].plan,e.sets[0].int)",0)
# workout: an open-target set shows "× ?" until the client fills it in, and needs reps before it counts
rep("const kg=x.kg!==''&&x.kg!=null?x.kg:'0',r=x.reps||String(parseInt(x.plan)||'');","const kg=x.kg!==''&&x.kg!=null?x.kg:'0',r=x.reps||String(parseInt(x.plan)||'')||'?';")
rep("<span class=\"ip '+(ICLS[x.int]||'')+'\">Cíl '+esc(repsTxt(x.plan,x.int))+(x.int&&!warm?' · '+esc(x.int):'')+'</span>",
    "<span class=\"ip '+(ICLS[x.int]||'')+'\">'+(parseInt(x.plan)?'Cíl '+esc(repsTxt(x.plan,x.int))+(x.int&&!warm?' · '+esc(x.int):''):esc(repsTxt(x.plan,x.int)))+'</span>")
rep("['plan','Cíl '+(parseInt(x.plan)||'')]]","].concat(parseInt(x.plan)?[['plan','Cíl '+parseInt(x.plan)]]:[])")
rep(" woset(v){const [i,k]=v.split(':').map(Number);const e=S.active.ex[i],x=e.sets[k];x.done=!x.done;",
    " woset(v){const [i,k]=v.split(':').map(Number);const e=S.active.ex[i],x=e.sets[k];if(!x.done&&!e.timed&&!x.reps&&!parseInt(x.plan)){A.wopad(v);UI.sheet.f='reps';rerender();toast('Zapiš, kolik opakování jsi dal(a)');return;}x.done=!x.done;")
rep(" wopadsave(){const sh=UI.sheet,e=S.active.ex[sh.i],x=e.sets[sh.k];",
    " wopadsave(){const sh=UI.sheet,e=S.active.ex[sh.i],x=e.sets[sh.k];if(!e.timed&&!sh.buf.reps){sh.f='reps';rerender();toast('Zapiš počet opakování');return;}")
# saving keeps an empty rep target empty
rep("e.sets.forEach(x=>{x.reps=String(x.reps).trim()||'10';});","e.sets.forEach(x=>{x.reps=String(x.reps==null?'':x.reps).trim();});")

# ---------- editor screen ----------
i=s.index("function scrEditor(){");j=s.index("\n}\n",i)+3
s=s[:i]+r"""const IDOT={'Selhání':'var(--i-fail)','1 RIR':'var(--i-1)','2 RIR':'var(--i-2)','3 RIR':'var(--i-3)','Rozcvička':'var(--i-warm)'};
function idots(sets){return '<span class="idots">'+sets.map(x=>'<i style="background:'+(IDOT[x.int]||'var(--chip)')+'"></i>').join('')+'</span>';}
function exTimed(e){return /s$/.test(String(e.sets[0]&&e.sets[0].reps||'').trim());}
function exSummary(e){const work=e.sets.filter(x=>x.int!=='Rozcvička'),w=work.length?work:e.sets,r=w.map(x=>String(x.reps||'').trim()),same=r.every(v=>v===r[0]);
 if(same&&r[0])return e.sets.length+' × '+(/^\d+$/.test(r[0])?r[0]:r[0]);
 if(same&&!r[0]){const ints=w.map(x=>x.int),si=ints.every(v=>v===ints[0]);return e.sets.length+' '+pl(e.sets.length,'série','série','sérií')+' · '+(si&&ints[0]?repsTxt('',ints[0]).toLowerCase():'bez počtu');}
 const nums=r.filter(Boolean);return e.sets.length+' '+pl(e.sets.length,'série','série','sérií')+(nums.length?' · '+nums.join('/'):'');}
function scrEditor(){
 const d=UI.draft;
 let h='<div class="view detail" id="view">'+nav(d.isNew?'Nová šablona':'Upravit šablonu','<button class="btn ink sm" data-a="savetpl">Uložit</button>')+'<div class="stack">';
 h+='<div class="glass card stack" style="gap:10px"><input class="input" id="d-name" data-in="d.name" value="'+esc(d.name)+'" placeholder="Název, např. Full body B" style="font-size:20px;font-weight:700;height:52px">'
  +'<div class="chips">'+CATS.map(c=>'<button class="chip'+(d.cat===c?' on':'')+'" data-a="dcat" data-v="'+c+'">'+c+'</button>').join('')+'</div>'
  +'<textarea class="input" id="d-desc" data-in="d.desc" placeholder="Popis pro klienta (nepovinné)" style="min-height:64px">'+esc(d.desc)+'</textarea></div>';
 const nset=d.ex.reduce((a,e)=>a+e.sets.length,0);
 h+='<div class="sec"><h3>Cviky</h3><span class="tiny faint">'+d.ex.length+' '+pl(d.ex.length,'cvik','cviky','cviků')+' · '+nset+' '+pl(nset,'série','série','sérií')+'</span></div>';
 h+=d.ex.length?'<div class="glass list" style="padding:0">'+d.ex.map((e,i)=>'<button class="edrow" data-a="exedit" data-v="'+e.id+'"><span class="setno" style="flex:none">'+(i+1)+'</span><span class="grow" style="min-width:0"><span class="ellip" style="display:block;font-weight:600">'+esc(e.name||'Bez názvu')+'</span><span class="tiny muted row" style="gap:10px;margin-top:4px;flex-wrap:wrap"><span class="num" style="color:var(--ink)">'+esc(exSummary(e))+'</span>'+idots(e.sets)+(e.rest?'<span class="row num" style="gap:3px">'+ic('clock',12)+fmtRest(e.restTxt!=null?parseRest(e.restTxt):e.rest)+'</span>':'')+(e.media&&e.media.length?'<span class="row" style="gap:3px">'+ic('camera',12)+e.media.length+'</span>':'')+'</span></span>'+ic('chev',18)+'</button>').join('')+'</div>':'<div class="glass card empty">Zatím žádné cviky. Přidej je z knihovny.</div>';
 h+='<div class="row" style="gap:8px"><button class="btn ink" style="flex:1;white-space:nowrap" data-a="expickopen">'+ic('plus',18,2.4)+' Přidat cviky</button><button class="btn ghost" style="white-space:nowrap" data-a="sheet" data-v="tplcopy">'+ic('copy',17)+' Z jiné šablony</button></div>';
 h+='<div class="row tiny faint" style="gap:10px;flex-wrap:wrap;margin:0 4px"><span>Tečky = intenzita sérií:</span><span style="color:var(--i-warm)">● rozcvička</span><span style="color:var(--i-3)">● 3 RIR</span><span style="color:var(--i-2)">● 2</span><span style="color:var(--i-1)">● 1</span><span style="color:var(--i-fail)">● selhání</span></div>';
 if(!d.isNew)h+='<button class="btn danger block" data-a="deltpl" data-v="'+d.id+'">Smazat šablonu</button>';
 h+='</div></div>';return h;
}
"""+s[j:]

# ---------- sheets: exercise detail, copy from template ----------
rep(" if(sh.type==='confirm'){",r""" if(sh.type==='exedit'&&UI.draft){const d=UI.draft,i=d.ex.findIndex(x=>x.id===sh.id),e=d.ex[i];if(e){const tm=exTimed(e),work=e.sets.filter(x=>x.int!=='Rozcvička'),r=(work.length?work:e.sets).map(x=>String(x.reps||'').trim()),same=r.every(v=>v===r[0]),free=same&&!r[0];
  const restNow=e.restTxt!=null?parseRest(e.restTxt):e.rest;
  b='<div class="stack" style="gap:12px"><div class="row" style="gap:8px;align-items:flex-start"><div class="grow" style="min-width:0"><div class="tiny muted">Cvik '+(i+1)+' z '+d.ex.length+'</div><input id="ee-name" data-in="e.'+e.id+'.name" value="'+esc(e.name)+'" placeholder="Název cviku" style="border:0;background:transparent;outline:none;font-size:21px;font-weight:700;width:100%;padding:0;color:var(--ink);font-family:inherit"></div>'
   +'<button class="iconbtn sm" data-a="exmove" data-v="'+e.id+':-1" aria-label="Posunout nahoru"'+(i===0?' disabled style="opacity:.3"':'')+'>'+ic('arrowup',16)+'</button><button class="iconbtn sm" data-a="exmove" data-v="'+e.id+':1" aria-label="Posunout dolů"'+(i===d.ex.length-1?' disabled style="opacity:.3"':'')+'>'+ic('arrowdown',16)+'</button><button class="iconbtn sm" style="color:var(--bad)" data-a="exdel" data-v="'+e.id+'" aria-label="Smazat cvik">'+ic('trash',16)+'</button></div>'
   +'<div class="row" style="gap:8px"><div class="edstp"><button class="b" data-a="exsets" data-v="-1" aria-label="Ubrat sérii">'+ic('minus',18,2.2)+'</button><div class="v"><span class="tiny muted">série</span><b>'+e.sets.length+'</b></div><button class="b" data-a="exsets" data-v="1" aria-label="Přidat sérii">'+ic('plus',18,2.2)+'</button></div>'
   +'<div class="edstp"'+(free?' style="opacity:.45"':'')+'><button class="b" data-a="exreps" data-v="-1" aria-label="Méně">'+ic('minus',18,2.2)+'</button><div class="v"><span class="tiny muted">'+(tm?'čas':'opakování')+'</span><b>'+(free?'—':same?esc(r[0].replace(/\s*s$/,'')+(tm?' s':'')):'různé')+'</b></div><button class="b" data-a="exreps" data-v="1" aria-label="Více">'+ic('plus',18,2.2)+'</button></div></div>'
   +(tm?'':'<button class="row" style="gap:10px;text-align:left" data-a="exfree"><span class="pkbox'+(free?' on':'')+'">'+(free?ic('check',15,3):'')+'</span><span class="grow"><span style="font-weight:600;display:block" class="small">Bez počtu opakování</span><span class="tiny muted">Klient cvičí do selhání nebo do zvoleného RIR</span></span></button>')
   +'<div class="tiny faint" style="margin:2px 2px -4px">Intenzita série · klepnutím přepneš</div>'
   +'<div class="edsets">'+e.sets.map((x,k)=>'<button data-a="exint" data-v="'+k+'"><span class="tiny faint">'+(k+1)+'.</span><span class="ip '+(ICLS[x.int]||'none')+'">'+(x.int?esc(x.int.replace('Rozcvička','Rozc.')):'–')+'</span></button>').join('')+'</div>'
   +'<div class="woqc"><span class="tiny faint" style="width:100%">Nastavit všem pracovním sériím</span>'+['Selhání','1 RIR','2 RIR','3 RIR'].map(o=>'<button class="ip '+ICLS[o]+'" style="height:32px;padding:0 11px;font-size:13px" data-a="exintall" data-v="'+o+'">'+o+'</button>').join('')+'<button style="height:32px;font-size:13px'+(e.sets[0]&&e.sets[0].int==='Rozcvička'?';box-shadow:inset 0 0 0 1.5px var(--i-warm);color:var(--i-warm)':'')+'" data-a="exwarm">+ Rozcvička</button></div>'
   +(UI.exAdv?'<div class="stack" style="gap:6px"><div class="tiny faint">Opakování každé série zvlášť (prázdné = bez počtu)</div>'+e.sets.map((x,k)=>'<div class="edadv"><span class="setno">'+(k+1)+'</span><input id="ee-r-'+k+'" data-in="s.'+e.id+'.'+k+'.reps" value="'+esc(x.reps||'')+'" placeholder="'+esc(repsTxt('',x.int))+'" inputmode="'+(tm?'text':'numeric')+'">'+ipill(x.int)+'</div>').join('')+'</div>':'<button class="small" style="color:var(--accent);font-weight:600;align-self:flex-start" data-a="exadv">Nastavit opakování každé série zvlášť</button>')
   +'<div class="tiny faint" style="margin:2px 2px -4px">Pauza mezi sériemi</div><div class="woqc">'+[30,60,90,120,180].map(v=>'<button class="'+(restNow===v?'on':'')+'" style="'+(restNow===v?'background:linear-gradient(120deg,#3D7BFF,#00C8FF);color:#fff':'')+'" data-a="exrest" data-v="'+v+'">'+fmtRest(v)+'</button>').join('')+'<label class="row" style="gap:4px;height:34px;padding:0 10px;border-radius:999px;background:var(--chip)">'+ic('clock',14)+'<input id="ee-rest" data-in="e.'+e.id+'.restTxt" value="'+esc(e.restTxt!=null?e.restTxt:fmtRest(e.rest))+'" inputmode="numeric" style="width:46px;border:0;background:transparent;outline:none;font-size:13.5px;font-weight:600;color:var(--ink);font-family:inherit" aria-label="Vlastní pauza"></label></div>'
   +'<input class="input" id="ee-note" data-in="e.'+e.id+'.note" value="'+esc(e.note||'')+'" placeholder="Poznámka k technice (nepovinné)">'
   +'<div class="media">'+e.media.map(m=>mediaThumb(m,true,e.id)).join('')+'<label class="thumb add" for="f-'+e.id+'" title="Přidat fotku nebo video">'+ic('camera',24)+'<span class="tag" style="background:transparent;color:var(--ink2)">Přidat</span></label><input type="file" id="f-'+e.id+'" accept="image/*,video/*" multiple hidden data-file="'+e.id+'"></div>'
   +'<button class="btn ink block" data-a="close">Hotovo</button></div>';}}
 if(sh.type==='tplcopy'){const ts=S.templates.filter(t=>!UI.draft||t.id!==UI.draft.id);
  b='<div class="stack"><div><span class="eyebrow">Z jiné šablony</span><div class="title-l" style="margin-top:4px">Zkopírovat cviky</div><div class="tiny muted" style="margin-top:2px">Cviky se přidají na konec, i se sériemi a pauzami.</div></div>'+(ts.length?'<div class="glass list">'+ts.map(t=>'<button class="li" data-a="tplcopydo" data-v="'+t.id+'"><div class="grow" style="min-width:0"><div class="ellip" style="font-weight:500">'+esc(t.name)+'</div><div class="tiny muted ellip">'+esc(t.ex.map(e=>e.name).join(' · '))+'</div></div><span class="pill neutral">'+t.ex.length+'</span></button>').join('')+'</div>':'<div class="glass card empty">Zatím nemáš jinou šablonu.</div>')+'<button class="btn ghost block" data-a="close">Zavřít</button></div>';}
 if(sh.type==='confirm'){""")

# multi-select library: checkbox rows + "Přidat N cviků"
rep("  b+=libFilters()+(list.length?'<div class=\"glass list\">'+list.map(x=>libRow(x,'expicked',ic(sw?'swap':'plus',16,2))).join('')+'</div>':'<div class=\"glass card empty\">Nic takového v knihovně není.</div>')+(sw?'':'<button class=\"btn ghost block\" data-a=\"exnew\" data-v=\"editor\">'+ic('plus',16,2.2)+' Vytvořit nový cvik</button>')+'<button class=\"btn ghost block\" data-a=\"close\">Zavřít</button></div>';}",
    "  const pk=UI.pick||[];\n  b+=libFilters()+(list.length?'<div class=\"glass list\">'+list.map(x=>sw?libRow(x,'expicked',ic('swap',16,2)):libRow(x,'extoggle',(pk.includes(x.id)?'<span class=\"tiny num\" style=\"color:var(--accent);font-weight:700\">'+(pk.indexOf(x.id)+1)+'.</span>':'')+'<span class=\"pkbox'+(pk.includes(x.id)?' on':'')+'\">'+(pk.includes(x.id)?ic('check',15,3):'')+'</span>')).join('')+'</div>':'<div class=\"glass card empty\">Nic takového v knihovně není.</div>')+(sw?'':'<button class=\"btn ghost block\" data-a=\"exnew\" data-v=\"editor\">'+ic('plus',16,2.2)+' Vytvořit nový cvik</button>')+(sw?'<button class=\"btn ghost block\" data-a=\"close\">Zavřít</button>':'<div style=\"position:sticky;bottom:-26px;padding:10px 0 2px;margin-bottom:-6px;background:linear-gradient(transparent,var(--glass-strong) 30%)\"><button class=\"btn ink block\" data-a=\"expickdone\"'+(pk.length?'':' disabled style=\"opacity:.5\"')+'>'+(pk.length?'Přidat '+pk.length+' '+pl(pk.length,'cvik','cviky','cviků'):'Vyber cviky')+'</button></div>')+'</div>';}")
rep("'+(sw?esc(cur.name):'Vyber cvik do šablony')+'","'+(sw?esc(cur.name):'Vyber cviky do šablony')+'")

# ---------- actions ----------
rep(" expickopen(){UI.exq='';UI.exm='';UI.exe='';UI.sheet={type:'expick',mode:'add'};rerender();},",
    r""" expickopen(){UI.exq='';UI.exm='';UI.exe='';UI.pick=[];UI.sheet={type:'expick',mode:'add'};rerender();},
 extoggle(id){const p=UI.pick=UI.pick||[];const k=p.indexOf(id);if(k>=0)p.splice(k,1);else p.push(id);rerender();},
 expickdone(){const p=UI.pick||[];if(!p.length)return;UI.sheet=null;p.forEach(id=>{const x=libById(id);if(x)addDraftEx(x.name);});UI.pick=[];rerender();toast(p.length===1?'Cvik přidán':p.length+' '+pl(p.length,'cvik','cviky','cviků')+' přidáno');},
 exedit(id){UI.exAdv=false;UI.sheet={type:'exedit',id:id};rerender();},
 exsets(v){const e=edEx();if(!e)return;if(+v<0){if(e.sets.length>1)e.sets.pop();}else{const l=e.sets[e.sets.length-1]||{reps:'10',int:''};e.sets.push({reps:l.reps,int:l.int==='Rozcvička'?'':l.int});}rerender();},
 exreps(v){const e=edEx();if(!e)return;const tm=exTimed(e),step=tm?5:1;const work=e.sets.filter(x=>x.int!=='Rozcvička');const base=parseInt((work[0]||e.sets[0]).reps)||(tm?30:10);const n=Math.max(1,base+ +v*step);
  (work.length?work:e.sets).forEach(x=>{x.reps=tm?n+' s':String(n);});rerender();},
 exfree(){const e=edEx();if(!e)return;const work=e.sets.filter(x=>x.int!=='Rozcvička'),ws=work.length?work:e.sets;const free=ws.every(x=>!String(x.reps||'').trim());
  ws.forEach(x=>{x.reps=free?'10':'';if(!free&&!x.int)x.int='Selhání';});rerender();},
 exint(k){const e=edEx();if(!e)return;const x=e.sets[+k];const order=['','3 RIR','2 RIR','1 RIR','Selhání','Rozcvička'];x.int=order[(order.indexOf(x.int||'')+1)%order.length];rerender();},
 exintall(v){const e=edEx();if(!e)return;e.sets.forEach(x=>{if(x.int!=='Rozcvička')x.int=v;});rerender();},
 exwarm(){const e=edEx();if(!e)return;if(e.sets[0]&&e.sets[0].int==='Rozcvička'){e.sets.shift();if(!e.sets.length)e.sets.push({reps:'10',int:''});}else{const f=e.sets[0]||{reps:'10'};e.sets.unshift({reps:String(f.reps||'').trim()?f.reps:'10',int:'Rozcvička'});}rerender();},
 exadv(){UI.exAdv=true;rerender();},
 exrest(v){const e=edEx();if(!e)return;e.rest=+v;delete e.restTxt;rerender();},
 tplcopydo(id){const t=tpl(id);if(!t)return;t.ex.forEach(e=>{const c=JSON.parse(JSON.stringify(e));c.id=uid();UI.draft.ex.push(c);});UI.sheet=null;rerender();toast(t.ex.length+' '+pl(t.ex.length,'cvik','cviky','cviků')+' z „'+t.name+'“');},""")
rep(" plus:'<path d=\"M12 5v14M5 12h14\"/>'"," plus:'<path d=\"M12 5v14M5 12h14\"/>',minus:'<path d=\"M5 12h14\"/>'")
rep(" exadd(v){"," exadd(v){if(v){addDraftEx(v);rerender();return;}")
rep("function newDraft(t){",r"""function edEx(){return UI.sheet&&UI.draft?UI.draft.ex.find(x=>x.id===UI.sheet.id):null;}
function addDraftEx(name){const lx=libByName(name),tm=lx&&lx.m==='time';UI.draft.ex.push({id:uid(),name:name,sets:[0,1,2].map(()=>({reps:tm?'40 s':'10',int:''})),rest:tm?30:90,note:'',media:[]});}
function newDraft(t){""")
# deleting or moving inside the sheet keeps the sheet sensible
rep(" exdel(id){UI.draft.ex=UI.draft.ex.filter(e=>e.id!==id);rerender();},"," exdel(id){UI.draft.ex=UI.draft.ex.filter(e=>e.id!==id);if(UI.sheet&&UI.sheet.id===id)UI.sheet=null;rerender();},")
# open-target sets keep the trainer's RIR as the client's target
rep("rir:p.int==='Rozcvička'?'':(ls&&ls.rir)||p.int||''","rir:p.int==='Rozcvička'?'':(!String(p.reps||'').trim()&&p.int)||(ls&&ls.rir)||p.int||''")
open('src.html','w').write(s)
print('editor ok')
