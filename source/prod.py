#!/usr/bin/env python3
# Turns the demo (src.html) into the production app (prod.html) backed by Supabase.
import re,sys
s=open('src.html').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    assert n>=1, 'anchor not found: '+old[:80]
    if count==1: assert n==1, 'anchor not unique (%d): %s'%(n,old[:80])
    s=s.replace(old,new) if count!=1 else s.replace(old,new,1)
def cut(start,end,new=''):
    """replace text from start anchor up to (not incl.) end anchor"""
    global s
    i=s.index(start);j=s.index(end,i)
    s=s[:i]+new+s[j:]

# ---------- page chrome ----------
rep('<h1>CoachMe pro trenéry</h1>','<h1>CoachMe</h1>')
cut('<div>Interaktivní demo.','  </div>\n  <div class="phone">',
 '<div>Aplikace pro trenéry a jejich klienty. Na telefonu ji otevřeš přes prohlížeč a přidáš na plochu.</div>\n    <div class="hint"><b>Trenér</b> si vytvoří účet a dostane kód.</div>\n    <div class="hint"><b>Klient</b> se zaregistruje s kódem trenéra a hned se propojí.</div>\n')
rep('<script>\n(function(){','<script src="supabase.js"></script>\n<script>\n(function(){')

# ---------- state: no seed, local prefs only ----------
cut('/* ---------- state ---------- */','function save(){',r'''/* ---------- state ---------- */
const KEY='coachme-local-v1';
const SB_URL='https://iqrtiypkczsarqimbnqj.supabase.co',SB_KEY='sb_publishable_fsdwgYn2Uvw0jtQw2pqcfg_M1m_1tR0';
const sb=window.supabase.createClient(SB_URL,SB_KEY,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
const LOCAL_KEYS=['theme','units','notif','cnotif','restOn','active','activeFor','guide','lang','exFav'];
function blank(){return {v:7,authed:false,role:'trainer',me:null,cme:null,uid:null,theme:'system',trainers:[],clientsAll:[],templatesAll:[],sessions:[],metrics:[],assign:[],messages:{},notes:{},exCustom:[],reports:[]};}
let S=blank();
function loadLocal(){try{const L=JSON.parse(localStorage.getItem(KEY)||'null');if(L)LOCAL_KEYS.forEach(k=>{if(L[k]!==undefined)S[k]=L[k];});}catch(e){}}
loadLocal();
/* views scoped to the signed-in account; not saved (non-enumerable) */
function bindS(){
 Object.defineProperty(S,'trainer',{configurable:true,enumerable:false,get(){return S.trainers.find(t=>t.id===S.me)||{id:S.me,name:'Trenér',spec:'',code:'',photo:null};}});
 Object.defineProperty(S,'clients',{configurable:true,enumerable:false,get(){return S.clientsAll.filter(c=>c.trainerId===S.me);}});
 Object.defineProperty(S,'templates',{configurable:true,enumerable:false,get(){return S.templatesAll.filter(t=>t.tr===S.me&&!t.cl);},set(v){S.templatesAll=S.templatesAll.filter(t=>t.tr!==S.me||t.cl).concat(v);}});
}
bindS();
function ensureSettings(){if(!S.cnotif)S.cnotif={on:true,plan:true,message:true,comment:true};if(!S.units)S.units='kg';if(!S.notif)S.notif={on:true,workout:true,client:true,message:true};if(!S.exCustom)S.exCustom=[];if(!S.reports)S.reports=[];}
ensureSettings();

/* ---------- Supabase sync ---------- */
/* Each table holds one app object per row in `data`; scoping columns drive row-level security. */
function strip(o,keys){const c={};Object.keys(o).forEach(k=>{if(!keys.includes(k)&&o[k]!==undefined)c[k]=o[k];});return c;}
function stable(v){if(Array.isArray(v))return '['+v.map(stable).join(',')+']';if(v&&typeof v==='object'){return '{'+Object.keys(v).filter(k=>v[k]!==undefined).sort().map(k=>JSON.stringify(k)+':'+stable(v[k])).join(',')+'}';}return JSON.stringify(v===undefined?null:v);}
const byAt=(a,b)=>String(a.data.at||'').localeCompare(String(b.data.at||''));
/* templates/exercises: a trainer writes the rows under their id (incl. comments on clients' own rows); a client writes only rows they made, tied to their current trainer */
function ownRows(list){return (isC()?list.filter(t=>t.cl===S.uid):list.filter(t=>t.tr===S.uid)).map(t=>({id:t.id,trainer_id:isC()?(S.me||null):t.tr,client_id:t.cl||null,data:strip(t,['id','tr','cl'])}));}
function fromOwnRow(r){const o=Object.assign({},r.data,{id:r.id,tr:r.trainer_id});if(r.client_id)o.cl=r.client_id;return o;}
const TB={
 trainers:{cols:['id','data'],get:()=>S.trainers.filter(t=>t.id===S.uid).map(t=>({id:t.id,data:strip(t,['id','code','owner'])})),
  set:rows=>{S.trainers=rows.map(r=>Object.assign({},r.data,{id:r.id,code:r.code,owner:!!r.is_owner}));}},
 clients:{cols:['id','data'],get:()=>S.clientsAll.filter(c=>c.id===S.uid||c.trainerId===S.uid).map(c=>({id:c.id,data:strip(c,['id','trainerId'])})),
  set:rows=>{S.clientsAll=rows.map(r=>Object.assign({},r.data,{id:r.id,trainerId:r.trainer_id}));}},
 templates:{cols:['id','trainer_id','client_id','data'],get:()=>ownRows(S.templatesAll),
  set:rows=>{S.templatesAll=rows.map(fromOwnRow);}},
 exercises:{cols:['id','trainer_id','client_id','data'],get:()=>ownRows(S.exCustom),
  set:rows=>{S.exCustom=rows.map(fromOwnRow);}},
 sessions:{cols:['id','client_id','data'],get:()=>S.sessions.map(x=>({id:x.id,client_id:x.clientId,data:strip(x,['id','clientId'])})),
  set:rows=>{S.sessions=rows.map(r=>Object.assign({},r.data,{id:r.id,clientId:r.client_id}));}},
 metrics:{cols:['id','client_id','data'],get:()=>S.metrics.map(x=>{if(!x.id)x.id='m'+uid()+uid();return {id:x.id,client_id:x.clientId,data:strip(x,['id','clientId'])};}),
  set:rows=>{S.metrics=rows.map(r=>Object.assign({},r.data,{id:r.id,clientId:r.client_id}));}},
 assignments:{cols:['id','client_id','data'],get:()=>S.assign.map(x=>({id:x.id,client_id:x.clientId,data:strip(x,['id','clientId'])})),
  set:rows=>{S.assign=rows.map(r=>Object.assign({},r.data,{id:r.id,clientId:r.client_id}));}},
 messages:{cols:['id','client_id','data'],get:()=>Object.keys(S.messages).flatMap(cid=>(S.messages[cid]||[]).map(m=>({id:m.id,client_id:cid,data:strip(m,['id'])}))),
  set:rows=>{const o={};rows.slice().sort(byAt).forEach(r=>{(o[r.client_id]=o[r.client_id]||[]).push(Object.assign({},r.data,{id:r.id}));});S.messages=o;}},
 notes:{cols:['id','client_id','trainer_id','data'],get:()=>isC()?[]:Object.keys(S.notes).flatMap(cid=>(S.notes[cid]||[]).map(n=>({id:n.id,client_id:cid,trainer_id:S.uid,data:strip(n,['id'])}))),
  set:rows=>{const o={};rows.slice().sort(byAt).forEach(r=>{(o[r.client_id]=o[r.client_id]||[]).push(Object.assign({},r.data,{id:r.id}));});S.notes=o;}},
 reports:{cols:['id','data'],get:()=>S.reports.map(x=>({id:x.id,data:strip(x,['id'])})),
  set:rows=>{S.reports=rows.map(r=>Object.assign({},r.data,{id:r.id}));}}
};
const TABLES=Object.keys(TB);
const ROWS={},SNAP={};TABLES.forEach(t=>{ROWS[t]=new Map();SNAP[t]=new Map();});
function pick(t,r){const o={};TB[t].cols.forEach(c=>{if(r[c]!==undefined)o[c]=r[c];});return o;}
function ensureBuckets(){S.clientsAll.forEach(c=>{if(!S.messages[c.id])S.messages[c.id]=[];if(!S.notes[c.id])S.notes[c.id]=[];});}
function materialize(){TABLES.forEach(t=>TB[t].set([...ROWS[t].values()]));ensureBuckets();}
function snapshot(){TABLES.forEach(t=>{SNAP[t]=new Map(TB[t].get().map(r=>[r.id,stable(r)]));});}
let flushT=null,flushing=Promise.resolve(),saveErr=0;const SOK=new Set();
function restoreOutbox(){try{const L=JSON.parse(localStorage.getItem(KEY)||'null');const ob=(L&&L.outbox)||[];let n=0;ob.forEach(x=>{if(x&&x.clientId===S.cme&&!S.sessions.some(y=>y.id===x.id)){S.sessions.push(x);n++;}});if(n){scheduleFlush();}}catch(e){}}
window.addEventListener('online',()=>scheduleFlush());
function scheduleFlush(){if(!S.authed)return;clearTimeout(flushT);flushT=setTimeout(flushNow,350);}
function flushNow(){clearTimeout(flushT);flushT=null;if(!S.authed)return flushing;
 const jobs=[];
 TABLES.forEach(t=>{
  const rows=TB[t].get(),seen=new Set(),ins=[],upd=[];
  rows.forEach(r=>{seen.add(r.id);const str=stable(r),old=SNAP[t].get(r.id);if(old===str)return;(old===undefined?ins:upd).push(r);SNAP[t].set(r.id,str);
   ROWS[t].set(r.id,Object.assign({},ROWS[t].get(r.id)||{},r));});
  const del=[...SNAP[t].keys()].filter(id=>!seen.has(id));
  del.forEach(id=>{SNAP[t].delete(id);ROWS[t].delete(id);});
  const fail=(rs,prev)=>e=>{saveErr++;console.error('CoachMe sync',t,e);rs.forEach(r=>SNAP[t].delete(r.id));if(navigator.onLine)toast('Nepodařilo se uložit, zkusím to znovu');setTimeout(scheduleFlush,navigator.onLine?4000:15000);};
  if(t==='trainers'||t==='clients'){[...ins,...upd].forEach(r=>jobs.push(sb.from(t).update({data:r.data}).eq('id',r.id).then(x=>{if(x.error)fail([r])(x.error);})));}
  else if(t==='reports'&&S.role!=='owner'){if(ins.length)jobs.push(sb.from(t).insert(ins).then(x=>{if(x.error)fail(ins)(x.error);}));}
  else{const all=[...ins,...upd];if(all.length)jobs.push(sb.from(t).upsert(all).then(x=>{if(x.error)fail(all)(x.error);else if(t==='sessions'){all.forEach(r=>SOK.add(r.id));saveLocal();}}));}
  if(del.length&&!(t==='reports'&&S.role!=='owner'))jobs.push(sb.from(t).delete().in('id',del).then(x=>{if(x.error){console.error('CoachMe delete',t,x.error);}}));
 });
 flushing=Promise.all(jobs);return flushing;}
async function fetchAll(t){let out=[],from=0;for(;;){const {data,error}=await sb.from(t).select('*').range(from,from+999);if(error)throw error;out=out.concat(data);if(data.length<1000)break;from+=1000;}return out;}
async function loadAll(){const res=await Promise.all(TABLES.map(t=>fetchAll(t).catch(e=>{console.error('load',t,e);return [];})));
 TABLES.forEach((t,i)=>{ROWS[t]=new Map(res[i].map(r=>[r.id,r]));});ROWS.sessions.forEach((v,k)=>SOK.add(k));materialize();}
/* live updates from other devices */
let chan=null;
function liveRender(){if(!S.authed)return;const ae=document.activeElement,fid=ae&&ae.id,val=ae&&ae.value!==undefined?ae.value:null,pos=ae&&ae.selectionStart;
 if(UI.sheet&&fid){UI.pendingRender=true;return;}
 const c=current();if(c&&c.startsWith('chat:'))render('bottom');else rerender();
 if(fid){const el=document.getElementById(fid);if(el){if(val!=null&&el.value!==val)el.value=val;el.focus();try{el.setSelectionRange(pos,pos);}catch(_){}}}}
document.addEventListener('focusout',()=>{if(UI.pendingRender){setTimeout(()=>{if(UI.pendingRender&&!UI.sheet){UI.pendingRender=false;rerender();}},120);}});
let liveT=null,liveNotes=[];
function applyChange(p){const t=p.table;if(!TB[t])return;
 flushNow();
 if(p.eventType==='DELETE'){const id=p.old&&p.old.id;if(!id||!ROWS[t].has(id))return;ROWS[t].delete(id);SNAP[t].delete(id);}
 else{const r=p.new;const prev=ROWS[t].get(r.id);ROWS[t].set(r.id,r);
  const norm=stable(pick(t,r));if(SNAP[t].get(r.id)===norm&&!(t==='trainers'&&prev&&prev.code!==r.code))return;
  if(t==='clients'&&r.id===S.uid&&r.trainer_id!==S.me){S.me=r.trainer_id;loadAll().then(()=>{snapshot();liveRender();});return;}
  if(p.eventType==='INSERT')liveNotes.push([t,r]);}
 clearTimeout(liveT);liveT=setTimeout(()=>{materialize();snapshot();const ns=liveNotes;liveNotes=[];liveRender();ns.forEach(([t,r])=>liveNotify(t,r));},120);}
function liveNotify(t,r){const d=r.data||{};const c=current()||'';
 if(t==='messages'){const mine=d.by===(isC()?'client':'trainer');if(mine||c==='chat:'+r.client_id)return;
  const from=isC()?S.trainer.name:((client(r.client_id)||{}).name||'Klient');notify('message',from,msgPreview(Object.assign({},d,{id:r.id})),'chat:'+r.client_id);}
 else if(t==='sessions'&&!isC()){const cl=client(r.client_id);if(cl)notify('workout',cl.name.split(' ')[0]+' dokončil(a) trénink',d.title||'Trénink','session:'+r.id);}
 else if(t==='clients'&&!isC()&&r.trainer_id===S.uid){notify('client','Nový klient',(d.name||'Klient')+' se připojil(a) přes tvůj kód','client:'+r.id);}
 else if(t==='assignments'&&isC()){const tp=tpl(d.templateId);notify('plan',S.trainer.name.split(' ')[0]+' ti poslal(a) trénink',tp?tp.name:'Nový trénink','template:'+d.templateId);}}
function subscribe(){if(chan)sb.removeChannel(chan);chan=sb.channel('coachme-'+S.uid).on('postgres_changes',{event:'*',schema:'public'},applyChange).subscribe();}
/* auth: decide role from the database, finish registration from sign-up metadata */
let bootUid=null;
async function boot(session){
 if(!session){S.authed=false;UI.booting=false;render();return;}
 if(bootUid===session.user.id)return;bootUid=session.user.id;
 UI.booting=true;render();
 const uidv=session.user.id;S.uid=uidv;
 let tr=(await sb.from('trainers').select('id,is_owner').eq('id',uidv).maybeSingle()).data;
 let cl=tr?null:(await sb.from('clients').select('id,trainer_id').eq('id',uidv).maybeSingle()).data;
 let fresh=false;
 if(!tr&&!cl){const md=session.user.user_metadata||{};
  if(md.role==='trainer'){const r=await sb.rpc('register_trainer',{p_name:md.name||'',p_spec:md.spec||''});if(r.error)return bootFail('Účet se nepodařilo dokončit. '+r.error.message);tr={id:uidv,is_owner:false};fresh='code';}
  else if(md.role==='client'){const r=await sb.rpc('register_client',{p_code:md.code||'',p_name:md.name||'',p_goal:md.goal||''});if(r.error)return bootFail(/bad code/.test(r.error.message)?'Kód trenéra už neplatí. Požádej trenéra o nový.':'Účet se nepodařilo dokončit.');cl={id:uidv,trainer_id:r.data.id};fresh='cdone';}
  else return bootFail('K tomuto e-mailu nepatří žádný účet CoachMe.');}
 if(tr){S.role=tr.is_owner?'owner':'trainer';S.me=uidv;S.cme=null;}else{S.role='client';S.cme=uidv;S.me=cl.trainer_id;}
 if(S.activeFor!==uidv){S.active=null;S.activeFor=uidv;}
 await loadAll();snapshot();subscribe();if(S.cme)restoreOutbox();
 UI.booting=false;UI.stack=[];UI.tab='home';UI.sheet=null;
 if(fresh){UI.authStep=fresh;S.authed=false;render('push');UI.pendingEnter=true;}else{S.authed=true;applyGo();render();}
 saveLocal();}
function bootFail(msg){bootUid=null;UI.booting=false;S.authed=false;sb.auth.signOut();UI.authStep='welcome';render();toast(msg);}
function authErr(e){const m=(e&&e.message)||'';return /Invalid login/i.test(m)?'Špatný e-mail nebo heslo':/already registered|already been registered/i.test(m)?'Tento e-mail už má účet. Přihlas se.':/not confirmed/i.test(m)?'Nejdřív potvrď e-mail z odkazu, který ti přišel':/rate|security purposes/i.test(m)?'Moc pokusů za sebou, zkus to prosím za chvíli':/Password should/i.test(m)?'Heslo musí mít alespoň 6 znaků':/valid email|invalid/i.test(m)?'Zkontroluj e-mailovou adresu':'Něco se nepovedlo: '+m;}
function saveLocal(){try{const L={};LOCAL_KEYS.forEach(k=>L[k]=S[k]);if(S.cme)L.outbox=S.sessions.filter(x=>x.clientId===S.cme&&!SOK.has(x.id));localStorage.setItem(KEY,JSON.stringify(L));}catch(e){}}
''')
rep("function save(){try{const copy=Object.assign({},S);localStorage.setItem(KEY,JSON.stringify(copy));}catch(e){}}","function save(){saveLocal();scheduleFlush();}")
# remove seed data generators
cut('/* ---------- seed data ---------- */','/* ---------- state ---------- */','')

