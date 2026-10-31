const $ = s => document.querySelector(s);
let csrf = '', busy = false, lang = 'auto';
const stage = $('#stage'), messages = $('#messages');

// UI text in English and Filipino (Level 1: interface and fixed labels).
const UI = {
  en: {navCurrent: 'Current chat', navNew: 'New chat',
    navScholarships: 'Scholarships', navAbout: 'About ASKOLAR', madeFor: 'Made for PGPC students<small>Group 3 • BSCS 3A</small>',
    welcome: 'How can I help you today?', jump: '↓ Jump to latest', hint: 'Filipino, English or Taglish',
    chipAvail: 'Scholarships', chipReq: 'Requirements', chipElig: 'Check eligibility', chipDeadline: 'Deadlines',
    chipHow: 'How to apply', chipInfo: 'About a program',
    disclaimer: 'Preliminary guidance only. The scholarship office makes the final decision.',
    privacy: 'Temporary session • Deleted after 30 minutes of inactivity', placeholder: 'Ask ASKOLAR about scholarships…',
    typing: 'ASKOLAR is typing', source: 'Source', verified: 'Last verified',
    dlgTitle: 'Start a new chat?', dlgText: 'This will delete the current conversation and your answers. Chat history is not saved.',
    dlgKeep: 'Keep chatting', dlgClear: 'Start new chat', themeDark: 'Switch to dark theme', themeLight: 'Switch to light theme',
    backToChat: 'Back to chat', askAbout: 'Ask about this', openHeading: 'Open to PGPC students', notOpenHeading: 'In ASKOLAR but not open to PGPC students',
    noPrograms: 'No verified programs yet.', loadError: 'The list could not be loaded. Please try again.',
    aboutText: 'ASKOLAR answers PGPC scholarship questions using a Rule-Based Expert System and an intent classifier trained by Group 3. It runs locally with no external AI. Answers come from verified scholarship information; eligibility results are preliminary and the scholarship office decides. Your answers stay in a temporary session and are deleted on New chat or after 30 minutes of inactivity (RA 10173). No account is needed.',
    errorPrefix: 'Unable to complete the request.', errorRestore: 'Your message is restored below so you can retry.',
    uploadTooLarge: 'The image must be smaller than 5 MB. Please type your answer instead.', uploadFailed: 'The document could not be uploaded. Please type your answer instead.'},
  fil: {navCurrent: 'Kasalukuyang chat', navNew: 'Bagong chat',
    navScholarships: 'Mga scholarship', navAbout: 'Tungkol sa ASKOLAR', madeFor: 'Para sa mga PGPC student<small>Group 3 • BSCS 3A</small>',
    welcome: 'Paano kita matutulungan ngayon?', jump: '↓ Pumunta sa pinakabago', hint: 'Filipino, English o Taglish',
    chipAvail: 'Mga scholarship', chipReq: 'Requirements', chipElig: 'Tingnan kung pasok', chipDeadline: 'Deadline',
    chipHow: 'Paano mag-apply', chipInfo: 'Tungkol sa program',
    disclaimer: 'Paunang gabay lamang. Ang scholarship office pa rin ang magdedesisyon.',
    privacy: 'Pansamantalang session • Buburahin pagkalipas ng 30 minutong walang galaw', placeholder: 'Magtanong tungkol sa scholarships…',
    typing: 'Nagta-type si ASKOLAR', source: 'Source', verified: 'Huling na-verify',
    dlgTitle: 'Magsimula ng bagong chat?', dlgText: 'Mabubura ang kasalukuyang usapan at ang mga sagot mo. Hindi sine-save ang chat history.',
    dlgKeep: 'Ituloy ang chat', dlgClear: 'Bagong chat', themeDark: 'Lumipat sa dark theme', themeLight: 'Lumipat sa light theme',
    backToChat: 'Bumalik sa chat', askAbout: 'Itanong ito', openHeading: 'Para sa PGPC students', notOpenHeading: 'Nasa ASKOLAR pero hindi para sa PGPC students',
    noPrograms: 'Wala pang verified na program.', loadError: 'Hindi ma-load ang listahan. Pakisubukan ulit.',
    aboutText: 'Sinasagot ng ASKOLAR ang mga tanong tungkol sa scholarships para sa PGPC students gamit ang Rule-Based Expert System at intent classifier na tinrain ng Group 3. Tumatakbo ito nang local at walang external AI. Galing sa verified na impormasyon ang mga sagot; paunang gabay lang ang eligibility result at ang scholarship office pa rin ang magdedesisyon. Nasa pansamantalang session lang ang mga sagot mo at buburahin sa Bagong chat o pagkalipas ng 30 minutong walang galaw (RA 10173). Hindi kailangan ng account.',
    errorPrefix: 'Hindi natapos ang request.', errorRestore: 'Ibinalik ang mensahe mo sa ibaba para masubukan ulit.',
    uploadTooLarge: 'Dapat mas maliit sa 5 MB ang image. Pakitype na lang ang sagot mo.', uploadFailed: 'Hindi na-upload ang document. Pakitype na lang ang sagot mo.'},
};
// Friendly labels for option buttons; the value sent to ASKOLAR stays the same.
const OPTION_LABELS = {
  en: {'availability': 'Scholarships', 'requirements': 'Requirements', 'eligibility': 'Check eligibility', 'deadline': 'Deadline',
    'application procedure': 'How to apply', 'general info': 'About the program', 'demo': 'Try fictional demo', 'cancel': 'Cancel',
    'confirm': 'Confirm', 'unknown': 'I don’t know', 'I agree': 'I agree', 'why': 'Why?', 'upload grade report': '📎 Upload class card',
    'use these values': 'Use these values', 'type manually': 'Type my answers', 'pgpc residency': 'I live in Lipa',
    'external scholarship': 'A Lipa City scholarship'},
  fil: {'availability': 'Mga scholarship', 'requirements': 'Requirements', 'eligibility': 'Tingnan kung pasok', 'deadline': 'Deadline',
    'application procedure': 'Paano mag-apply', 'general info': 'Tungkol sa program', 'demo': 'Subukan ang demo', 'cancel': 'Cancel',
    'confirm': 'I-confirm', 'unknown': 'Hindi ko alam', 'I agree': 'Pumapayag ako', 'why': 'Bakit?', 'upload grade report': '📎 I-upload ang class card',
    'use these values': 'Gamitin ito', 'type manually': 'I-type ko na lang', 'pgpc residency': 'Taga-Lipa ako',
    'external scholarship': 'Scholarship ng Lipa City'},
};
const optionLabel = value => OPTION_LABELS[uiLang()][value] || value;
let replyLang = 'en';  // language of ASKOLAR's last reply (follows Auto detection)
const uiLang = () => (lang === 'auto' ? replyLang : lang);
const tr = key => UI[uiLang()][key];
function applyLanguage() {
  document.documentElement.lang = uiLang() === 'fil' ? 'fil' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => { el.innerHTML = tr(el.dataset.i18n); });
  $('#input').placeholder = tr('placeholder');
  document.querySelectorAll('[data-lang]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === lang)));
  theme(document.documentElement.dataset.theme || 'light');
}

