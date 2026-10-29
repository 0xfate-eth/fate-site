(()=>{
 const body=document.body,ui=JSON.parse(document.getElementById('ui-data').textContent);
 const theme=document.querySelector('[data-theme-button]');
 const modes=['auto','light','dark'];
 function readTheme(){try{return localStorage.getItem('fate-theme-v2')||'auto'}catch{return 'auto'}}
 function apply(value){body.dataset.theme=modes.includes(value)?value:'auto';theme.textContent=ui.theme+': '+ui[body.dataset.theme];}
 apply(readTheme());
 theme.addEventListener('click',()=>{const next=modes[(modes.indexOf(body.dataset.theme)+1)%3];apply(next);try{localStorage.setItem('fate-theme-v2',next)}catch{}});
 const dialog=document.getElementById('search-dialog'),input=document.getElementById('query'),results=document.getElementById('results');
 const items=JSON.parse(document.getElementById('search-data').textContent);
 function render(){results.replaceChildren();const q=input.value.trim().toLocaleLowerCase();
 const hits=q?items.filter(x=>(x.title+' '+x.text).toLocaleLowerCase().includes(q)):[];
 if(!q||!hits.length){const p=document.createElement('p');p.className='empty';p.textContent=q?ui.empty:ui.search_start;results.append(p);return;}
 for(const item of hits){const a=document.createElement('a');a.href=item.href;a.className='result';const strong=document.createElement('strong');strong.textContent=item.title;const span=document.createElement('span');span.textContent=item.lede;a.append(strong,span);results.append(a);}}
 document.querySelector('[data-search-open]').addEventListener('click',()=>{dialog.showModal();render();input.focus()});
 document.querySelector('[data-search-close]').addEventListener('click',()=>dialog.close());
 input.addEventListener('input',render);
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dialog.open){e.preventDefault();dialog.close();return;}if(e.key==='/'&&!['INPUT','TEXTAREA'].includes(document.activeElement.tagName)&&!dialog.open){e.preventDefault();dialog.showModal();render();input.focus()}});
 document.querySelectorAll('[data-contact]').forEach(a=>{a.addEventListener('click',e=>{e.preventDefault();window.location.href='mailto:'+atob(a.dataset.contact)})});
 const old={'#verdict':'practice.html','#platform':'practice.html','#knowledge':'practice.html#knowledge','#work':'practice.html','#updates':'updates.html','#about':'about.html'};
 if(body.dataset.page==='index'&&old[location.hash]){location.replace((document.documentElement.lang==='zh-Hant'?'zh-':'')+old[location.hash]);}
})();