# ---------- media: photos as small images in the row, videos in Storage ----------
rep("const BLOBS={};","const BLOBS={},SIGNED={};\nfunction msrc(s){if(!s)return '';if(BLOBS[s])return BLOBS[s];if(s.startsWith('data:')||s.startsWith('https:'))return s;\n if(s.startsWith('sb:')){const p=s.slice(3);if(SIGNED[p])return SIGNED[p];if(SIGNED[p]===undefined){SIGNED[p]=null;sb.storage.from('media').createSignedUrl(p,60*60*24*7).then(r=>{if(r.data&&r.data.signedUrl){SIGNED[p]=r.data.signedUrl;liveRender();}});}}return '';}\nasync function upload(file){const ext=(file.name.split('.').pop()||'bin').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,5)||'bin';const path=S.uid+'/'+Date.now().toString(36)+uid()+'.'+ext;\n if(file.size>50*1024*1024)throw new Error('Soubor je větší než 50 MB');const r=await sb.storage.from('media').upload(path,file,{contentType:file.type||undefined,upsert:false});if(r.error)throw r.error;BLOBS['sb:'+path]=URL.createObjectURL(file);return 'sb:'+path;}")
rep("const src=c.photo&&(BLOBS[c.photo]||c.photo);","const src=c.photo&&msrc(c.photo);")
rep("function mediaThumb(m,editable,exId){const src=m.src&&BLOBS[m.src];","function mediaThumb(m,editable,exId){const src=msrc(m.src);")
rep("if(m.kind==='photo'||m.kind==='video'){const src=m.src&&(m.src.startsWith('data:')?m.src:BLOBS[m.src]);","if(m.kind==='photo'||m.kind==='video'){const src=msrc(m.src);",count=0)
# chat attachments
i=s.index("if(f.startsWith('chat:')){const cid=f.slice(5);UI.sheet=null;")
j=s.index("return;}",s.index("trainerReply(cid,'Díky, mrknu na to a dám ti vědět",i))+len("return;}")
s=s[:i]+"""if(f.startsWith('chat:')){const cid=f.slice(5);UI.sheet=null;rerender();
  files.forEach(file=>{const isV=file.type.startsWith('video');
   if(isV){toast('Nahrávám video…');upload(file).then(src=>{S.messages[cid].push(msgOut({kind:'video',src:src,text:''}));save();render('bottom');}).catch(e=>toast('Video se nepodařilo nahrát. '+(e.message||'')));}
   else{const r=new FileReader();r.onload=()=>downscale(r.result,1000).then(url=>{S.messages[cid].push(msgOut({kind:'photo',src:url,text:''}));save();render('bottom');});r.readAsDataURL(file);}});
  return;}"""+s[j:]
