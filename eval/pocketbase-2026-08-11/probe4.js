// Fourth pass: ordering operators on a multi-select field.
const BASE='http://127.0.0.1:8090'; const q=encodeURIComponent;
async function run(f){const p='/api/collections/probe_items/records?perPage=100&sort=id&filter='+q(f);
 const a=await fetch(BASE+p).then(r=>r.json()); const b=await fetch(BASE+p).then(r=>r.json());
 return {t:(a.items||[]).map(x=>x.title===''?'#'+x.note:x.title).sort(), stable:JSON.stringify(a)===JSON.stringify(b), st:a.status||200};}
(async()=>{
console.log('probe pass 4 — '+new Date().toISOString()+' — pocketbase.exe 0.39.10');
console.log('fixture opts: "Lorem ipsum"=[a,b]  "lorem lower"=[a]  "100% pure"=[]  "under_score"=[pb_x,pb_y]');
console.log('             quote\'d=[c]  "#emptytit"=[b,c]  "back\\slash"=[a,c]\n');
console.log('=== multi-SELECT: "?" operators, doc gloss "Any/At least one of X" ===');
for(const f of ['opts ?= "b"','opts ?= "a"','opts ?!= "a"','opts ?~ "b"','opts ?!~ "b"',
                'opts ?> "a"','opts ?>= "b"','opts ?< "b"','opts ?<= "a"','opts ?> "b"','opts ?< "c"']){
  const r=await run(f); console.log('  '+f.padEnd(20)+' status='+r.st+' stable='+r.stable+'  -> '+JSON.stringify(r.t));}
console.log('\n=== multi-SELECT: match-all (no "?") counterparts ===');
for(const f of ['opts = "a"','opts != "a"','opts > "a"','opts < "c"','opts ~ "b"']){
  const r=await run(f); console.log('  '+f.padEnd(20)+' status='+r.st+' stable='+r.stable+'  -> '+JSON.stringify(r.t));}
console.log('\n=== control: the SAME ordering operators on a SINGLE-valued text field (note) ===');
console.log('fixture note: plain / "" / pct / us / q / emptytit / bs');
for(const f of ['note > "p"','note >= "p"','note < "p"','note ?> "p"','note ?< "p"']){
  const r=await run(f); console.log('  '+f.padEnd(20)+' status='+r.st+' stable='+r.stable+'  -> '+JSON.stringify(r.t));}
console.log('\n=== control: ordering operators on the multi-RELATION label ===');
for(const f of ['tags.label ?> "alpha"','tags.label ?>= "beta"','tags.label ?< "beta"','tags.label > "alpha"']){
  const r=await run(f); console.log('  '+f.padEnd(24)+' status='+r.st+' stable='+r.stable+'  -> '+JSON.stringify(r.t));}
})();
