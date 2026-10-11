const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const W=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:430,height:900},colorScheme:'dark'});const errs=[];
 const mk=async n=>{const p=await ctx.newPage();p.on('pageerror',e=>errs.push(n+' '+e.stack));p.on('console',m=>{if(m.type()==='error')errs.push(n+' console '+m.text());});return p;};
 const url='file://'+process.cwd()+'/test/index.html';
 const regT=async(P,name,em)=>{await P.click('[data-a=auth][data-v=register]');await P.fill('#r-name',name);await P.fill('#r-email',em);await P.fill('#r-pass','heslo123');await P.click('form[data-form=register] button[type=submit]');await W(700);await P.click('[data-a=enter]');await W(300);};
 const A=await mk('A');await A.goto(url);await A.evaluate(()=>{localStorage.clear();sessionStorage.clear();});await A.reload();await W(400);
 await regT(A,'Tomáš Beneš','tomas@test.cz');
 const code=await A.evaluate(()=>JSON.parse(localStorage.mockdb).t.trainers[0].code);
 await A.click('[data-a=tab][data-v=templates]');await A.click('[data-a=newtpl]');await W(300);await A.fill('#d-name','Full body A');await A.click('[data-a=savetpl]');await W(500);
 const B=await mk('B');await B.goto(url);await W(400);
 await B.click('[data-a=appsw][data-v=client]');await B.click('[data-a=auth][data-v=creg]');await B.fill('#cr-code',code);await B.fill('#cr-name','Jana Malá');await B.fill('#cr-email','jana@test.cz');await B.fill('#cr-pass','heslo123');await B.click('form[data-form=creg] button[type=submit]');await W(800);await B.click('[data-a=enter]');await W(400);
 await A.click('[data-a=sheet][data-v^=share]');await W(300);await A.click('.sheet [data-a=toggle] >> nth=0');await A.click('[data-a=doshare]');await W(600);
 await B.click('[data-a=tab][data-v=chat]');await W(300);const cc=await B.locator('#chat-in').count();if(!cc){await B.click('#view button >> nth=0').catch(()=>{});await W(300);}
 await B.fill('#chat-in','Ahoj');await B.press('#chat-in','Enter');await W(600);await B.click('[data-a=back]').catch(()=>{});await W(300);
 // trainer removes client
 await A.click('[data-a=tab][data-v=clients]');await W(300);await A.click('#view [data-v^="client:"] >> nth=0');await W(400);await A.click('[data-a=rmclient]');await W(300);await A.click('button[data-a=confirm]');await W(900);
 await A.screenshot({path:'y8a.png'});await B.screenshot({path:'y8b.png'});
 const db=()=>A.evaluate(()=>{const d=JSON.parse(localStorage.mockdb).t;return Object.fromEntries(Object.entries(d).map(([k,v])=>[k,v.length]));});
 console.log('after rmclient',await db(),'B no-trainer screen:',await B.locator('#nt-code').count(),'A clients:',await A.evaluate(()=>document.querySelectorAll('#view [data-v^="client:"]').length));
 // client rejoins by code
 await B.fill('#nt-code',code);await B.click('[data-a=ccodesave]');await W(900);console.log('B rejoined, tabs:',await B.locator('.tabbar').count());
 // owner removes trainer A
 const C=await mk('C');await C.goto(url);await W(400);await regT(C,'Michael','m@test.cz');
 await C.evaluate(()=>{const d=JSON.parse(localStorage.mockdb);d.t.trainers.find(t=>t.data.email==='m@test.cz').is_owner=true;localStorage.mockdb=JSON.stringify(d);});
 await C.reload();await W(900);await C.click('[data-a=tab][data-v=trainers]');await W(400);
 const aid=await A.evaluate(()=>JSON.parse(sessionStorage.mocksess).user.id);
 await C.click('#view [data-a=opentrainer][data-v="'+aid+'"]');await W(400);await C.click('[data-a=rmtrainer]');await W(300);await C.screenshot({path:'y8c.png'});await C.click('button[data-a=confirm]');await W(1200);
 console.log('trainers',await A.evaluate(()=>JSON.parse(localStorage.mockdb).t.trainers.map(t=>t.data.name+':'+t.is_owner)),'removed',await A.evaluate(()=>JSON.parse(localStorage.mockdb).removed),'C toast',await C.evaluate(()=>{const t=document.querySelector('.toast');return t&&t.textContent;}));console.log('after rmtrainer',await db(),'A authed screen?',await A.locator('.tabbar').count(),'B no-trainer:',await B.locator('#nt-code').count());
 await A.screenshot({path:'y8d.png'});
 // A tries to sign in again
 await A.click('[data-a=auth][data-v=login]').catch(e=>console.log('login btn',e.message));await A.fill('#l-email','tomas@test.cz');await A.fill('#l-pass','heslo123');await A.click('form[data-form=login] button[type=submit]');await W(1200);
 console.log('A toast:',await A.evaluate(()=>{const t=document.querySelector('.toast');return t&&t.textContent;}));
 console.log(errs);await b.close();})();