# template media
rep("files.forEach(file=>{const key='b'+uid();BLOBS[key]=URL.createObjectURL(file);ex.media.push({id:uid(),kind:file.type.startsWith('video')?'video':'photo',name:file.name,src:key});});\n rerender();toast(files.length===1?'Médium přidáno':files.length+' médií přidáno');",
 "files.forEach(file=>{const isV=file.type.startsWith('video');const m={id:uid(),kind:isV?'video':'photo',name:file.name,src:''};ex.media.push(m);\n  if(isV){upload(file).then(src=>{m.src=src;rerender();}).catch(e=>{ex.media=ex.media.filter(x=>x!==m);rerender();toast('Video se nepodařilo nahrát. '+(e.message||''));});}\n  else{const r=new FileReader();r.onload=()=>downscale(r.result,1200).then(url=>{m.src=url;rerender();});r.readAsDataURL(file);}});\n rerender();toast(files.some(f=>f.type.startsWith('video'))?'Nahrávám…':files.length===1?'Médium přidáno':files.length+' médií přidáno');")

# ---------- auth screens ----------
rep('<div class="row" style="justify-content:center"><button class="small muted" style="padding:8px" data-a="democlient">Demo jako klient</button></div>','')
rep('<div class="row" style="justify-content:center;gap:4px;flex-wrap:wrap"><button class="small muted" style="padding:8px" data-a="demo">Demo jako trenér</button><span class="faint">·</span><button class="small muted" style="padding:8px" data-a="demoowner">Demo jako majitel</button></div>','')
rep("'<div class=\"tiny faint\" style=\"margin:-6px 4px 0\">V demu zkus kód K7P 4QX (trenér Tomáš Beneš).</div>'","''")
rep('placeholder="Např. K7P 4QX"','placeholder="Např. ABC 123"')
rep('<input class="input" id="cl-email" type="email" value="jakub@email.cz" autocomplete="email">','<input class="input" id="cl-email" type="email" required placeholder="ty@email.cz" autocomplete="email">')
rep('<input class="input" id="cl-pass" type="password" value="demodemo" autocomplete="current-password">','<input class="input" id="cl-pass" type="password" required autocomplete="current-password">')
rep('<input class="input" id="l-email" type="email" value="\'+esc(S.trainer.email)+\'" autocomplete="email">','<input class="input" id="l-email" type="email" required placeholder="ty@email.cz" autocomplete="email">')
rep('<input class="input" id="l-pass" type="password" value="demodemo" autocomplete="current-password">','<input class="input" id="l-pass" type="password" required autocomplete="current-password">')
FORGOT='<button type="button" class="small muted" style="padding:8px;align-self:center" data-a="auth" data-v="forgot">Zapomenuté heslo?</button>'
rep('<button class="btn ink block" type="submit" style="margin-top:8px">Přihlásit se</button></form></div></div>\';\n if(st===\'cdone\')','<button class="btn ink block" type="submit" style="margin-top:8px">Přihlásit se</button>'+FORGOT+'</form></div></div>\';\n if(st===\'cdone\')')
rep('<button class="btn ink block" type="submit" style="margin-top:8px">Přihlásit se</button></form></div></div>\';\n if(st===\'register\')','<button class="btn ink block" type="submit" style="margin-top:8px">Přihlásit se</button>'+FORGOT+'</form></div></div>\';\n if(st===\'register\')')
rep("function scrAuth(){\n const st=UI.authStep;",r"""function scrAuth(){
 const st=UI.authStep;
 if(UI.booting)return '<div class="view" style="display:flex;align-items:center;justify-content:center"><div class="stack" style="align-items:center;gap:18px"><div class="glass" style="width:110px;height:110px;border-radius:30px;display:grid;place-items:center"><span class="mark" style="width:64px"></span></div><span class="small muted">Načítám…</span></div></div>';
 if(st==='verify')return '<div class="view" style="display:flex;flex-direction:column;justify-content:space-between;padding-bottom:40px"><div class="stack" style="padding-top:80px;align-items:center;text-align:center;gap:16px"><span class="eyebrow">Skoro hotovo</span><h1 class="title-xl">Potvrď svůj e-mail</h1><p class="muted" style="margin:0;line-height:1.5;max-width:310px">Poslali jsme ti odkaz na <b>'+esc(UI.verifyEmail||'')+'</b>. Klepni na něj a pak se tady přihlas.</p></div><button class="btn ink block" data-a="auth" data-v="'+(UI.app==='client'?'clogin':'login')+'">Přihlásit se</button></div>';
 if(st==='forgot')return '<div class="view detail">'+nav('Zapomenuté heslo')+'<div class="stack"><h1 class="title-xl">Nové heslo</h1><p class="muted" style="margin:0">Pošleme ti e-mail s odkazem, přes který si nastavíš nové heslo.</p><form class="stack" data-form="forgot" style="margin-top:6px"><div class="field"><label for="fg-email">E-mail</label><input class="input" id="fg-email" type="email" required placeholder="ty@email.cz" autocomplete="email"></div><button class="btn ink block" type="submit" style="margin-top:8px">Poslat odkaz</button></form></div></div>';
 if(st==='newpass')return '<div class="view detail"><div class="stack" style="padding-top:20px"><h1 class="title-xl">Nastav nové heslo</h1><form class="stack" data-form="newpass" style="margin-top:6px"><div class="field"><label for="np-pass">Nové heslo</label><input class="input" id="np-pass" type="password" required minlength="6" placeholder="Alespoň 6 znaků" autocomplete="new-password"></div><button class="btn ink block" type="submit" style="margin-top:8px">Uložit heslo</button></form></div></div>';""")

