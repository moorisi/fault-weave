const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),repo='moorisi/fault-weave';
const cases={uniform:{weights:[1,1,1,1],threshold:3,quorums:[7,11,13,14]},core:{weights:[0,1,1,1],threshold:2,quorums:[6,10,12]},impossible:{status:'BLOCKED'}};
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const equal=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b)),clone=x=>JSON.parse(JSON.stringify(x));
function assert(ok,message){if(!ok)throw Error(message);}
function descriptor(id,revision){return {url:`https://raw.githubusercontent.com/${repo}/${revision}/fixtures/${id}.json`,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'fixtures',id+'.json'))).digest('hex')};}
function args(id,revision,accounts){const d=descriptor(id,revision);return [repo,'release-register',['Aspen','Birch','Cedar','Dogwood'],accounts,d.url,d.sha256];}
function configuration(a){return {repository:a[0],register:a[1],labels:a[2],signers:a[3],url:a[4],sha256:a[5]};}
const empty={status:'UNCOMPILED',weights:[],threshold:0,quorums:[],witness:[]};
function initial(id,revision,accounts){return {configuration:configuration(args(id,revision,accounts)),assessment:null,policy:clone(empty),nonce:0,value:'',proposals:[],history:[]};}
const members=m=>[0,1,2,3].filter(i=>m&(1<<i));
function model(id){return {faults:Array.from({length:16},(_,m)=>id==='core'?Number((m&~1)===0):Number(members(m).length<=(id==='impossible'?2:1))),outages:Array.from({length:16},(_,m)=>Number(members(m).length<=1))};}
function oracle(faults,outages){
 // Independent truth-table oracle: checks ALL winning coalitions, rather than
 // only their minimal antichain as the contract does.
 const n=Math.log2(faults.length),full=faults.length-1,bad=membersOf(faults),down=membersOf(outages);
 for(const a of down)for(const b of down)for(const f of bad)if((((full^a)&(full^b))&~f)===0)return {status:'BLOCKED',weights:[],threshold:0,quorums:[],witness:[a,b,f]};
 let best;
 for(let code=1;code<3**n;code++){
  let v=code;const weights=Array.from({length:n},()=>{const w=v%3;v=Math.floor(v/3);return w;}),total=weights.reduce((a,b)=>a+b,0);
  for(let threshold=1;threshold<=total;threshold++){
   const winning=Array.from({length:full},(_,i)=>i+1).filter(m=>weights.reduce((s,w,i)=>s+((m&(1<<i))?w:0),0)>=threshold);
   if(down.some(o=>!winning.some(q=>(q&o)===0)))continue;
   if(winning.some(a=>winning.some(b=>bad.some(f=>((a&b)&~f)===0))))continue;
   const quorums=winning.filter(m=>!winning.some(q=>q!==m&&(q&m)===q)),sizes=quorums.map(m=>Array.from({length:n},(_,i)=>Number(Boolean(m&(1<<i)))).reduce((a,b)=>a+b,0));
   const rank=[Math.max(...sizes),sizes.reduce((a,b)=>a+b,0),total,threshold,...weights];
   if(!best||compare(rank,best.rank)<0)best={rank,weights,threshold,quorums};
  }
 }
 return best?{status:'ACTIVE',weights:best.weights,threshold:best.threshold,quorums:best.quorums,witness:[]}:{status:'UNSUPPORTED',weights:[],threshold:0,quorums:[],witness:[]};
}
function membersOf(v){return v.map((x,i)=>x===1?i:-1).filter(x=>x>=0);}
function compare(a,b){for(let i=0;i<a.length;i++)if(a[i]!==b[i])return a[i]-b[i];return 0;}
function check(s,id,revision,accounts){
 assert(Object.keys(s).sort().join(',')==='assessment,configuration,history,nonce,policy,proposals,value','Exact whole state');
 assert(equal(s.configuration,configuration(args(id,revision,accounts))),'Immutable source and signer roster');
 assert(Number.isSafeInteger(s.nonce)&&s.nonce>=0&&s.nonce<=32&&s.history.length===s.nonce&&s.proposals.length<=128,'Bounded nonce and proposal histories');
 if(s.assessment!==null){
  const a=s.assessment,source=JSON.parse(fs.readFileSync(path.join(root,'fixtures',id+'.json'))),m=model(id);
  assert(Object.keys(a).sort().join(',')==='model,source'&&equal(a.source,source)&&Object.keys(a.model).sort().join(',')==='anchors,faults,outages'&&equal(a.model.faults,m.faults)&&equal(a.model.outages,m.outages),'Full source and all 32 failure decisions');
  assert(Array.isArray(a.model.anchors)&&a.model.anchors.length===2&&a.model.anchors.every(v=>Array.isArray(v)&&v.length>=1&&v.length<=6&&v.every(j=>Number.isInteger(j)&&j>=0&&j<source.clauses.length)&&equal(v,[...new Set(v)].sort((a,b)=>a-b))),'Material source anchors');
  assert(equal(s.policy,oracle(m.faults,m.outages)),'Exact independently optimized policy or impossibility witness');
 }else assert(equal(s.policy,empty),'Uncompiled policy');
 for(const p of s.proposals)assert(Object.keys(p).sort().join(',')==='endorsements,nonce,proposer,value'&&Number.isInteger(p.endorsements)&&p.endorsements>=0&&p.endorsements<=15&&Number.isInteger(p.proposer)&&p.proposer>=0&&p.proposer<4,'Native signer-bound proposals');
 for(const [i,h] of s.history.entries())assert(h.nonce===i&&h.value===s.proposals[h.proposal_id].value&&s.proposals[h.proposal_id].nonce===i,'Executed proposal linkage');
 assert(s.value===(s.history.at(-1)?.value||''),'Register equals last authorized update');
}
function plan(id){
 const p=[],add=(label,caller,method,args=[],error)=>p.push({label:id+'-'+label,caller,method,args,...(error?{error}:{})});
 add('compile',3,'compile');
 if(id==='impossible'){
  add('reject-proposal',0,'propose',['bypass'],'[EXPECTED] Active quorum required');add('reject-execution',1,'execute',[0],'[EXPECTED] Active quorum required');
 }else if(id==='uniform'){
  add('propose-first',0,'propose',['release-a']);add('propose-competing',1,'propose',['release-b']);
  add('endorse-aspen',0,'endorse',[0]);add('endorse-birch',1,'endorse',[0]);
  add('reject-two-signers',3,'execute',[0],'[EXPECTED] Quorum not met');
  add('revoke-birch',1,'revoke',[0]);add('endorse-cedar',2,'endorse',[0]);add('endorse-dogwood',3,'endorse',[0]);
  add('execute-without-birch',1,'execute',[0]);add('reject-stale-competitor',0,'execute',[1],'[EXPECTED] Stale proposal');
 }else{
  add('propose-first',0,'propose',['core-release-a']);add('zero-weight-aspen',0,'endorse',[0]);add('endorse-birch',1,'endorse',[0]);
  add('reject-one-trusted',3,'execute',[0],'[EXPECTED] Quorum not met');add('endorse-cedar',2,'endorse',[0]);add('execute-first',0,'execute',[0]);
  add('propose-next',3,'propose',['core-release-b']);add('next-birch',1,'endorse',[1]);add('next-dogwood',3,'endorse',[1]);add('execute-next',2,'execute',[1]);
 }
 return p;
}
function replay(before,item,after,id,revision,accounts){
 check(before,id,revision,accounts);check(after,id,revision,accounts);
 if(item.error){assert(equal(before,after),'Expected rejection changed state');return;}
 const e=clone(before);
 if(item.method==='compile'){e.assessment=clone(after.assessment);const m=model(id);e.policy=oracle(m.faults,m.outages);}
 else if(item.method==='propose')e.proposals.push({nonce:e.nonce,proposer:item.caller,value:item.args[0],endorsements:0});
 else if(item.method==='endorse')e.proposals[item.args[0]].endorsements|=(1<<item.caller);
 else if(item.method==='revoke')e.proposals[item.args[0]].endorsements&=~(1<<item.caller);
 else if(item.method==='execute'){
  const k=item.args[0],p=e.proposals[k];assert(p.nonce===e.nonce&&e.policy.weights.reduce((s,w,i)=>s+((p.endorsements&(1<<i))?w:0),0)>=e.policy.threshold,'Exact live signature threshold');
  e.value=p.value;e.history.push({nonce:e.nonce,proposal_id:k,value:p.value,endorsements:p.endorsements});e.nonce++;
 }else throw Error('Unknown scenario method');
 assert(equal(e,after),'Independent full-state replay: '+item.label);
}
module.exports={cases,args,descriptor,initial,plan,replay,oracle,check,model};
