const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const W=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:430,height:900},colorScheme:'light'});const errs=[];
 const mk=async n=>{const p=await ctx.newPage();p.on('pageerror',e=>errs.push(n+' '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push(n+' console '+m.text());});return p;};
 const A=await mk('A');const url='file://'+process.cwd()+'/test/index.html';
 await A.goto(url);await A.evaluate(()=>{localStorage.clear();sessionStorage.clear();});await A.reload();await W(400);
 await A.click('[data-a=auth][data-v=register]');await A.fill('#r-name','Tomáš Beneš');await A.fill('#r-email','tomas@test.cz');await A.fill('#r-pass','heslo123');await A.click('form[data-form=register] button[type=submit]');await W(700);
 await A.screenshot({path:'q1.png'});await A.click('[data-a=enter]');await W(300);
 const code=await A.evaluate(()=>JSON.parse(localStorage.mockdb).t.trainers[0].code);
 await A.click('[data-a=tab][data-v=templates]');await A.click('[data-a=newtpl]');await W(300);await A.fill('#d-name','Full body A');await A.click('[data-a=savetpl]');await W(500);await A.screenshot({path:'q2.png'});
 // client registers in a second tab
 const B=await mk('B');await B.goto(url);await W(400);
 await B.click('[data-a=appsw][data-v=client]');await B.click('[data-a=auth][data-v=creg]');await B.fill('#cr-code',code.slice(0,3)+' '+code.slice(3));await B.fill('#cr-name','Jana Malá');await B.fill('#cr-email','jana@test.cz');await B.fill('#cr-pass','heslo123');await B.click('form[data-form=creg] button[type=submit]');await W(800);
 await B.screenshot({path:'q3.png'});await B.click('[data-a=enter]');await W(400);await B.screenshot({path:'q4.png'});
 await W(400);await A.screenshot({path:'q5.png'});
 // trainer assigns template to the client from the template detail
 await A.click('[data-a=sheet][data-v^=share]');await W(300);await A.click('.sheet [data-a=toggle] >> nth=0');await A.click('[data-a=doshare]');await W(600);
 await B.screenshot({path:'q6.png'});
 await B.click('[data-a=tab][data-v=plan]');await W(300);await B.screenshot({path:'q7.png'});
 console.log('db',await A.evaluate(()=>{const d=JSON.parse(localStorage.mockdb).t;return Object.fromEntries(Object.entries(d).map(([k,v])=>[k,v.length]));}));
 console.log(errs);await b.close();})();