# ---------- auth handlers ----------
i=s.index(" if(k==='login'){");j=s.index(" if(k==='chat'){",i)
s=s[:i]+r""" const busy=b=>{const bt=form.querySelector('button[type=submit]');if(bt){bt.disabled=b;bt.style.opacity=b?.6:'';}};
 const val=id=>{const el=document.getElementById(id);return el?el.value.trim():'';};
 if(k==='login'||k==='clogin'){const p=k==='login'?'l':'cl';busy(true);
  sb.auth.signInWithPassword({email:val(p+'-email').toLowerCase(),password:document.getElementById(p+'-pass').value}).then(({data,error})=>{busy(false);if(error)return toast(authErr(error));boot(data.session);});return;}
 if(k==='register'){const n=val('r-name'),em=val('r-email').toLowerCase(),sp=val('r-spec'),pw=document.getElementById('r-pass').value;busy(true);
  sb.auth.signUp({email:em,password:pw,options:{data:{role:'trainer',name:n,spec:sp},emailRedirectTo:location.origin}}).then(({data,error})=>{busy(false);if(error)return toast(authErr(error));
   if(data.session)boot(data.session);else{UI.app='trainer';UI.verifyEmail=em;UI.authStep='verify';render('push');}});return;}
 if(k==='creg'){const r={code:val('cr-code'),name:val('cr-name'),goal:val('cr-goal'),email:val('cr-email').toLowerCase()};UI.creg=r;const pw=document.getElementById('cr-pass')?document.getElementById('cr-pass').value:'';busy(true);
  sb.rpc('trainer_by_code',{p_code:r.code}).then(({data,error})=>{
   if(error||!data){busy(false);UI.cregErr=error?'Kód teď nejde ověřit, zkus to prosím znovu.':'Tenhle kód nepatří žádnému trenérovi. Zkontroluj ho u svého trenéra.';render();const el=document.getElementById('cr-code');if(el)el.focus();return;}
   UI.cregErr='';
   sb.auth.signUp({email:r.email,password:pw,options:{data:{role:'client',code:r.code,name:r.name,goal:r.goal},emailRedirectTo:location.origin}}).then(({data:d2,error:e2})=>{busy(false);if(e2)return toast(authErr(e2));
    if(d2.session)boot(d2.session);else{UI.app='client';UI.verifyEmail=r.email;UI.authStep='verify';render('push');}});});return;}
 if(k==='forgot'){const em=val('fg-email').toLowerCase();busy(true);sb.auth.resetPasswordForEmail(em,{redirectTo:location.origin}).then(({error})=>{busy(false);if(error)return toast(authErr(error));UI.authStep='welcome';render('pop');toast('Odkaz jsme poslali na '+em);});return;}
 if(k==='newpass'){const pw=document.getElementById('np-pass').value;busy(true);sb.auth.updateUser({password:pw}).then(({data,error})=>{busy(false);if(error)return toast(authErr(error));toast('Heslo změněno');UI.recovery=false;bootUid=null;sb.auth.getSession().then(r=>boot(r.data.session));});return;}
"""+s[j:]
# client registration form needs a password field id cr-pass (check it exists)
assert 'id="cr-pass"' in s, 'cr-pass missing'

