#!/usr/bin/env python3
# Owner Trainers tab: "Trenérů v aplikaci" jumps to the trainer list, "Klientů celkem" opens a list of all clients.
s=open('src.html').read()
def rep(old,new):
    global s
    assert s.count(old)==1, ('anchor',s.count(old),old[:70])
    s=s.replace(old,new)
rep("+'<div class=\"glass kpi\"><span class=\"l\">Trenérů v aplikaci</span><span class=\"v num\">'+S.trainers.length+'</span><span class=\"tiny faint\">'+S.trainers.filter(t=>daysAgo(t.joined)<=30).length+' nových za 30 dní</span></div>'",
    "+'<button class=\"glass kpi\" data-a=\"scrollto\" data-v=\"trlist\" style=\"text-align:left\"><span class=\"l\">Trenérů v aplikaci</span><span class=\"v num\">'+S.trainers.length+'</span><span class=\"tiny faint\">'+S.trainers.filter(t=>daysAgo(t.joined)<=30).length+' nových za 30 dní</span></button>'")
rep("+'<div class=\"glass kpi\"><span class=\"l\">Klientů celkem</span><span class=\"v num\">'+total+'</span><span class=\"tiny faint\">'+fresh+' nových za 30 dní</span></div>'",
    "+'<button class=\"glass kpi\" data-a=\"open\" data-v=\"allclients\" style=\"text-align:left\"><span class=\"l\">Klientů celkem</span><span class=\"v num\">'+total+'</span><span class=\"tiny faint\">'+fresh+' nových za 30 dní</span></button>'")
rep("h+='<div class=\"sec\"><h3>Všichni trenéři</h3>","h+='<div class=\"sec\" id=\"trlist\" style=\"scroll-margin-top:16px\"><h3>Všichni trenéři</h3>")
rep("function scrAttendance(){",r"""function scrAllClients(){
 const q=(UI.acq||'').trim().toLowerCase(),f=UI.acf||'all';
 const all=S.clientsAll.filter(c=>c.trainerId&&S.trainers.some(t=>t.id===c.trainerId)&&c.status==='active');
 const tn=c=>(S.trainers.find(t=>t.id===c.trainerId)||{}).name||'';
 const rows=all.filter(c=>(f==='all'||c.trainerId===f)&&(!q||(c.name+' '+c.goal+' '+tn(c)).toLowerCase().includes(q))).sort((a,b)=>a.name.localeCompare(b.name,'cs'));
 const trs=S.trainers.filter(t=>all.some(c=>c.trainerId===t.id));
 let h='<div class="view detail" id="view">'+nav('Klienti')+'<div class="stack"><h1 class="title-xl">Všichni klienti</h1><p class="muted" style="margin:-4px 2px 0">'+all.length+' '+pl(all.length,'klient','klienti','klientů')+' u '+trs.length+' '+pl(trs.length,'trenéra','trenérů','trenérů')+'.</p>';
 h+='<input class="input" id="ac-q" data-in="acq" type="search" placeholder="Hledat klienta nebo trenéra" value="'+esc(UI.acq||'')+'">';
 h+='<div class="row" style="gap:6px;overflow-x:auto;padding-bottom:2px">'+[['all','Všichni']].concat(trs.map(t=>[t.id,t.id===S.me?'Moji':t.name.split(' ')[0]])).map(x=>'<button class="chip'+(f===x[0]?' on':'')+'" data-a="acf" data-v="'+x[0]+'">'+esc(x[1])+'</button>').join('')+'</div>';
 h+=rows.length?'<div class="glass list" id="ac-list">'+rows.map(c=>{const mine=c.trainerId===S.me,d=lastDays(c.id);return '<button class="li" data-a="'+(mine?'open':'opentrainer')+'" data-v="'+(mine?'client:'+c.id:c.trainerId)+'">'+avatar(c,40)+'<div class="grow" style="min-width:0"><div class="ellip" style="font-weight:500">'+esc(c.name)+'</div><div class="tiny muted ellip">'+(mine?'Tvůj klient':ic('person',12)+' '+esc(tn(c)))+'</div><div class="tiny faint">'+(d===null?'Zatím bez tréninku':'Trénoval(a) '+rel(sessOf(c.id)[0].date))+'</div></div>'+ring(adherence(c.id),38)+'</button>';}).join('')+'</div>':'<div class="glass card empty">Nikoho takového jsme nenašli.</div>';
 h+='<p class="tiny faint" style="text-align:center;margin:4px 20px">Klepnutím na cizího klienta otevřeš jeho trenéra. Poznámky a chat zůstávají soukromé.</p>';
 h+='</div></div>';return h;
}
function scrAttendance(){""")
rep("k==='attendance'?scrAttendance():","k==='attendance'?scrAttendance():k==='allclients'&&S.role==='owner'?scrAllClients():")
rep(" opentrainer(v){push('trainer:'+v);},",""" opentrainer(v){push('trainer:'+v);},
 scrollto(v){const el=document.getElementById(v);if(el)el.scrollIntoView({behavior:REDUCED?'auto':'smooth',block:'start'});},
 acf(v){UI.acf=v;rerender();},""")
rep(" if(k==='tq'){"," if(k==='acq'){UI.acq=v;const pos=e.target.selectionStart;rerender();const q=document.getElementById('ac-q');if(q){q.focus();try{q.setSelectionRange(pos,pos);}catch(_){}}return;}\n if(k==='tq'){")
open('src.html','w').write(s)
print('owner ok')
