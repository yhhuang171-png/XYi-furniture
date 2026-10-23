(() => {
 const preference=matchMedia('(prefers-reduced-motion: reduce)');
 const buttons=[...document.querySelectorAll('.xy-motion-toggle')];
 let paused=false,observer;
 try{paused=localStorage.getItem('xy-motion-paused')==='true'}catch{}
 const reveals=[...document.querySelectorAll('.factory-photo,.factory-text,.mf-process-item,.mf-process>.mf-art,.mf-cap,.section-head')];
 function motion(){
  const enabled=!paused&&!preference.matches;
  document.documentElement.classList.toggle('xy-motion',enabled);
  document.documentElement.classList.toggle('xy-paused',!enabled);
  buttons.forEach(b=>{b.hidden=false;b.textContent=enabled?'Pause motion':'Motion paused';b.setAttribute('aria-pressed',String(!enabled));b.disabled=preference.matches});
  observer?.disconnect();reveals.forEach(n=>n.classList.remove('xy-await'));
  if(!enabled||!('IntersectionObserver' in window))return;
  observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.remove('xy-await');observer.unobserve(e.target)}}),{threshold:.1});
  reveals.forEach(n=>{if(n.getBoundingClientRect().top>innerHeight){n.classList.add('xy-enter','xy-await');observer.observe(n)}});
 }
 buttons.forEach(b=>b.addEventListener('click',()=>{paused=!paused;try{localStorage.setItem('xy-motion-paused',String(paused))}catch{}motion()}));
 preference.addEventListener('change',motion);motion();
 document.querySelectorAll('#dt01-collection .mf-case-visuals,#dt02 .mf-case-visuals').forEach((group,index)=>{
  const figures=[...group.querySelectorAll(':scope > figure')];if(figures.length!==2)return;
  const controls=document.createElement('div');controls.className='xy-switch-controls';controls.setAttribute('role','group');controls.setAttribute('aria-label',`DT0${index+1} image view`);
  group.classList.add('xy-switch');figures.forEach((figure,i)=>{figure.id=`xy-case-${index}-${i}`;const button=document.createElement('button');button.type='button';button.textContent=i?'Concept sketch':'Catalogue product image';button.setAttribute('aria-controls',figure.id);button.setAttribute('aria-pressed',String(i===0));figure.classList.toggle('xy-active',i===0);figure.setAttribute('aria-hidden',String(i!==0));button.addEventListener('click',()=>{figures.forEach((f,k)=>{f.classList.toggle('xy-active',i===k);f.setAttribute('aria-hidden',String(i!==k));controls.children[k].setAttribute('aria-pressed',String(i===k))})});controls.append(button)});
  group.before(controls);const note=document.createElement('p');note.className='xy-switch-note';note.textContent='Visual comparison only. Sketch geometry and catalogue photography / rendering status require factory verification. No engineering transformation is implied.';group.after(note);
 });
 // Local preview must never send a real inquiry or pollute production analytics.
 if(!['www.xy-furniture.com','xy-furniture.com'].includes(location.hostname)){
  document.querySelectorAll('form').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();event.stopImmediatePropagation();const status=form.querySelector('[role="status"],#formStatus')||document.createElement('p');status.setAttribute('role','status');status.textContent='Preview only — no inquiry was sent.';if(!status.parentNode)form.append(status)},true));
 }
})();