# ---------- actions ----------
rep(" demo(){S.role='trainer';S.me='tr1';S.authed=true;save();render('push');},\n","")
rep(" demoowner(){S.role='owner';S.me='own';S.authed=true;UI.tab='home';save();render('push');toast('Přihlášen jako majitel');},\n","")
rep(" enter(){S.authed=true;save();render('push');},"," enter(){S.authed=true;UI.authStep='welcome';UI.stack=[];UI.tab='home';render('push');},")
rep(" democlient(){","  _democlient(){")
rep(" regen(){UI.sheet={type:'confirm',title:'Vygenerovat nový kód?',text:'Starý kód přestane fungovat pro nové registrace. Stávající klienti zůstanou připojení.',ok:'Vygenerovat',run:()=>{S.trainer.code=genCode();save();toast('Nový kód: '+fmtCode(S.trainer.code));}};rerender();},",
 " regen(){UI.sheet={type:'confirm',title:'Vygenerovat nový kód?',text:'Starý kód přestane fungovat pro nové registrace. Stávající klienti zůstanou připojení.',ok:'Vygenerovat',run:()=>{sb.rpc('regen_code').then(({data,error})=>{if(error)return toast('Kód se nepodařilo změnit');S.trainer.code=data;const r=ROWS.trainers.get(S.uid);if(r)r.code=data;rerender();toast('Nový kód: '+fmtCode(data));});}};rerender();},")
