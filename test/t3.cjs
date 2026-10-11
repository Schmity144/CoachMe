const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const W=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:430,height:900},colorScheme:'dark'});const errs=[];
 const mk=async n=>{const p=await ctx.newPage();p.on('pageerror',e=>errs.push(n+' '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push(n+' console '+m.text());});return p;};
 const A=await mk('A');const url='file://'+process.cwd()+'/test/index.html';
 await A.goto(url);await A.evaluate(()=>{localStorage.clear();sessionStorage.clear();});await A.reload();await W(400);
 await A.click('[data-a=auth][data-v=register]');await A.fill('#r-name','Tomáš Beneš');await A.fill('#r-email','tomas@test.cz');await A.fill('#r-pass','heslo123');await A.click('form[data-form=register] button[type=submit]');await W(700);await A.click('[data-a=enter]');await W(300);
 const code=await A.evaluate(()=>JSON.parse(localStorage.mockdb).t.trainers[0].code);
 await A.click('[data-a=tab][data-v=templates]');await A.click('[data-a=newtpl]');await W(300);await A.fill('#d-name','Full body A');await A.click('[data-a=savetpl]');await W(500);
 const B=await mk('B');await B.goto(url);await W(400);
 await B.click('[data-a=appsw][data-v=client]');await B.click('[data-a=auth][data-v=creg]');await B.fill('#cr-code',code);await B.fill('#cr-name','Jana Malá');await B.fill('#cr-email','jana@test.cz');await B.fill('#cr-pass','heslo123');await B.click('form[data-form=creg] button[type=submit]');await W(800);await B.click('[data-a=enter]');await W(400);
 await A.click('[data-a=sheet][data-v^=share]');await W(300);await A.click('.sheet [data-a=toggle] >> nth=0');await A.click('[data-a=doshare]');await W(600);
 // client workout
 await B.click('[data-a^=wostart] >> nth=0');await W(400);
 await B.click('[data-a=woset] >> nth=0');await B.click('[data-a=woset] >> nth=1');await W(200);await B.screenshot({path:'r1.png'});
 await B.click('[data-a=wofinish]');await W(300);await B.click('[data-a=finfeel] >> nth=3');await B.click('[data-a=finsave]');await W(800);await B.screenshot({path:'r2.png'});
 await A.screenshot({path:'r3.png'});
 await A.click('[data-a=tab][data-v=home]');await W(300);await A.screenshot({path:'r4.png'});
 // chat: client writes, trainer answers
 await B.click('[data-a=back]').catch(()=>{});await B.click('[data-a=tab][data-v=chat]');await W(300);await B.screenshot({path:'r5.png'});
 const cc=await B.locator('#chat-in').count();if(!cc){await B.click('#view button >> nth=0').catch(()=>{});await W(300);}
 await B.fill('#chat-in','Ahoj, dneska to bylo super!');await B.press('#chat-in','Enter');await W(800);
 await A.screenshot({path:'r6.png'});
 await A.click('[data-a=tab][data-v=chat]');await W(300);await A.click('#view [data-a=open] >> nth=0');await W(300);await A.fill('#chat-in','Paráda, jen tak dál 💪');await A.press('#chat-in','Enter');await W(800);await A.screenshot({path:'r7.png'});
 await B.screenshot({path:'r8.png'});
 // reload persistence on trainer side
 await A.reload();await W(900);await A.screenshot({path:'r9.png'});
 console.log('db',await A.evaluate(()=>{const d=JSON.parse(localStorage.mockdb).t;return Object.fromEntries(Object.entries(d).map(([k,v])=>[k,v.length]));}));
 console.log(errs);await b.close();})();
