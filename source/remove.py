#!/usr/bin/env python3
# Trainer can remove a client; owner can remove a trainer together with all their clients. Clients left without a trainer get a join-by-code screen.
s=open('src.html').read()
def rep(old,new):
    global s
    assert s.count(old)==1, ('anchor',s.count(old),old[:70])
    s=s.replace(old,new)

# a missing trainer never crashes a screen
rep("get(){return S.trainers.find(t=>t.id===S.me);}});",
    "get(){return S.trainers.find(t=>t.id===S.me)||{id:S.me,name:'Trenér',spec:'',code:'',email:'',photo:null};}});")

# trainer: remove button at the bottom of a client's detail
rep(" }\n h+='</div></div>';return h;\n}\n\nfunction statsBlocks",
    " }\n h+='<button class=\"btn danger block\" style=\"margin-top:10px\" data-a=\"rmclient\" data-v=\"'+id+'\">'+ic('logout',18)+' Odebrat svěřence</button>';\n h+='</div></div>';return h;\n}\n\nfunction statsBlocks")

# owner: remove button on a trainer's detail (not on the owner's own account)
rep("Poznámky a chat mezi trenérem a klientem zůstávají soukromé.</p>';\n h+='</div></div>';return h;",
    "Poznámky a chat mezi trenérem a klientem zůstávají soukromé.</p>';\n if(!t.owner&&t.id!==S.me)h+='<button class=\"btn danger block\" data-a=\"rmtrainer\" data-v=\"'+t.id+'\">'+ic('logout',18)+' Odebrat trenéra</button>';\n h+='</div></div>';return h;")

# client without a trainer
rep("function scrCHome(){",r"""function scrCNoTrainer(){const c=me();
 let h='<div class="view" id="view"><div class="stack" style="padding-top:36px;align-items:center;text-align:center;gap:14px">'+avatar(c,84)+'<span class="eyebrow">Bez trenéra</span><h1 class="title-xl">Zatím nemáš trenéra</h1><p class="muted" style="margin:0;line-height:1.5;max-width:310px">Už nejsi propojený(á) s žádným trenérem. Historie tréninků i váhy ti zůstala. Zadej kód nového trenéra a hned se propojíte.</p></div>';
 h+='<div class="glass card stack" style="margin-top:18px"><input class="input num" id="nt-code" data-in="ccode" value="'+esc(UI.ccode||'')+'" placeholder="Kód trenéra" maxlength="8" autocomplete="off" style="letter-spacing:.12em;font-weight:600;font-size:20px;text-align:center'+(UI.ccodeErr?';border-color:var(--bad)':'')+'">'+(UI.ccodeErr?'<div class="small" style="color:var(--bad)">'+esc(UI.ccodeErr)+'</div>':'<span class="tiny faint">Kód ti pošle trenér. Najde ho ve svém profilu.</span>')+'<button class="btn ink block" data-a="ccodesave">Připojit k trenérovi</button></div>';
 h+='<div class="glass list" style="margin-top:6px"><button class="li plain" data-a="open" data-v="settings"><span class="iconbtn sm" style="background:var(--chip)">'+ic('gear',18)+'</span><span class="grow" style="font-weight:500">Nastavení</span>'+ic('chev',18)+'</button><button class="li plain" data-a="open" data-v="report"><span class="iconbtn sm" style="background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn)">'+ic('bug',18)+'</span><span class="grow" style="font-weight:500">Nahlásit problém</span>'+ic('chev',18)+'</button><button class="li plain" data-a="logout" style="color:var(--bad)"><span class="grow">Odhlásit se</span>'+ic('logout',18)+'</button></div>';
 h+=demoSwitch();
 h+='</div>';return h;}
function scrCHome(){""")
rep("  if(isC()){\n   if(top){",
    "  if(isC()&&!me().trainerId&&!(top==='settings'||top==='report')){S.active=null;h=scrCNoTrainer();}\n  else if(isC()){\n   if(top){")

# actions
rep(" confirm(){const r=UI.sheet.run;UI.sheet=null;r();},",r""" confirm(){const r=UI.sheet.run;UI.sheet=null;r();},
 rmclient(id){const c=client(id);if(!c)return;const n=c.name.split(' ')[0];
  UI.sheet={type:'confirm',title:'Odebrat '+c.name+'?',text:n+' se od tebe odpojí. Smažou se přiřazené tréninky, vaše zprávy a tvoje poznámky k němu/ní. Účet i historie tréninků mu/jí zůstanou a může se připojit k jinému trenérovi.',ok:'Odebrat svěřence',run:()=>removeClient(id)};rerender();},
 rmtrainer(id){const t=S.trainers.find(x=>x.id===id);if(!t||t.owner||S.role!=='owner')return;const n=S.clientsAll.filter(c=>c.trainerId===id).length;
  UI.sheet={type:'confirm',title:'Odebrat trenéra '+t.name+'?',text:'Trenér přijde o účet a smažou se jeho šablony a vlastní cviky. '+(n?'Odpojí se i '+(n===1?'jeho 1 klient':'všech jeho '+n+' '+pl(n,'klient','klienti','klientů'))+', smažou se jim přiřazené tréninky a zprávy s trenérem. Historie tréninků klientům zůstane a mohou se připojit k jinému trenérovi.':'Nemá žádné klienty.'),ok:'Odebrat trenéra',run:()=>removeTrainer(id)};rerender();},""")
rep("function me(){return client(S.cme);}",r"""function me(){return client(S.cme);}
function detachClient(id){const c=client(id);if(!c)return;c.trainerId=null;S.assign=S.assign.filter(a=>a.clientId!==id);S.notes[id]=[];S.messages[id]=[];}
function leaveScreens(ids){UI.stack=UI.stack.filter(x=>!ids.some(id=>x.endsWith(':'+id)));}
function removeClient(id){const c=client(id);if(!c)return;detachClient(id);save();leaveScreens([id]);render('pop');toast(c.name+' už není tvůj svěřenec');}
function removeTrainer(id){const t=S.trainers.find(x=>x.id===id);if(!t)return;const cs=S.clientsAll.filter(c=>c.trainerId===id).map(c=>c.id);cs.forEach(detachClient);
 S.trainers=S.trainers.filter(x=>x.id!==id);S.templatesAll=S.templatesAll.filter(x=>x.tr!==id);S.exCustom=(S.exCustom||[]).filter(x=>x.tr!==id);save();leaveScreens([id].concat(cs));render('pop');toast('Trenér '+t.name+' byl odebrán');}""")

# demo: switching apps and signing in still work after removals
rep(" astrainer(){S.me=me().trainerId;"," astrainer(){S.me=me().trainerId||'own';")
rep("if(t){S.me=t.id;S.role=t.owner?'owner':'trainer';}else{S.me='tr1';S.role='trainer';}",
    "if(t){S.me=t.id;S.role=t.owner?'owner':'trainer';}else if(S.trainers.some(x=>x.id==='tr1')){S.me='tr1';S.role='trainer';}else{toast('Tento účet byl odebrán.');return;}")
rep("  S.role='trainer';S.me='tr1';S.trainer.name=",
    "  if(!S.trainers.some(x=>x.id==='tr1'))S.trainers.push({id:'tr1',name:'Trenér',email:'',spec:'',bio:'',code:genCode(),photo:null,joined:new Date().toISOString()});\n  S.role='trainer';S.me='tr1';S.trainer.name=")
open('src.html','w').write(s)
print('remove ok')