# change trainer by code through the database
i=s.index(" ccodesave(){");j=s.index("\n csim(k){",i)
s=s[:i]+""" ccodesave(){const code=String(UI.ccode||'').replace(/\\s/g,'').toUpperCase();if(!code){UI.ccodeErr='Zadej kód trenéra.';rerender();return;}
  sb.rpc('trainer_by_code',{p_code:code}).then(({data})=>{
   if(!data){UI.ccodeErr='Tenhle kód nepatří žádnému trenérovi. Zkontroluj ho.';rerender();return;}
   if(data.id===me().trainerId){UI.ccodeErr='U tohoto trenéra už jsi.';rerender();return;}
   sb.rpc('change_trainer',{p_code:code}).then(async ({error})=>{if(error){UI.ccodeErr='Nepodařilo se připojit, zkus to znovu.';rerender();return;}
    S.me=data.id;await loadAll();snapshot();S.messages[S.cme]=S.messages[S.cme]||[];S.messages[S.cme].push(msgOut({text:'Ahoj, právě jsem se k tobě připojil(a) přes tvůj kód!'}));
    UI.ccode='';UI.ccodeErr='';UI.sheet=null;save();rerender();toast('Připojeno k trenérovi '+data.name);});});},"""+s[j:]
rep(" logout(){UI.app=isC()?'client':'trainer';S.authed=false;S.role='trainer';S.me='tr1';UI.authStep='welcome';UI.stack=[];UI.tab='home';save();render('pop');}",
 " logout(){flushNow().then(()=>S.cnotif&&S.cnotif.remind?(S.cnotif.remind=false,pushSync().catch(()=>{})):0).then(()=>{bootUid=null;UI.app=isC()?'client':'trainer';if(chan){sb.removeChannel(chan);chan=null;}sb.auth.signOut();const keep={};LOCAL_KEYS.forEach(k=>keep[k]=S[k]);S=Object.assign(blank(),keep);bindS();ensureSettings();TABLES.forEach(t=>{ROWS[t]=new Map();SNAP[t]=new Map();});UI.authStep='welcome';UI.stack=[];UI.tab='home';UI.sheet=null;render('pop');});},\n shareinvite(){const el=document.getElementById('invite-text');const text=el?el.textContent:'';const url=inviteURL();if(navigator.share){navigator.share({title:'CoachMe',text:text,url:url}).catch(()=>{});}else copy(text+' '+url,'Pozvánka zkopírována');}")
