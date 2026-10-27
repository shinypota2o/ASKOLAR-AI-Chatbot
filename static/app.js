const $=s=>document.querySelector(s);
let csrf='',busy=false;
const stage=$('#stage'),messages=$('#messages');
function closeNav(){document.body.classList.remove('nav-open');$('#menu').setAttribute('aria-expanded','false')}
function scrollEnd(){requestAnimationFrame(()=>stage.scrollTop=stage.scrollHeight)}
function message(text,role='bot',options=[]){
 stage.classList.add('chat');const row=document.createElement('div');row.className='message '+role;
 const bubble=document.createElement('div');bubble.className='bubble';bubble.textContent=text;row.append(bubble);messages.append(row);
 if(options.length){const actions=document.createElement('div');actions.className='actions';for(const option of options){const b=document.createElement('button');b.textContent=option;b.onclick=()=>send(option);actions.append(b)}bubble.append(actions)}scrollEnd();
}
async function init(){const r=await fetch('/api/session');if(!r.ok)throw Error('Cannot start session');const data=await r.json();csrf=data.csrf}
function chatView(){closeNav();$('#info-view').hidden=true;stage.hidden=false}
async function send(text){
 if(busy||!text.trim())return;chatView();busy=true;$('#send').disabled=true;
 message(text,'user');$('#input').value='';$('#input').placeholder='ASKOLAR is processing…';
 try{if(!csrf)await init();const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify({message:text})});
 const data=await r.json();if(!r.ok)throw Error(data.text||'Request failed');message(data.text+(data.source?'\nSource: '+data.source:''),'bot',data.options);
 }catch(e){message('Unable to complete the request. '+e.message+' Your message is restored below so you can retry.');$('#input').value=text}
 finally{busy=false;$('#send').disabled=false;$('#input').placeholder='Ask ASKOLAR about scholarships…'}
}
async function clearChat(){if(busy)return;try{if(!csrf)await init();const r=await fetch('/api/session/end',{method:'POST',headers:{'X-CSRF-Token':csrf}});if(!r.ok)throw Error('Could not end the session');csrf='';await init();messages.replaceChildren();stage.classList.remove('chat');chatView();$('#clear-dialog').close()}catch(e){message(e.message)}}
$('#composer').onsubmit=e=>{e.preventDefault();send($('#input').value)};
$('#input').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send(e.target.value)}};
document.querySelectorAll('[data-ask]').forEach(b=>b.onclick=()=>send(b.dataset.ask));
document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{
 const view=b.dataset.go;if(view==='new'){if(!busy)$('#clear-dialog').showModal();return}if(view==='chat'){chatView();return}
 closeNav();stage.hidden=true;const panel=$('#info-view');panel.hidden=false;panel.replaceChildren();
 const title=document.createElement('h1');title.textContent=view==='about'?'About this starter':'Scholarship information';panel.append(title);
 const p=document.createElement('p');p.textContent=view==='about'?
 'Python + Flask now handles the conversation and fictional rule evaluation. No trained intent model, OCR, accounts or verified policy data are included yet. Facts are held in server memory until explicit New chat, restart or 30 minutes of inactivity (cleanup within a further 30 seconds). Closing the browser does not immediately notify the server. Chat messages remain in page memory and disappear on refresh. Use invented facts only.':
 'No verified programs are loaded yet. Demo Scholarship A is fictional: year 2 or higher and a percentage grade of at least 85. These are not PGPC policies.';panel.append(p);
 const button=document.createElement('button');button.className='back';button.textContent='Try fictional demo';button.onclick=()=>send('demo');panel.append(button);
 const back=document.createElement('button');back.className='back';back.textContent='Back to chat';back.onclick=chatView;panel.append(back);
});
$('.brand').onclick=e=>{e.preventDefault();chatView()};$('#keep-chat').onclick=()=>$('#clear-dialog').close();$('#clear-chat').onclick=clearChat;
$('#menu').onclick=()=>{const open=document.body.classList.toggle('nav-open');$('#menu').setAttribute('aria-expanded',String(open))};$('#overlay').onclick=closeNav;
function theme(value){document.documentElement.dataset.theme=value;$('#theme-toggle').textContent=value==='dark'?'Light':'Dark'}
let initial='light';try{initial=localStorage.getItem('askolar-theme')==='dark'?'dark':'light'}catch{}theme(initial);
$('#theme-toggle').onclick=()=>{const value=document.documentElement.dataset.theme==='dark'?'light':'dark';theme(value);try{localStorage.setItem('askolar-theme',value)}catch{}};
$('#mobile-preview').onclick=()=>{const on=document.body.classList.toggle('mobile-preview');$('#mobile-preview').setAttribute('aria-pressed',String(on));$('#mobile-preview').textContent=on?'Desktop view':'Mobile view';closeNav()};
$('#jump').onclick=scrollEnd;stage.addEventListener('scroll',()=>$('#jump').hidden=stage.scrollHeight-stage.scrollTop-stage.clientHeight<160);
init().catch(e=>message(e.message+' Reload to retry.'));