function closeNav() { document.body.classList.remove('nav-open'); $('#menu').setAttribute('aria-expanded', 'false'); }
function scrollEnd() { requestAnimationFrame(() => { stage.scrollTop = stage.scrollHeight; }); }

function message(text, role = 'bot', options = [], source = null) {
  stage.classList.add('chat');
  const row = document.createElement('div'); row.className = 'message ' + role;
  if (role === 'bot') { const a = document.createElement('img'); a.className = 'avatar'; a.src = '/static/pgpc-logo.png'; a.alt = ''; row.append(a); }
  const bubble = document.createElement('div'); bubble.className = 'bubble'; bubble.textContent = text; row.append(bubble);
  if (source) {
    const card = document.createElement('div'); card.className = 'source';
    card.textContent = tr('source') + ': ' + source; bubble.append(card);
  }
  $('#attach').hidden = !options.includes('upload grade report');
  if (options.length) {
    const actions = document.createElement('div'); actions.className = 'actions';
    for (const option of options) {
      const b = document.createElement('button'); b.textContent = optionLabel(option);
      b.onclick = option === 'upload grade report' ? () => picker.click() : () => send(option, optionLabel(option));
      actions.append(b);
    }
    bubble.append(actions);
  }
  messages.append(row); scrollEnd();
}
function typing(on) {
  const old = $('#typing'); if (old) old.remove(); if (!on) return;
  const row = document.createElement('div'); row.className = 'message bot'; row.id = 'typing';
  row.innerHTML = '<img class="avatar" src="/static/pgpc-logo.png" alt=""><div class="bubble typing"><span></span><span></span><span></span> <em></em></div>';
  row.querySelector('em').textContent = tr('typing'); messages.append(row); scrollEnd();
}

async function init() { const r = await fetch('/api/session'); if (!r.ok) throw Error('Cannot start session'); csrf = (await r.json()).csrf; }
function chatView() { closeNav(); $('#info-view').hidden = true; stage.hidden = false; }

async function send(text, shown) {
  if (busy || !text.trim()) return; chatView(); busy = true; $('#send').disabled = true;
  message(shown || text, 'user'); $('#input').value = ''; typing(true);
  try {
    if (!csrf) await init();
    const r = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf},
      body: JSON.stringify({message: text, lang})});
    const data = await r.json(); if (!r.ok) throw Error(data.text || 'Request failed');
    if (data.lang) { replyLang = data.lang; if (lang === 'auto') applyLanguage(); }
    typing(false); message(data.text, 'bot', data.options || [], data.source);
  } catch (e) { typing(false); message(tr('errorPrefix') + ' ' + e.message + ' ' + tr('errorRestore')); $('#input').value = text; }
  finally { busy = false; $('#send').disabled = false; }
}