# invite sheet: real share instead of simulate
rep('<button class="btn ink" data-a="simjoin">\'+ic(\'bolt\',18)+\' Simulovat</button></div><span class="tiny faint">„Simulovat“ předvede, jak se nový klient objeví po zadání kódu.</span>','<button class="btn ink" data-a="shareinvite">\'+ic(\'share\',18)+\' Poslat</button></div>')
rep("Stáhni si ji a při registraci zadej můj kód '+fmtCode(S.trainer.code)+'.","Otevři '+esc(location.host)+', klepni na Klient a při registraci zadej můj kód '+fmtCode(S.trainer.code)+'.")
rep("Klient si stáhne aplikaci CoachMe, při registraci zadá tento kód a automaticky se připojí k tobě.","Klient otevře CoachMe, zvolí Klient, při registraci zadá tento kód a automaticky se připojí k tobě.")
# profile: drop demo-only blocks
i=s.index(' h+=\'<div class="glass card stack" style="gap:10px"><span class="small muted">Vyzkoušej si, jak oznámení vypadá');j=s.index("\n h+='</div></div>';return h;",i)
s=s[:i]+"\n h+='<p class=\"tiny faint\" style=\"margin:4px 6px 0\">Oznámení se zatím zobrazují, když máš aplikaci otevřenou.</p>';"+s[j:]
# workout: no lock-screen preview button
rep('<button class="btn ghost block" data-a="lockprev">\'+ic(\'lock\',18)+\' Náhled zamknuté obrazovky</button>','')
# no fake replies
i=s.index("function clientReply(cid,text){");j=s.index("/* workout clock:",i)
s=s[:i]+"function clientReply(){}\nfunction trainerReply(){}\nfunction trainerComment(){}\n"+s[j:]

rep("function pushEnable(){if(!('Notification' in window))return Promise.reject(new Error('unsupported'));return Notification.requestPermission().then(p=>{if(p!=='granted')throw new Error('denied');});}\nfunction pushSync(){return Promise.resolve();}",r"""const VAPID='BD93Ihv2xaGDShtLF6wyuC5wMb9AtJRfC1xxuiYnX6bHLkG1HErQ6xsxwVLIW72ZdVJTAqbvUrXGxUx2BiLLBrs';
function pushOK(){return 'serviceWorker' in navigator&&'PushManager' in window&&'Notification' in window;}
function b64u(s){const p='='.repeat((4-s.length%4)%4),b=atob((s+p).replace(/-/g,'+').replace(/_/g,'/'));return Uint8Array.from(b,c=>c.charCodeAt(0));}
async function pushHash(t){const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t));return Array.from(new Uint8Array(d)).map(x=>x.toString(16).padStart(2,'0')).join('').slice(0,40);}
function pushEnable(){if(!pushOK())return Promise.reject(new Error('unsupported'));return Notification.requestPermission().then(p=>{if(p!=='granted')throw new Error('denied');return navigator.serviceWorker.register('/sw.js');});}
async function pushCur(){const r=await navigator.serviceWorker.getRegistration('/');return r?r.pushManager.getSubscription():null;}
async function pushSync(){if(!S.cme||!S.uid||!pushOK())return;const n=S.cnotif||{};
 if(!n.remind){const c=await pushCur();if(c)await sb.from('push_subs').update({on:false,updated_at:new Date().toISOString()}).eq('id',await pushHash(S.uid+'|'+c.endpoint));return;}
 const reg=await navigator.serviceWorker.register('/sw.js');await navigator.serviceWorker.ready;
 let c=await reg.pushManager.getSubscription();if(!c)c=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:b64u(VAPID)});
 let tz='Europe/Prague';try{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||tz;}catch(_){}
 const {error}=await sb.from('push_subs').upsert({id:await pushHash(S.uid+'|'+c.endpoint),client_id:S.uid,sub:c.toJSON(),hour:n.remindH==null?8:n.remindH,tz:tz,on:true,updated_at:new Date().toISOString()});if(error)throw error;}""")
