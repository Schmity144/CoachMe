p='src.html';s=open(p,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(n,a[:80]); s=s.replace(a,b)
# home: Začít trénink opens the picker of shared templates
rep("""data-a="wostart" data-v="'+nt.id+'">'+ic('play',18)+' Začít trénink</button>""","""data-a="sheet" data-v="cpick">'+ic('play',18)+' Začít trénink</button>""")
# helper: muscles of a template
rep("function exMuTile(name,sz){","""function tplMuscles(t){const m=[];t.ex.forEach(e=>{const x=libByName(e.name);if(x&&!m.includes(x.mu))m.push(x.mu);});return m;}
function exMuTile(name,sz){""")
# sheet
rep(" if(sh.type==='tplcopy'){",""" if(sh.type==='cpick'){const p=myPlan(),np=nextPlan();
  b='<div class="stack"><div><span class="eyebrow">Od trenéra '+esc(S.trainer.name.split(' ')[0])+'</span><div class="title-l" style="margin-top:4px">Jaký trénink dnes?</div><div class="tiny muted" style="margin-top:2px">Klepni na trénink a časomíra se hned spustí.</div></div>'
   +(p.length?'<div class="stack" style="gap:10px">'+p.map(a=>{const t=tpl(a.templateId);if(!t)return '';const ld=lastDone(t.id),mu=tplMuscles(t),nx=np&&np.templateId===t.id;
    return '<div class="glass card" style="padding:12px 12px 12px 14px;'+(nx?'box-shadow:inset 0 0 0 1.5px var(--accent)':'')+'"><div class="row" style="gap:12px;align-items:center"><button class="row grow" style="gap:12px;text-align:left;min-width:0" data-a="wostart" data-v="'+t.id+'">'
     +'<span class="row" style="flex:none">'+mu.slice(0,3).map((m,i)=>'<span style="margin-left:'+(i?-14:0)+'px;border-radius:13px;background:var(--glass-strong)">'+muTile(m,null,38)+'</span>').join('')+(mu.length?'':muTile('',null,38))+'</span>'
     +'<span class="grow" style="min-width:0"><span class="row" style="gap:6px"><span class="ellip" style="font-weight:600">'+esc(t.name)+'</span>'+(nx?'<span class="pill" style="flex:none;background:color-mix(in srgb,var(--accent) 16%,transparent);color:var(--accent)">Na řadě</span>':'')+'</span>'
     +'<span class="tiny muted ellip" style="display:block;margin-top:2px">'+(mu.length?esc(mu.slice(0,3).join(', '))+' · ':'')+t.ex.length+' '+pl(t.ex.length,'cvik','cviky','cviků')+'</span>'
     +'<span class="tiny faint" style="display:block">'+(ld?'naposledy '+rel(ld):'zatím necvičeno')+'</span></span></button>'
     +'<button class="iconbtn sm" style="background:var(--chip);flex:none" data-a="open" data-v="template:'+t.id+'" aria-label="Detail tréninku">'+ic('chev',18)+'</button></div>'
     +(a.note?'<div class="tiny muted" style="margin-top:8px;line-height:1.4">„'+esc(a.note)+'“</div>':'')+'</div>';}).join('')+'</div>':'<div class="glass card empty">Trenér ti zatím neposlal žádný trénink.</div>')
   +'<button class="btn ghost block" data-a="close">Zavřít</button></div>';}
 if(sh.type==='tplcopy'){""")
open(p,'w',encoding='utf-8').write(s);print('ok')
