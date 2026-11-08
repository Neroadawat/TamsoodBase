// Scroll-driven fuel story. The illustration is conceptual, not a computed flow diagram.
(function(root){
 const doc=root.document;if(!doc||!doc.querySelector)return;
 const stage=doc.querySelector('.story-visual');if(!stage)return;
 const chapters=[...doc.querySelectorAll('[data-story-step]')],buttons=[...doc.querySelectorAll('[data-story-go]')];
 const reduced=()=>root.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
 function select(index){
  if(!Number.isInteger(index)||index<0||index>=chapters.length)return;
  stage.dataset.stage=String(index);
  doc.querySelector('#story-counter').textContent=String(index+1).padStart(2,'0')+' / 05';
  doc.querySelector('#story-caption').textContent=chapters[index].querySelector('h3').textContent;
  const coverage=doc.querySelector('#story-coverage');if(coverage)coverage.textContent='มีในเว็บ: '+chapters[index].dataset.coverage;
  buttons.forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));
 }
 buttons.forEach(button=>button.addEventListener('click',()=>{
  const index=Number(button.dataset.storyGo);select(index);
  chapters[index].scrollIntoView({behavior:reduced()?'instant':'smooth',block:'start'});chapters[index].focus({preventScroll:true});
 }));
 doc.querySelector('#story-start')?.addEventListener('click',()=>doc.querySelector('#fuel-story').scrollIntoView({behavior:reduced()?'instant':'smooth',block:'start'}));
 doc.querySelectorAll('[data-story-home]').forEach(button=>button.addEventListener('click',()=>{root.dispatchEvent(new CustomEvent('tamsood:navigate',{detail:{view:'catalog'}}));doc.querySelector('#fuel-story').scrollIntoView({behavior:reduced()?'instant':'smooth',block:'start'});}));
 if(root.IntersectionObserver){
  const observer=new root.IntersectionObserver(entries=>{
   const active=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
   if(active)select(Number(active.target.dataset.storyStep));
  },{rootMargin:'-35% 0px -35% 0px',threshold:0});
  chapters.forEach(chapter=>observer.observe(chapter));
 }
 // One queued frame per scroll event: no perpetual render loop or fake data counter.
 if(root.addEventListener&&root.requestAnimationFrame){
  let queued=false;
  const updateProgress=()=>{
   queued=false;if(stage.closest('[hidden]'))return;
   const chapter=chapters[Number(stage.dataset.stage)||0],rect=chapter.getBoundingClientRect();
   const progress=Math.max(0,Math.min(1,(root.innerHeight*.7-rect.top)/(rect.height+root.innerHeight*.4)));
   stage.style.setProperty('--story-progress',String(progress));
  };
  const schedule=()=>{if(!queued){queued=true;root.requestAnimationFrame(updateProgress);}};
  root.addEventListener('scroll',schedule,{passive:true});root.addEventListener('resize',schedule);schedule();
 }
})(typeof window==='undefined'?globalThis:window);