rep("if(S.cme)restoreOutbox();","if(S.cme)restoreOutbox();if(S.cme&&S.cnotif&&S.cnotif.remind)pushSync().catch(()=>{});")
rep("function refreshData(){return new Promise(r=>setTimeout(r,700));}","function refreshData(){if(!navigator.onLine)return Promise.reject(new Error('offline'));return flushNow().then(()=>loadAll()).then(()=>{snapshot();});}")
# ---------- start ----------
rep("\napplyInvite();applyGo();render();\n})();\n</script>",r"""
applyInvite();
UI.booting=true;render();
if(UI.invCode)sb.rpc('trainer_by_code',{p_code:UI.invCode}).then(({data})=>{if(data&&!S.authed){UI.invBy=data;render();}});
sb.auth.onAuthStateChange((ev,session)=>{
 if(ev==='PASSWORD_RECOVERY'){UI.recovery=true;UI.booting=false;S.authed=false;UI.authStep='newpass';render();return;}
 if(UI.recovery)return;
 if(ev==='INITIAL_SESSION'||ev==='SIGNED_IN')setTimeout(()=>boot(session),0);
});
window.addEventListener('pagehide',()=>{flushNow();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)flushNow();});
})();
</script>""")
open('prod.html','w').write(s)
print('ok',len(s))
# second pass
s=open('prod.html').read()
i=s.index("function demoSwitch(){");j=s.index("Demo verze</span></div>';}",i)+len("Demo verze</span></div>';}")
s=s[:i]+"function demoSwitch(){return '<div class=\"row\" style=\"justify-content:center;gap:8px;margin-top:10px\"><span class=\"mark\" style=\"width:26px;background:var(--ink3)\"></span><span class=\"tiny faint\">CoachMe</span></div>';}"+s[j:]
i=s.index(" reset(){");j=s.index("\n logout(){",i)
s=s[:i]+" reset(){},"+s[j:]
open('prod.html','w').write(s)
print('pass2 ok')
s=open('prod.html').read()
s=s.replace("'+esc(t.spec)+'. Jakmile","'+(t.spec?esc(t.spec)+'. ':'')+'Jakmile",1)
open('prod.html','w').write(s)
# ---------- removing clients / trainers through the database ----------
s=open('prod.html').read()
def rep2(old,new):
    global s
    assert s.count(old)==1, ('anchor',s.count(old),old[:70])
    s=s.replace(old,new)
i=s.index("function removeClient(id){");j=s.index("toast('Trenér '+t.name+' byl odebrán');}",i)+len("toast('Trenér '+t.name+' byl odebrán');}")
s=s[:i]+r"""async function afterRemove(ids,msg){await loadAll();snapshot();leaveScreens(ids);render('pop');toast(msg);}
function removeClient(id){const c=client(id);if(!c)return;flushNow().then(()=>sb.rpc('remove_client',{p_client:id})).then(({error})=>{if(error)return toast('Svěřence se nepodařilo odebrat, zkus to znovu');afterRemove([id],c.name+' už není tvůj svěřenec');});}
function removeTrainer(id){const t=S.trainers.find(x=>x.id===id);if(!t)return;const cs=S.clientsAll.filter(c=>c.trainerId===id).map(c=>c.id);flushNow().then(()=>sb.rpc('remove_trainer',{p_trainer:id})).then(({error})=>{if(error)return toast('Trenéra se nepodařilo odebrat, zkus to znovu');afterRemove([id].concat(cs),'Trenér '+t.name+' byl odebrán');});}"""+s[j:]
# a trainer whose account the owner removed is signed out
rep2("function applyChange(p){const t=p.table;if(!TB[t])return;",
     "function applyChange(p){const t=p.table;if(!TB[t])return;\n if(t==='trainers'&&p.eventType==='DELETE'&&p.old&&p.old.id===S.uid&&!isC()){S.authed=false;A.logout();setTimeout(()=>toast('Tvůj trenérský účet byl odebrán.'),400);return;}")
rep2("if(r.error)return bootFail('Účet se nepodařilo dokončit. '+r.error.message);",
     "if(r.error)return bootFail(/account removed/.test(r.error.message)?'Tento účet byl odebrán.':'Účet se nepodařilo dokončit. '+r.error.message);")
rep2("return bootFail(/bad code/.test(r.error.message)?","return bootFail(/account removed/.test(r.error.message)?'Tento účet byl odebrán.':/bad code/.test(r.error.message)?")
# sync hardening: clients write only their own templates/exercises (see ownRows); deleted rows leave local state at once; a reload is snapshotted before anything can flush
rep2("if(p.eventType==='DELETE'){const id=p.old&&p.old.id;if(!id||!ROWS[t].has(id))return;ROWS[t].delete(id);SNAP[t].delete(id);}",
     "if(p.eventType==='DELETE'){const id=p.old&&p.old.id;if(!id||!ROWS[t].has(id))return;ROWS[t].delete(id);SNAP[t].delete(id);TB[t].set([...ROWS[t].values()]);ensureBuckets();}")
rep2("TABLES.forEach((t,i)=>{ROWS[t]=new Map(res[i].map(r=>[r.id,r]));});ROWS.sessions.forEach((v,k)=>SOK.add(k));materialize();}","TABLES.forEach((t,i)=>{ROWS[t]=new Map(res[i].map(r=>[r.id,r]));});ROWS.sessions.forEach((v,k)=>SOK.add(k));materialize();snapshot();}")
# a late boot for a session that was already signed out (e.g. removed account) does nothing
rep2(" if(bootUid===session.user.id)return;bootUid=session.user.id;"," if(bootUid===session.user.id)return;bootUid=session.user.id;\n if(!(await sb.auth.getSession()).data.session){bootUid=null;return;}")
open('prod.html','w').write(s)
print('remove pass ok')
