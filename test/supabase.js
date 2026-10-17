/* Test double for supabase-js: shared in-memory DB in localStorage, one session per tab, rough RLS, realtime via storage events. */
(function(){
const LS=localStorage,SS=sessionStorage;
const db=()=>JSON.parse(LS.getItem('mockdb')||'{"users":[],"t":{}}');
const put=d=>LS.setItem('mockdb',JSON.stringify(d));
const T=['trainers','clients','templates','exercises','sessions','metrics','assignments','messages','notes','reports','slots','client_groups'];
const sess=()=>JSON.parse(SS.getItem('mocksess')||'null');
const uidOf=()=>{const s=sess();return s&&s.user.id;};
function code(){const a='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';let c='';for(let i=0;i<6;i++)c+=a[Math.floor(Math.random()*a.length)];return c;}
function tbl(d,t){d.t[t]=d.t[t]||[];return d.t[t];}
function myTrainer(d,u){const c=tbl(d,'clients').find(x=>x.id===u);return c&&c.trainer_id;}
function isOwner(d,u){const t=tbl(d,'trainers').find(x=>x.id===u);return !!(t&&t.is_owner);}
function isMyClient(d,u,cid){const c=tbl(d,'clients').find(x=>x.id===cid);return !!(c&&c.trainer_id===u);}
function visible(d,t,r,u){if(!u)return false;
 switch(t){case 'trainers':return r.id===u||r.id===myTrainer(d,u)||isOwner(d,u);
  case 'clients':return r.id===u||r.trainer_id===u||isOwner(d,u);
  case 'templates':case 'exercises':return r.trainer_id===u||(!r.client_id&&r.trainer_id===myTrainer(d,u))||r.client_id===u;
  case 'notes':return r.trainer_id===u&&isMyClient(d,u,r.client_id);
  case 'reports':return isOwner(d,u);
  case 'slots':return r.trainer_id===u||r.trainer_id===myTrainer(d,u);
  case 'client_groups':return r.trainer_id===u;
  default:return r.client_id===u||isMyClient(d,u,r.client_id)||(t==='sessions'&&isOwner(d,u));}}
function writable(d,t,r,u){if(t==='reports')return true;if(t==='slots')return r.trainer_id===u;if(t==='templates'||t==='exercises')return r.trainer_id===u||(r.client_id===u&&(!r.trainer_id||r.trainer_id===myTrainer(d,u)));if(t==='trainers')return r.id===u;if(t==='clients')return r.id===u||r.trainer_id===u;return visible(d,t,r,u);}
function emit(table,eventType,nw,old){const ev={table,eventType,new:nw,old:old,n:Math.random()};LS.setItem('mockev',JSON.stringify(ev));window.dispatchEvent(new CustomEvent('mockev',{detail:ev}));}
class Q{constructor(t){this.t=t;this.f=[];this.op='select';}
 select(){if(this.op==='select')this.op='select';return this;}
 eq(c,v){this.f.push(r=>r[c]===v);return this;}
 in(c,vs){this.f.push(r=>vs.includes(r[c]));return this;}
 range(a,b){this.rg=[a,b];return this;}
 maybeSingle(){this.single=true;return this;}
 insert(rows){this.op='insert';this.rows=[].concat(rows);return this;}
 upsert(rows){this.op='upsert';this.rows=[].concat(rows);return this;}
 update(o){this.op='update';this.patch=o;return this;}
 delete(){this.op='delete';return this;}
 then(res,rej){return Promise.resolve().then(()=>this.run()).then(res,rej);}
 run(){const d=db(),u=uidOf(),t=this.t,a=tbl(d,t);
  if(this.op==='select'){let out=a.filter(r=>visible(d,t,r,u)).filter(r=>this.f.every(f=>f(r)));if(this.rg)out=out.slice(this.rg[0],this.rg[1]+1);return {data:this.single?(out[0]||null):JSON.parse(JSON.stringify(out)),error:null};}
  if(this.op==='insert'||this.op==='upsert'){for(const r0 of this.rows){const r=Object.assign({},r0,{updated_at:new Date().toISOString()});if(t==='notes'&&!r.trainer_id)r.trainer_id=u;
    if(!writable(d,t,r,u))return {data:null,error:{message:'new row violates row-level security policy for table "'+t+'"'}};
    const i=a.findIndex(x=>x.id===r.id);if(i>=0&&this.op==='insert')return {data:null,error:{message:'duplicate key'}};
    if(i>=0){a[i]=Object.assign(a[i],r);put(d);emit(t,'UPDATE',a[i]);}else{a.push(r);put(d);emit(t,'INSERT',r);}}
   return {data:null,error:null};}
  if(this.op==='update'){a.filter(r=>this.f.every(f=>f(r))&&writable(d,t,r,u)).forEach(r=>{Object.assign(r,this.patch,{updated_at:new Date().toISOString()});emit(t,'UPDATE',r);});put(d);return {data:null,error:null};}
  if(this.op==='delete'){const del=a.filter(r=>this.f.every(f=>f(r))&&writable(d,t,r,u));d.t[t]=a.filter(r=>!del.includes(r));put(d);del.forEach(r=>emit(t,'DELETE',null,{id:r.id}));return {data:null,error:null};}}}
const listeners=[];
function fire(ev,s){listeners.forEach(cb=>setTimeout(()=>cb(ev,s),0));}
const auth={
 onAuthStateChange(cb){listeners.push(cb);setTimeout(()=>cb('INITIAL_SESSION',sess()),0);return {data:{subscription:{unsubscribe(){}}}};},
 getSession(){return Promise.resolve({data:{session:sess()}});},
 signUp({email,password,options}){const d=db();if(d.users.find(x=>x.email===email))return Promise.resolve({data:{},error:{message:'User already registered'}});
  const user={id:'u'+Math.random().toString(36).slice(2,10),email,user_metadata:(options&&options.data)||{}};d.users.push(Object.assign({password},user));put(d);
  if(window.MOCK_CONFIRM){return Promise.resolve({data:{user,session:null},error:null});}
  const s={user,access_token:'x'};SS.setItem('mocksess',JSON.stringify(s));fire('SIGNED_IN',s);return Promise.resolve({data:{user,session:s},error:null});},
 signInWithPassword({email,password}){const d=db();const u=d.users.find(x=>x.email===email&&x.password===password);if(!u)return Promise.resolve({data:{},error:{message:'Invalid login credentials'}});
  const user={id:u.id,email:u.email,user_metadata:u.user_metadata};const s={user,access_token:'x'};SS.setItem('mocksess',JSON.stringify(s));fire('SIGNED_IN',s);return Promise.resolve({data:{user,session:s},error:null});},
 signOut(){SS.removeItem('mocksess');fire('SIGNED_OUT',null);return Promise.resolve({error:null});},
 resetPasswordForEmail(){return Promise.resolve({error:null});},
 updateUser(){return Promise.resolve({data:{},error:null});}
};
function rpc(name,args){const d=db(),u=uidOf(),s=sess();const norm=c=>String(c||'').replace(/\s/g,'').toUpperCase();
 const tr=c=>tbl(d,'trainers').find(x=>x.code===norm(c)&&x.approved!==false);
 let r={data:null,error:null};
 if(name==='book_slot'||name==='cancel_slot'){const a=tbl(d,'slots'),x=a.find(y=>y.id===args.p_id),bk=name==='book_slot';let ok=false;if(x&&(bk?(!x.client_id&&x.trainer_id===myTrainer(d,u)&&new Date(x.data.at)>new Date()):(x.client_id===u&&new Date(x.data.at)-new Date()>12*3600e3))){x.client_id=bk?u:null;put(d);emit('slots','UPDATE',x);ok=true;}r.data=ok;}
  else if(name==='trainer_by_code'){const t=tr(args.p_code);r.data=t?{id:t.id,name:t.data.name,spec:t.data.spec}:null;}
 else if(name==='register_trainer'&&(d.removed||[]).includes(u)){r.error={message:'account removed'};}
 else if(name==='register_trainer'){if(!tbl(d,'trainers').find(x=>x.id===u)){const row={id:u,code:code(),is_owner:false,approved:localStorage.mockApproval==='1'?false:true,data:{name:args.p_name||'Trenér',email:s.user.email,spec:args.p_spec||'',bio:'',photo:null,joined:new Date().toISOString()}};tbl(d,'trainers').push(row);put(d);emit('trainers','INSERT',row);}}
 else if(name==='approve_trainer'){if(!isOwner(d,u))r.error={message:'owner only'};else{const t=tbl(d,'trainers').find(x=>x.id===args.p_id);if(t){t.approved=true;put(d);emit('trainers','UPDATE',t);}r.data=!!t;}}
 else if(name==='register_client'){const t=tr(args.p_code);if(!t)r.error={message:'bad code'};else{const row={id:u,trainer_id:t.id,data:{name:args.p_name||'Klient',goal:args.p_goal||'Zatím nevyplněno',email:s.user.email,joined:new Date().toISOString(),target:3,photo:null,status:'active'}};tbl(d,'clients').push(row);put(d);emit('clients','INSERT',row);r.data={id:t.id,name:t.data.name};}}
 else if(name==='change_trainer'){const t=tr(args.p_code);const c=tbl(d,'clients').find(x=>x.id===u);if(!t||!c)r.error={message:'bad code'};else{c.trainer_id=t.id;['templates','exercises'].forEach(k=>tbl(d,k).filter(x=>x.client_id===u).forEach(x=>{x.trainer_id=t.id;emit(k,'UPDATE',x);}));put(d);emit('clients','UPDATE',c);r.data={id:t.id,name:t.data.name};}}
 else if(name==='remove_client'||name==='remove_trainer'){
  const detach=cid=>{['assignments','messages','notes'].forEach(t=>{const del=tbl(d,t).filter(r=>r.client_id===cid);d.t[t]=tbl(d,t).filter(r=>r.client_id!==cid);del.forEach(r=>emit(t,'DELETE',null,{id:r.id}));});['templates','exercises'].forEach(k=>tbl(d,k).filter(x=>x.client_id===cid).forEach(x=>{x.trainer_id=null;emit(k,'UPDATE',x);}));const c=tbl(d,'clients').find(x=>x.id===cid);c.trainer_id=null;emit('clients','UPDATE',c);};
  if(name==='remove_client'){const c=tbl(d,'clients').find(x=>x.id===args.p_client);if(!c||c.trainer_id!==u)r.error={message:'not your client'};else detach(c.id);}
  else{if(!isOwner(d,u)||args.p_trainer===u)r.error={message:'owner only'};else{const cs=tbl(d,'clients').filter(x=>x.trainer_id===args.p_trainer);cs.forEach(c=>detach(c.id));
   ['notes','templates','exercises'].forEach(t=>{const del=tbl(d,t).filter(x=>x.trainer_id===args.p_trainer);d.t[t]=tbl(d,t).filter(x=>x.trainer_id!==args.p_trainer);del.forEach(x=>emit(t,'DELETE',null,{id:x.id}));});
   d.t.trainers=tbl(d,'trainers').filter(x=>x.id!==args.p_trainer);d.removed=(d.removed||[]).concat(args.p_trainer);emit('trainers','DELETE',null,{id:args.p_trainer});r.data={clients:cs.length};}}
  put(d);}
 else if(name==='regen_code'){const t=tbl(d,'trainers').find(x=>x.id===u);t.code=code();put(d);emit('trainers','UPDATE',t);r.data=t.code;}
 return Promise.resolve(r);}
function channel(){const h=[];const ch={on(_a,_b,cb){h.push(cb);return ch;},subscribe(){
  const deliver=ev=>{const d=db(),u=uidOf();const r=ev.new||ev.old;if(ev.eventType!=='DELETE'&&!visible(d,ev.table,ev.new,u))return;h.forEach(cb=>cb({table:ev.table,eventType:ev.eventType,new:ev.new||{},old:ev.old||{}}));};
  window.addEventListener('storage',e=>{if(e.key==='mockev'&&e.newValue)deliver(JSON.parse(e.newValue));});
  window.addEventListener('mockev',e=>deliver(e.detail));return ch;}};return ch;}
const storage={from(){return {upload(p){return Promise.resolve({data:{path:p},error:null});},createSignedUrl(p){return Promise.resolve({data:{signedUrl:''},error:null});}};}};
window.supabase={createClient(){return {auth,from:t=>new Q(t),rpc,channel,removeChannel(){},storage};}};
})();
