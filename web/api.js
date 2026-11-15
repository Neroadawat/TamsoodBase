/* Shared API transport for same-origin EC2 and separately hosted frontends. */
(function (root) {
  'use strict';
  function validateBase(value) {
    if (!value) return '';
    const url = new URL(value);
    const local = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
    if (url.username || url.password || url.search || url.hash || url.pathname !== '/' ||
        !(url.protocol === 'https:' || (local && url.protocol === 'http:'))) {
      throw Error('API URL ต้องเป็น HTTPS origin เช่น https://api.example.com โดยไม่ต่อ /api');
    }
    return url.origin;
  }
  let base = '', configurationError = '';
  try { base = validateBase((root.TAMSOOD_CONFIG || {}).apiBaseUrl || ''); }
  catch (error) { configurationError = error instanceof TypeError ? 'ตั้งค่าที่อยู่ backend ไม่ถูกต้อง กรุณาตรวจ API origin' : error.message; }
  function url(path) {
    if (configurationError) throw Error(configurationError);
    const target = new URL(path, base || root.location.origin);
    if (target.origin !== (base || root.location.origin) ||
        !(target.pathname.startsWith('/api/') || ['/readyz', '/healthz'].includes(target.pathname))) {
      throw Error('เส้นทาง API ไม่ถูกต้อง');
    }
    return target.href;
  }
  const pending=new Map(),failures=new Map(),versions=new Map();let serial=0;
  function announce(state,key,id){
    if(state==='loading'){pending.set(id,key);versions.set(key,id);}
    else {pending.delete(id);if(versions.get(key)===id){if(state==='connected')failures.delete(key);else failures.set(key,state);}}
    const states=[...failures.values()];
    const aggregate=states.includes('unauthorized')?'unauthorized':states.length&&states.every(state=>state==='restricted')?'restricted':states.length?'error':pending.size?'loading':'connected';
    root.dispatchEvent(new CustomEvent('tamsood:connection',{detail:{state:aggregate,dataset:key,datasetState:state,pending:pending.size,failedDatasets:[...failures.keys()]}}));
  }
  async function get(path, timeoutMs = 35000, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const key=new URL(path,base||root.location.origin).pathname,id=++serial;
    const abort=()=>controller.abort();if(options.signal){if(options.signal.aborted)abort();else options.signal.addEventListener('abort',abort,{once:true});}
    announce('loading',key,id);
    try {
      const response = await fetch(url(path), { signal: controller.signal, headers: { Accept: 'application/json' } });
      if(response.status===401 && (root.TAMSOOD_CONFIG||{}).loginUrl){
        announce('unauthorized',key,id);
        const error=new Error('กรุณาเข้าสู่ระบบก่อนดูข้อมูล');error.authenticationRequired=true;throw error;
      }
      if (!(response.headers.get('content-type') || '').includes('application/json')) {
        throw Error('ปลายทางไม่ใช่ API ข้อมูล กรุณาตรวจที่อยู่ backend และการตั้งค่า deploy');
      }
      const data = await response.json();
      if (!response.ok) {
        if(response.status===403&&data.error==='ข้อมูลชุดนี้ยังไม่เปิดผ่านเว็บไซต์ระหว่างตรวจสอบสิทธิ์เผยแพร่'){
          announce('restricted',key,id);
          const error=new Error('พักการแสดงข้อมูลชุดนี้ระหว่างตรวจสอบสิทธิ์เผยแพร่');error.accessRestricted=true;throw error;
        }
        throw Error(data.error === 'Search too long' ? 'คำค้นยาวเกินไป กรุณาใช้ไม่เกิน 160 ตัวอักษร' : data.error || 'โหลดข้อมูลไม่สำเร็จ');
      }
      announce('connected',key,id);
      return data;
    } catch (error) {
      if(!error.authenticationRequired&&!error.accessRestricted)announce('error',key,id);
      if (error.name === 'AbortError') throw Error('backend ตอบช้าเกินไป กรุณาลองอีกครั้ง');
      if (error instanceof TypeError) throw Error('เชื่อมต่อ backend ไม่ได้ กรุณาตรวจเครือข่ายและที่อยู่ API');
      throw error;
    } finally { clearTimeout(timer);options.signal?.removeEventListener('abort',abort); }
  }
  root.TamsoodAPI = Object.freeze({ url, get, base, configurationError });
})(window);
