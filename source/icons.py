import re
p='src.html';s=open(p,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(n,a[:80]); s=s.replace(a,b)
# CSS
rep('.setno{width:28px;','''.mtile{display:grid;place-items:center;flex:none;border-radius:13px;background:color-mix(in srgb,var(--ink3) 10%,transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--ink3) 18%,transparent)}
.mtile.sm{border-radius:7px}.chip .mtile{background:transparent;box-shadow:none;margin:0 2px 0 -6px}.chip{display:inline-flex;align-items:center;gap:4px}
.musec{display:flex;align-items:center;gap:8px;margin:10px 4px 2px;font-size:13px;font-weight:600;color:var(--ink2)}.musec .n{color:var(--ink3);font-weight:500}
.setno{width:28px;''')
# JS helpers
rep('function muCol(m){','''const MCOL={'Hrudník':'#4C8DFF','Záda':'#2FC6A4','Ramena':'#A78BFA','Biceps':'#FF8A4C','Triceps':'#FF5D8F','Předloktí':'#E9A93A','Břicho a střed':'#3FBDF0','Hýždě':'#FF6B6B','Přední stehna':'#2FD08C','Zadní stehna':'#86CC4A','Lýtka':'#7C9CFF','Celé tělo':'#8B9CF5','Kardio':'#FF4D6D'};
const MBACK=['Záda','Triceps','Hýždě','Zadní stehna','Lýtka'];
const MFRONT=[['Ramena','<ellipse cx="12.6" cy="12.6" rx="3.1" ry="2.6"/><ellipse cx="27.4" cy="12.6" rx="3.1" ry="2.6"/>'],['Hrudník','<rect x="14.2" y="10.6" width="5.6" height="5.6" rx="2"/><rect x="20.2" y="10.6" width="5.6" height="5.6" rx="2"/>'],['Břicho a střed','<rect x="15.6" y="17" width="8.8" height="9.6" rx="2.4"/>'],['Biceps','<ellipse cx="10.4" cy="18.6" rx="2" ry="4"/><ellipse cx="29.6" cy="18.6" rx="2" ry="4"/>'],['Předloktí','<ellipse cx="9" cy="26.6" rx="1.7" ry="3.6"/><ellipse cx="31" cy="26.6" rx="1.7" ry="3.6"/>'],['Přední stehna','<ellipse cx="16.8" cy="34.4" rx="3.1" ry="6.4"/><ellipse cx="23.2" cy="34.4" rx="3.1" ry="6.4"/>'],['Lýtka','<ellipse cx="16.8" cy="44" rx="2" ry="3.3"/><ellipse cx="23.2" cy="44" rx="2" ry="3.3"/>']];
const MREAR=[['Ramena','<ellipse cx="12.6" cy="12.6" rx="3.1" ry="2.6"/><ellipse cx="27.4" cy="12.6" rx="3.1" ry="2.6"/>'],['Záda','<path d="M15 10.4h10l1.4 3-2 9.6h-8.8l-2-9.6z"/>'],['Triceps','<ellipse cx="10.4" cy="18.6" rx="2" ry="4"/><ellipse cx="29.6" cy="18.6" rx="2" ry="4"/>'],['Předloktí','<ellipse cx="9" cy="26.6" rx="1.7" ry="3.6"/><ellipse cx="31" cy="26.6" rx="1.7" ry="3.6"/>'],['Břicho a střed','<rect x="16" y="23.6" width="8" height="3" rx="1.4"/>'],['Hýždě','<ellipse cx="17" cy="29.4" rx="3.2" ry="2.8"/><ellipse cx="23" cy="29.4" rx="3.2" ry="2.8"/>'],['Zadní stehna','<ellipse cx="16.8" cy="36.6" rx="2.9" ry="4.6"/><ellipse cx="23.2" cy="36.6" rx="2.9" ry="4.6"/>'],['Lýtka','<ellipse cx="16.8" cy="44" rx="2.2" ry="3.4"/><ellipse cx="23.2" cy="44" rx="2.2" ry="3.4"/>']];
function bodySvg(mu,sec,h){sec=sec||[];const c=MCOL[mu]||'var(--ink2)',all=mu==='Celé tělo'||mu==='Kardio',base='style="fill:var(--ink3);opacity:.32"';
 const f=m=>all?'style="fill:'+c+';opacity:'+(mu==='Kardio'?.55:.85)+'"':m===mu?'style="fill:'+c+'"':sec.includes(m)?'style="fill:'+c+';opacity:.42"':base;
 const parts=MBACK.includes(mu)?MREAR:MFRONT;let g=parts.map(p=>'<g '+f(p[0])+'>'+p[1]+'</g>').join('');
 if(mu==='Kardio')g+='<path d="M20 22.6s-4.2-2.6-4.2-5.6a2.3 2.3 0 014.2-1.3 2.3 2.3 0 014.2 1.3c0 3-4.2 5.6-4.2 5.6z" fill="'+c+'"/>';
 return '<svg width="'+Math.round(h*40/48)+'" height="'+h+'" viewBox="0 0 40 48" aria-hidden="true"><circle cx="20" cy="5.2" r="3.4" '+(all?f(''):base)+'/>'+g+'</svg>';}
function muTile(mu,sec,sz){sz=sz||40;if(!MCOL[mu])return '<span class="mtile" style="width:'+sz+'px;height:'+sz+'px;color:var(--ink2)">'+ic('dumbbell',Math.round(sz*.45))+'</span>';return '<span class="mtile'+(sz<26?' sm':'')+'" style="width:'+sz+'px;height:'+sz+'px" title="'+esc(mu)+'">'+bodySvg(mu,sec,Math.round(sz*(sz<26?.9:.84)))+'</span>';}
function exMuTile(name,sz){const x=libByName(name);return x?muTile(x.mu,x.sec,sz):muTile('',null,sz);}
function libGrouped(list,rowFn){if(UI.exm||(UI.exq||'').trim())return '<div class="glass list">'+list.map(rowFn).join('')+'</div>';
 return MUSCLES.map(m=>{const g=list.filter(x=>x.mu===m);return g.length?'<div class="musec">'+muTile(m,null,22)+esc(m)+' <span class="n">'+g.length+'</span></div><div class="glass list">'+g.map(rowFn).join('')+'</div>':'';}).join('');}
function libMuNote(){return UI.exm?'<div class="tiny faint" style="margin:0 4px;line-height:1.4">Jen cviky, kde je '+esc(UI.exm.toLowerCase())+' hlavní sval. Vedlejší partie jsou u cviku jen pro informaci.</div>':'';}
function muCol(m){''')
# filter: primary muscle only, search ignores secondary
rep("(x.name+' '+x.mu+' '+x.eq+' '+x.sec.join(' ')).toLowerCase().includes(q))&&(!UI.exm||x.mu===UI.exm||x.sec.includes(UI.exm))","(x.name+' '+x.mu+' '+x.eq).toLowerCase().includes(q))&&(!UI.exm||x.mu===UI.exm)")
# sort library by muscle order then name
rep(".sort((a,b)=>a.name.localeCompare(b.name,'cs'));}\nfunction libById",".sort((a,b)=>(MUSCLES.indexOf(a.mu)-MUSCLES.indexOf(b.mu))||a.name.localeCompare(b.name,'cs'));}\nfunction libById")
# lib row
rep("""function libRow(x,act,trail){const col=muCol(x.mu);return '<button class="li" data-a="'+act+'" data-v="'+x.id+'"><span class="iconbtn sm" style="background:color-mix(in srgb,'+col+' 16%,transparent);color:'+col+';flex:none">'+ic(x.m==='time'?'clock':'dumbbell',18)+'</span>""","""function libRow(x,act,trail){return '<button class="li" data-a="'+act+'" data-v="'+x.id+'">'+muTile(x.mu,x.sec,42)+'""")
rep("""<div class="tiny muted ellip">'+esc(x.mu)+' · '+esc(x.eq)+(x.m==='time'?' · na čas':'')+'</div></div>'+(trail||'')""","""<div class="tiny muted ellip"><b style="color:'+(MCOL[x.mu]||'inherit')+';font-weight:600">'+esc(x.mu)+'</b> · '+esc(x.eq)+(x.m==='time'?' · na čas':'')+'</div>'+(x.sec&&x.sec.length?'<div class="tiny faint ellip">Vedlejší: '+esc(x.sec.join(', '))+'</div>':'')+'</div>'+(trail||'')""")
# chips with mini icon
rep("""data-a="exmu" data-v="'+m+'">'+(m||'Všechny partie')+'</button>'""","""data-a="exmu" data-v="'+m+'">'+(m?muTile(m,null,22):'')+(m||'Všechny partie')+'</button>'""")
# lib body grouped
rep("""list.length+' '+pl(list.length,'cvik','cviky','cviků')+'</div>'+(list.length?'<div class="glass list">'+list.map(x=>libRow(x,act,ic('chev',18))).join('')+'</div>':""","""list.length+' '+pl(list.length,'cvik','cviky','cviků')+'</div>'+libMuNote()+(list.length?libGrouped(list,x=>libRow(x,act,ic('chev',18))):""")
# picker grouped
rep("""b+=libFilters()+(list.length?'<div class="glass list">'+list.map(x=>sw?""","""b+=libFilters()+libMuNote()+(list.length?libGrouped(list,x=>sw?""")
rep("""'<span class="pkbox'+(pk.includes(x.id)?' on':'')+'">'+(pk.includes(x.id)?ic('check',15,3):'')+'</span>')).join('')+'</div>':""","""'<span class="pkbox'+(pk.includes(x.id)?' on':'')+'">'+(pk.includes(x.id)?ic('check',15,3):'')+'</span>')):""")
# exercise info
rep("""<span class="iconbtn" style="background:color-mix(in srgb,'+muCol(x.mu)+' 16%,transparent);color:'+muCol(x.mu)+'">'+ic(x.m==='time'?'clock':'dumbbell',22)+'</span>""","""'+muTile(x.mu,x.sec,60)+'""")
# editor rows: icon instead of number
rep("""'<button class="edrow" data-a="exedit" data-v="'+e.id+'"><span class="setno" style="flex:none">'+(i+1)+'</span>""","""'<button class="edrow" data-a="exedit" data-v="'+e.id+'">'+exMuTile(e.name,40)+'""")
# template detail
rep("""<span class="num faint" style="width:18px">'+(i+1)+'</span><div class="title-m grow ellip">'+esc(e.name)""","""'+exMuTile(e.name,36)+'<div class="title-m grow ellip">'+esc(e.name)""")
# workout list rows: small icon before name
rep("""'</span><span class="grow" style="min-width:0"><span class="ellip" style="display:block;font-weight:600">'+esc(e.name)+'</span><span class="tiny muted ellip" style="display:block">'+sub""","""'</span>'+exMuTile(e.name,34)+'<span class="grow" style="min-width:0"><span class="ellip" style="display:block;font-weight:600">'+esc(e.name)+'</span><span class="tiny muted ellip" style="display:block">'+sub""")
open(p,'w',encoding='utf-8').write(s);print('ok')
