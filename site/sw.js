// CoachMe – service worker jen pro upozornění (nic necachuje)
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('push',e=>{
  let d={};try{d=e.data?e.data.json():{};}catch(_){d={body:e.data&&e.data.text()};}
  e.waitUntil(self.registration.showNotification(d.title||'CoachMe',{body:d.body||'',icon:'/icon.png',badge:'/icon.png',tag:d.tag||'coachme-remind',data:{url:d.url||'/?go=workout'}}));
});
self.addEventListener('notificationclick',e=>{
  e.notification.close();
  const url=new URL((e.notification.data&&e.notification.data.url)||'/',self.location.origin).href;
  e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(ws=>{
    for(const w of ws){if('navigate' in w)return w.navigate(url).then(x=>(x||w).focus());}
    return self.clients.openWindow(url);
  }));
});