// Grade report upload (local OCR). The server deletes the file right after reading it.
const picker = document.createElement('input'); picker.type = 'file'; picker.accept = 'image/png,image/jpeg'; picker.hidden = true; document.body.append(picker);
$('#attach').onclick = () => picker.click();
picker.onchange = async () => {
  const file = picker.files[0]; picker.value = ''; if (!file || busy) return;
  if (file.size > 5 * 1024 * 1024) { message(tr('uploadTooLarge')); return; }
  chatView(); busy = true; $('#send').disabled = true; message('📎 ' + file.name, 'user'); typing(true);
  try {
    if (!csrf) await init(); const form = new FormData(); form.append('file', file);
    const r = await fetch('/api/ocr/extract', {method: 'POST', headers: {'X-CSRF-Token': csrf}, body: form});
    const data = await r.json(); typing(false); message(data.text, 'bot', data.options || []);
  } catch (e) { typing(false); message(tr('uploadFailed')); }
  finally { busy = false; $('#send').disabled = false; }
};

async function clearChat() {
  if (busy) return;
  try {
    if (!csrf) await init();
    const r = await fetch('/api/session/end', {method: 'POST', headers: {'X-CSRF-Token': csrf}});
    if (!r.ok) throw Error('Could not end the session');
    csrf = ''; await init(); messages.replaceChildren(); stage.classList.remove('chat'); $('#attach').hidden = true; chatView(); $('#clear-dialog').close();
  } catch (e) { message(e.message); }
}

$('#composer').onsubmit = e => { e.preventDefault(); send($('#input').value); };
$('#input').onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(e.target.value); } };
document.querySelectorAll('[data-ask]').forEach(b => { b.onclick = () => send(b.dataset.ask, b.textContent); });
document.querySelectorAll('[data-go]').forEach(b => {
  b.onclick = () => {
    const view = b.dataset.go;
    if (view === 'new') { if (!busy) $('#clear-dialog').showModal(); return; }
    if (view === 'chat') { chatView(); return; }
    closeNav(); stage.hidden = true; const panel = $('#info-view'); panel.hidden = false; panel.replaceChildren();
    const title = document.createElement('h1'); title.textContent = view === 'about' ? tr('navAbout') : tr('navScholarships'); panel.append(title);
    if (view === 'about') {
      const p = document.createElement('p'); p.textContent = tr('aboutText'); panel.append(p);
    } else {
      showPrograms(panel);
    }
    const back = document.createElement('button'); back.className = 'back'; back.textContent = tr('backToChat'); back.onclick = chatView; panel.append(back);
  };
});
async function showPrograms(panel) {
  const box = document.createElement('div'); box.className = 'programs'; panel.append(box);
  try {
    const data = await (await fetch('/api/programs')).json();
    const section = (heading, items, open) => {
      const h = document.createElement('h2'); h.textContent = heading; box.append(h);
      if (!items.length) { const p = document.createElement('p'); p.textContent = tr('noPrograms'); box.append(p); }
      for (const item of items) {
        const card = document.createElement('div'); card.className = 'program';
        const name = document.createElement('strong'); name.textContent = item.name; card.append(name);
        const meta = document.createElement('small');
        meta.textContent = open ? `${tr('source')}: ${item.source}` + (item.last_verified ? ` • ${tr('verified')}: ${item.last_verified}` : '') : item.reason;
        card.append(meta);
        const ask = document.createElement('button'); ask.textContent = tr('askAbout');
        ask.onclick = () => send(item.name); card.append(ask); box.append(card);
      }
    };
    section(tr('openHeading'), data.open, true);
    if (data.not_open.length) section(tr('notOpenHeading'), data.not_open, false);
    const demo = document.createElement('button'); demo.className = 'back'; demo.textContent = optionLabel('demo'); demo.onclick = () => send('demo', optionLabel('demo')); box.append(demo);
  } catch (e) { box.textContent = tr('loadError'); }
}
$('.brand').onclick = e => { e.preventDefault(); chatView(); };
$('#keep-chat').onclick = () => $('#clear-dialog').close(); $('#clear-chat').onclick = clearChat;
$('#menu').onclick = () => { const open = document.body.classList.toggle('nav-open'); $('#menu').setAttribute('aria-expanded', String(open)); };
$('#overlay').onclick = closeNav;

function theme(value) {
  document.documentElement.dataset.theme = value;
  const b = $('#theme-toggle'); b.textContent = value === 'dark' ? '☀️' : '🌙';
  b.setAttribute('aria-label', value === 'dark' ? tr('themeLight') : tr('themeDark')); b.title = b.getAttribute('aria-label');
}
let initial = 'light'; try { initial = localStorage.getItem('askolar-theme') === 'dark' ? 'dark' : 'light'; } catch {}
try { lang = localStorage.getItem('askolar-lang') || 'auto'; } catch {}
theme(initial); applyLanguage();
$('#theme-toggle').onclick = () => { const v = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; theme(v); try { localStorage.setItem('askolar-theme', v); } catch {} };
document.querySelectorAll('[data-lang]').forEach(b => { b.onclick = () => { lang = b.dataset.lang; try { localStorage.setItem('askolar-lang', lang); } catch {} applyLanguage(); }; });
$('#jump').onclick = scrollEnd;
stage.addEventListener('scroll', () => { $('#jump').hidden = stage.scrollHeight - stage.scrollTop - stage.clientHeight < 160; });
init().catch(e => message(e.message + ' Reload to retry.'));
