const BASE='http://127.0.0.1:8090'; const q=encodeURIComponent;
async function j(p,tok){const h={};if(tok)h.Authorization=tok;return (await fetch(BASE+p,{headers:h})).json();}
async function run(f){const p='/api/collections/probe_items/records?perPage=100&sort=id&filter='+q(f);
 const a=await fetch(BASE+p).then(r=>r.json());const b=await fetch(BASE+p).then(r=>r.json());
 return {t:(a.items||[]).map(x=>x.title===''?'#'+x.note:x.title).sort(),stable:JSON.stringify(a)===JSON.stringify(b),st:a.status||200,raw:a};}
(async()=>{
console.log('probe pass 5 — '+new Date().toISOString()+' — pocketbase.exe 0.39.10');
const tok=(await (await fetch(BASE+'/api/collections/_superusers/auth-with-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({identity:'probe@example.com',password:'Probe12345678'})})).json()).token;
const col=await j('/api/collections/probe_items',tok);
console.log('=== 0. Confirming the fixture really is multi-valued (guards against a probe-side schema mistake) ===');
for(const f of col.fields) if(['select','relation'].includes(f.type))
  console.log('  field '+f.name+'  type='+f.type+'  maxSelect='+f.maxSelect);
const rec=(await j('/api/collections/probe_items/records?perPage=100&filter='+q('note="plain"'))).items[0];
console.log('  record "Lorem ipsum" stored value: opts='+JSON.stringify(rec.opts)+'  tags='+JSON.stringify(rec.tags));
const tags=(await j('/api/collections/probe_tags/records?perPage=10')).items;
const alpha=tags.find(t=>t.label==='alpha').id;
console.log('  alpha tag id = '+alpha);

console.log('\n=== 1. "?= Any/At least one of Equal" on a multi-RELATION field, by id (direct analogue) ===');
for(const f of ['tags ?= "'+alpha+'"','tags = "'+alpha+'"','tags.id ?= "'+alpha+'"']){
  const r=await run(f);console.log('  '+f.padEnd(34)+' -> '+JSON.stringify(r.t));}
console.log('  expected per doc (any-of alpha): ["#emptytit","Lorem ipsum","lorem lower"]');

console.log('\n=== 2. "?= Any/At least one of Equal" on a multi-SELECT field ===');
for(const f of ['opts ?= "a"','opts ?= "b"','opts ?= "c"','opts ?= "pb_x"']){
  const r=await run(f);console.log('  '+f.padEnd(34)+' -> '+JSON.stringify(r.t));}
console.log('  expected per doc for opts ?= "a": ["Lorem ipsum","back\\slash","lorem lower"]');

console.log('\n=== 3. what DOES retrieve a select option, for comparison ===');
for(const f of ['opts:each = "a"','opts ~ "a"','opts ?~ "a"','opts:each ?= "a"']){
  const r=await run(f);console.log('  '+f.padEnd(34)+' status='+r.st+' -> '+JSON.stringify(r.t));}

console.log('\n=== 4. reproduction x5 of opts ?= "a" and tags ?= alpha ===');
for(let i=1;i<=5;i++){const a=await run('opts ?= "a"');const b=await run('tags ?= "'+alpha+'"');
 console.log('  run '+i+': opts ?= "a" -> '+a.t.length+' items   |   tags ?= alpha -> '+b.t.length+' items');}

console.log('\n=== 5. does a SINGLE-valued select behave differently? (maxSelect=1) ===');
await fetch(BASE+'/api/collections/probe_single',{method:'DELETE',headers:{Authorization:tok}});
let r=await fetch(BASE+'/api/collections',{method:'POST',headers:{'Content-Type':'application/json',Authorization:tok},body:JSON.stringify({name:'probe_single',type:'base',fields:[{name:'label',type:'text'},{name:'one',type:'select',maxSelect:1,values:['a','b']}],listRule:'',viewRule:'',createRule:'',updateRule:'',deleteRule:''})});
console.log('  create probe_single: '+r.status);
for(const [label,one] of [['r1',['a']],['r2',['b']],['r3',[]]])
  await fetch(BASE+'/api/collections/probe_single/records',{method:'POST',headers:{'Content-Type':'application/json',Authorization:tok},body:JSON.stringify({label,one})});
for(const f of ['one = "a"','one ?= "a"']){
  const p='/api/collections/probe_single/records?perPage=10&filter='+q(f);
  const res=await fetch(BASE+p).then(x=>x.json());
  console.log('  '+f.padEnd(16)+' -> '+JSON.stringify((res.items||[]).map(x=>x.label))+'  (single-valued select stores '+JSON.stringify((await j('/api/collections/probe_single/records?perPage=10')).items[0].one)+')');}
})();
