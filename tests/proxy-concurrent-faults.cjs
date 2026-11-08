const assert=require('node:assert/strict');
const {EventEmitter}=require('node:events');
const fs=require('node:fs'),path=require('node:path');
const https=require('node:https');
const handler=require('../api/[route].js');
process.env.TAMSOOD_BACKEND_ORIGIN='https://test.trycloudflare.com';
process.env.TAMSOOD_BACKEND_AUTH='Basic dGVzdDp0ZXN0';
delete process.env.TAMSOOD_BACKEND_ALLOWED_ORIGINS;
const saved={request:https.request,setTimeout:global.setTimeout,clearTimeout:global.clearTimeout};
const requests=[],timers=[],responses=[];
let callbackDestroyCount=0;
try{
 global.setTimeout=(callback,delay)=>{assert.equal(delay,28000);const timer={callback,cleared:false,unref(){}};timers.push(timer);return timer;};
 global.clearTimeout=timer=>{if(timer)timer.cleared=true;};
 https.request=(url,options,callback)=>{
  const request=new EventEmitter();request.end=()=>{};request.cancelled=0;
  request.destroy=()=>{request.cancelled++;request.emit('error',Error('simulated interruption'));};
  request.reply=()=>{
   const upstream=new EventEmitter();upstream.statusCode=200;upstream.headers={'content-type':'application/json'};
   upstream.resume=()=>{};upstream.destroy=()=>{callbackDestroyCount++;};callback(upstream);
   upstream.emit('data',Buffer.from('{"rows":[],"total":0,"manifest":{}}'));upstream.emit('end');
  };requests.push(request);return request;
 };
 for(let index=0;index<12;index++){
  const response=Object.assign(new EventEmitter(),{ends:0,setHeader(){},end(){this.ends++;this.writableEnded=true;this.emit('finish');}});
  responses.push(response);handler({url:'/api/reference',method:'GET',headers:{}},response);
 }
 assert.equal(requests.length,12);assert.equal(timers.length,12);
 for(let index=0;index<12;index++){
  if(index%3===0){timers[index].callback();assert.equal(responses[index].statusCode,504);requests[index].reply();}
  else if(index%3===1){responses[index].emit('close');requests[index].reply();}
  else requests[index].reply();
 }
 for(let index=0;index<12;index++){
  assert.equal(requests[index].cancelled,index%3===2?0:1);
  assert.equal(responses[index].ends,index%3===1?0:1);
  if(index%3===2)assert.equal(responses[index].statusCode,200);
  assert.equal(timers[index].cleared,true);
 }
 assert.equal(callbackDestroyCount,8);
 const report={checked_at_utc:new Date().toISOString(),scope:'LOCAL_PROXY_CONCURRENT_FAULT_SIMULATION_NOT_PRODUCTION',
  overlapping_requests:12,deadline504:4,disconnects_cancelled:4,successful_responses:4,
  late_callbacks_ignored:8,no_cross_request_cancellation:true,no_duplicate_response_end:true,real_network_requests:0,passed:true};
 fs.writeFileSync(path.join(__dirname,'../evidence/local-proxy-faults-2026-11-08.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
}finally{https.request=saved.request;global.setTimeout=saved.setTimeout;global.clearTimeout=saved.clearTimeout;}
