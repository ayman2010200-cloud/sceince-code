#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds the new multi-page index.html for
"Science Code — مستشار المادة" (Prof. Ayman Mansour)

It keeps the original <head>, <style>, data arrays and the protection suite
from the uploaded index.html, and replaces the navigation layer with:

  * 4 unit covers (Unit Selector)  -> main study topics from the book cover images
  * Unit One lessons 1 & 2 linked to the real lesson HTML files
      - unit 1 .. lesson 1  ->  lesson-1-types-of-chemical-reactions.html
      - unit 1 .. lesson 2  ->  lesson-2-combustion-and-pollution.html
  * Lesson viewer: lesson chrome + inner page tabs (iframe) + back button
  * Feedback area: flashcards component ONLY
"""
import io, os, re, sys

SRC = "uploads/index.html"
OUT = "index.html"

src = io.open(SRC, encoding="utf-8", errors="ignore").read()

# ------------------------------------------------------------------
# 1) NEW CSS  (appended to the original style block, nothing removed)
# ------------------------------------------------------------------
NEW_CSS = r"""
    /* ============================================================
       HUB LAYER — unit covers, lesson viewer, feedback
       (added on top of the original Science Code style)
       ============================================================ */
    .unit-view{display:none}
    .unit-view.active{display:block;animation:viewIn .35s ease both}
    @keyframes viewIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

    /* ---------- unit cover card ---------- */
    .unit-card{
      background:#fff;border:1px solid #e2e8f0;border-radius:24px;overflow:hidden;
      box-shadow:0 16px 40px rgba(15,23,42,.12);margin:22px 0 34px;color:#0f172a;
    }
    .unit-card-head{
      display:flex;align-items:center;gap:16px;padding:16px 20px;color:#fff;
      background:linear-gradient(120deg,var(--uc),var(--uc2));
    }
    .unit-num{
      width:64px;height:64px;flex:0 0 64px;border-radius:18px;display:grid;place-items:center;
      font-size:34px;font-weight:900;line-height:1;
      background:rgba(255,255,255,.20);border:2px solid rgba(255,255,255,.5);
      box-shadow:inset 0 0 18px rgba(255,255,255,.18);
    }
    .unit-head-text{min-width:0}
    .unit-head-text .u-ar{font-size:clamp(1.05rem,2.5vw,1.5rem);font-weight:900;line-height:1.45}
    .unit-head-text .u-en{font-size:.85rem;font-weight:700;opacity:.95;margin-top:3px}
    .unit-body{display:grid;grid-template-columns:1fr 300px;gap:20px;padding:18px}
    .unit-photo{
      width:100%;height:100%;max-height:310px;object-fit:cover;border-radius:18px;
      border:1px solid #e2e8f0;box-shadow:0 8px 20px rgba(15,23,42,.08);
      pointer-events:auto; /* original style disables pointer events on img */
      display:block;
    }
    .lesson-list{list-style:none;display:flex;flex-direction:column;gap:12px;padding:0;margin:0}
    .lesson-item{
      display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:16px;cursor:pointer;
      background:linear-gradient(135deg,#f8fafc,#eef4ff);border:1px solid #dbe4f3;transition:.22s;
      direction:ltr;text-align:left;
    }
    .lesson-item:hover{transform:translateX(5px);border-color:var(--uc);box-shadow:0 12px 24px rgba(15,23,42,.14)}
    .lesson-item .li-num{
      width:42px;height:42px;flex:0 0 42px;border-radius:13px;display:grid;place-items:center;
      font-weight:900;color:#fff;background:linear-gradient(135deg,var(--uc),var(--uc2));font-size:17px;
    }
    .lesson-item .li-text{flex:1;min-width:0}
    .lesson-item .li-ar{display:block;font-weight:900;font-size:1.02rem;color:#0f172a;line-height:1.5}
    .lesson-item .li-en{display:block;font-weight:700;font-size:.79rem;color:#64748b;margin-top:3px}
    .lesson-item .li-go{font-size:1.5rem;line-height:1;color:var(--uc);font-weight:900}
    .lesson-item.locked{opacity:.66;cursor:not-allowed;background:#f8fafc}
    .lesson-item.locked:hover{transform:none;border-color:#dbe4f3;box-shadow:none}
    .pill-soon{
      background:#fef3c7;color:#92400e;font-size:.68rem;font-weight:900;
      padding:5px 10px;border-radius:999px;white-space:nowrap;letter-spacing:.4px;
    }

    /* ---------- lesson viewer ---------- */
    .back-bar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:10px 0 16px}
    .btn.back{background:linear-gradient(135deg,rgba(56,189,248,.24),rgba(139,92,246,.20));border-color:rgba(56,189,248,.55)}
    .btn:disabled{opacity:.4;cursor:not-allowed}
    .lesson-head{
      border-radius:22px;padding:20px 22px;color:#fff;margin-bottom:14px;
      background:linear-gradient(120deg,var(--uc),var(--uc2));
      box-shadow:0 16px 38px rgba(0,0,0,.35);
    }
    .lesson-head .lh-badge{
      display:inline-block;background:rgba(255,255,255,.20);border:1px solid rgba(255,255,255,.5);
      padding:4px 13px;border-radius:999px;font-size:.73rem;font-weight:900;letter-spacing:.7px;text-transform:uppercase;
    }
    .lesson-head h2{margin:11px 0 5px;font-size:clamp(1.2rem,3vw,1.85rem);font-weight:900;line-height:1.35}
    .lesson-head .lh-ar{font-weight:800;opacity:.96;font-size:1rem}

    .page-tabs{display:flex;gap:8px;overflow-x:auto;padding:4px 2px 14px;-webkit-overflow-scrolling:touch}
    .page-tabs::-webkit-scrollbar{height:7px}
    .page-tabs::-webkit-scrollbar-thumb{background:rgba(148,163,184,.5);border-radius:9px}
    .page-tab{
      flex:0 0 auto;
      scroll-margin-inline:20px;padding:9px 15px;border-radius:999px;border:1px solid var(--border);
      background:var(--panel);color:var(--text);font-weight:800;font-size:.82rem;cursor:pointer;
      transition:.2s;white-space:nowrap;font-family:inherit;
    }
    .page-tab:hover{background:rgba(255,255,255,.16)}
    .page-tab.active{
      background:linear-gradient(90deg,var(--blue),var(--purple));color:#fff;border-color:transparent;
      box-shadow:0 0 16px rgba(56,189,248,.40);
    }
    .page-content{
      position:relative;border-radius:20px;overflow:hidden;border:1px solid var(--border);
      background:#fff;box-shadow:0 20px 46px rgba(0,0,0,.40);margin-bottom:34px;
    }
    .lesson-frame{display:block;width:100%;height:84vh;min-height:660px;border:0;background:#fff}
    .page-loader{
      position:absolute;inset:0;display:grid;place-items:center;z-index:6;
      background:rgba(11,18,32,.90);color:#fff;font-weight:800;transition:opacity .35s;
    }
    .page-loader.off{opacity:0;pointer-events:none}
    .pl-inner{text-align:center;padding:20px}
    .spinner{
      width:46px;height:46px;border-radius:50%;margin:0 auto 14px;
      border:4px solid rgba(255,255,255,.22);border-top-color:var(--blue);animation:spin .9s linear infinite;
    }
    @keyframes spin{to{transform:rotate(360deg)}}
    .pl-hint{font-size:.78rem;color:var(--muted);font-weight:600;margin-top:8px;max-width:420px}

    /* ---------- feedback area (flashcards only) ---------- */
    .fb-toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:0 0 6px}
    .fb-search{flex:1;min-width:220px;max-width:460px}
    .fb-count{
      font-weight:900;color:var(--amber);font-size:.85rem;letter-spacing:.4px;
      background:rgba(251,191,36,.12);border:1px solid rgba(251,191,36,.4);
      padding:7px 13px;border-radius:999px;white-space:nowrap;
    }
    .fb-empty{color:var(--muted);font-weight:700;text-align:center;padding:34px 16px;font-size:1rem}
    #feedbackView .flashcard-grid{grid-template-columns:repeat(auto-fit,minmax(215px,1fr))}
    #feedbackView .flashcard-front .flashcard-text{font-size:17px}
    #feedbackView .flashcard-back .flashcard-text{font-size:27px;letter-spacing:1px}

    /* ---------- lesson reading mode: give the lesson the full stage ---------- */
    body.lesson-mode .control-panel{display:none}
    body.lesson-mode .lesson-frame{height:calc(100vh - 46px);min-height:680px}
    body.lesson-mode .container{margin-top:8px}

    .unit-body{align-items:center}
    .unit-photo{width:100%}
    .lesson-list{width:100%}

    /* dynamic sticky offset so the panel never overlaps the topbar */
    .control-panel{top:var(--topbar-h,68px)}
    .cp-header{align-items:center;gap:14px}
    .cp-header .toolbar{margin-inline-start:auto}
    .cp-header .toolbar .btn{font-weight:800}

    @media (max-width:768px){
      body.lesson-mode .lesson-frame{height:82vh}
      .unit-body{grid-template-columns:1fr;padding:14px;gap:14px}
      .unit-photo{max-height:235px;order:-1}
      .unit-num{width:52px;height:52px;flex:0 0 52px;font-size:26px;border-radius:15px}
      .unit-card{border-radius:20px}
      .lesson-item{padding:12px 13px;gap:11px}
      .lesson-item .li-ar{font-size:.95rem}
      .lesson-item:hover{transform:none}
      .lesson-frame{height:78vh;min-height:520px}
      .lesson-head{padding:16px}
      .back-bar .btn{font-size:12px;padding:8px 11px}
      #feedbackView .flashcard-grid{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
    }
"""

# ------------------------------------------------------------------
# 2) NEW SCRIPT (hub logic)
# ------------------------------------------------------------------
NEW_JS = r"""
/* ================================================================
   SCIENCE CODE — HUB LAYER
   Units -> Lessons -> Lesson pages (iframe) + Flashcards feedback
   ================================================================ */

/* Book colours sampled from the textbook cover images */
const BOOK_BLUE   = '#007dc5';
const BOOK_BLUE2  = '#00a7e1';
const BOOK_PURPLE = '#8e52a1';
const BOOK_PURPLE2= '#b06fc4';

const UNITS = [
  {
    num:1, color:BOOK_BLUE, color2:BOOK_BLUE2,
    ar:'التفاعلات الكيميائية وتأثيراتها البيئية',
    en:'Chemical Reactions and Their Environmental Effects',
    enShort:'Chemical Reactions',
    img:'images/unit1-cover.png',
    lessons:[
      {
        ar:'الدرس الأول: أنواع التفاعلات الكيميائية',
        en:'Lesson 1 — Types of Chemical Reactions',
        href:'lesson-1-types-of-chemical-reactions.html',
        pages:[
          {label:'Introduction',            hash:'#intro'},
          {label:'Chemical Reaction',       hash:'#def'},
          {label:'Main Types',              hash:'#types'},
          {label:'Combination (direct union)', hash:'#comb'},
          {label:'Decomposition',              hash:'#dec'},
          {label:'Single substitution',        hash:'#sing'},
          {label:'Activity Series',         hash:'#series'},
          {label:'Metal + water',              hash:'#water'},
          {label:'Metal + salt',               hash:'#salt'},
          {label:'Double substitution',        hash:'#doub'},
          {label:'Oxidation & reduction',      hash:'#redox'},
          {label:'Summary',                 hash:'#summary'},
          {label:'Question Bank',           hash:'#bank'},
          {label:'Self Quiz',               hash:'#quiz'}
        ]
      },
      {
        ar:'الدرس الثاني: تفاعلات الاحتراق والتلوث البيئي',
        en:'Lesson 2 — Combustion Reactions and Environmental Pollution',
        href:'lesson-2-combustion-and-pollution.html',
        pages:[
          {label:'Fire Triangle',           hash:'#triangle'},
          {label:'Matches',                 hash:'#matches'},
          {label:'Metals & Nonmetals',      hash:'#metals'},
          {label:'Flame & Hydrocarbons',    hash:'#hydrocarbons'},
          {label:'Products of Burning',     hash:'#products'},
          {label:'Air Pollution',           hash:'#pollution'},
          {label:'Summary & Quiz',          hash:'#study'}
        ]
      }
    ]
  },
  {
    num:2, color:BOOK_PURPLE, color2:BOOK_PURPLE2,
    ar:'الكهربية والمغناطيسية',
    en:'Electricity and Magnetism',
    enShort:'Electricity & Magnetism',
    img:'images/unit2-cover.png',
    lessons:[
      {ar:'الدرس الأول: التيار الكهربي',            en:'Lesson 1 — Electric Current',              href:'', pages:[]},
      {ar:'الدرس الثاني: الدوائر الكهربية',         en:'Lesson 2 — Electric Circuits',             href:'', pages:[]},
      {ar:'الدرس الثالث: القوى الكهربية والمغناطيسية', en:'Lesson 3 — Electrical and Magnetic Forces', href:'', pages:[]}
    ]
  },
  {
    num:3, color:BOOK_BLUE, color2:BOOK_BLUE2,
    ar:'تنوع الصفات في الكائنات الحية',
    en:'Variation of Traits in Living Organisms',
    enShort:'Variation of Traits',
    img:'images/unit3-cover.png',
    lessons:[
      {ar:'الدرس الأول: الوراثة وتنوع الصفات',       en:'Lesson 1 — Heredity and Variation of Traits', href:'', pages:[]},
      {ar:'الدرس الثاني: الانتخاب الطبيعي والانتخاب الصناعي', en:'Lesson 2 — Natural and Artificial Selection',  href:'', pages:[]}
    ]
  },
  {
    num:4, color:BOOK_PURPLE, color2:BOOK_PURPLE2,
    ar:'تاريخ كوكب الأرض',
    en:'The History of Planet Earth',
    enShort:'History of Earth',
    img:'images/unit4-cover.png',
    lessons:[
      {ar:'الدرس الأول: السجل الحفري',   en:'Lesson 1 — The Fossil Record',   href:'', pages:[]},
      {ar:'الدرس الثاني: الأزمنة الجيولوجية', en:'Lesson 2 — Geological Eras', href:'', pages:[]}
    ]
  }
];

/* ---------------- view state ---------------- */
let currentUnit   = null;
let currentLesson = null;
let currentPage   = 0;
let currentLessonIndex = 0;
window.__lessonMode = false;   /* keeps the protection shield from blurring while reading a lesson */

const VIEW_IDS = ['unitCover1','unitCover2','unitCover3','unitCover4','feedbackView','lessonPage'];

function showView(id){
  VIEW_IDS.forEach(v=>{
    const el = document.getElementById(v);
    if(el) el.classList.toggle('active', v===id);
  });
}

/* ---------------- theme ---------------- */
function toggleTheme(){
  const body = document.body;
  if(body.getAttribute('data-theme')==='light'){
    body.removeAttribute('data-theme');
  }else{
    body.setAttribute('data-theme','light');
  }
  try{ localStorage.setItem('chemTheme', body.getAttribute('data-theme')||'dark'); }catch(e){}
}

/* ---------------- unit covers ---------------- */
function renderCovers(){
  UNITS.forEach(u=>{
    const host = document.getElementById('unitCover'+u.num);
    if(!host) return;
    host.style.setProperty('--uc',  u.color);
    host.style.setProperty('--uc2', u.color2);
    host.innerHTML = `
      <article class="unit-card">
        <div class="unit-card-head">
          <div class="unit-num">${u.num}</div>
          <div class="unit-head-text">
            <div class="u-ar">${u.ar}</div>
            <div class="u-en">${u.en}</div>
          </div>
        </div>
        <div class="unit-body">
          <ul class="lesson-list">
            ${u.lessons.map((l,i)=>{
              const ready = !!(l.href && l.pages && l.pages.length);
              return `
                <li class="lesson-item ${ready ? '' : 'locked'}" onclick="openLesson(${u.num},${i})">
                  <span class="li-num">${i+1}</span>
                  <span class="li-text">
                    <span class="li-ar">${l.ar}</span>
                    <span class="li-en">${l.en}</span>
                  </span>
                  ${ready ? '<span class="li-go">&rsaquo;</span>' : '<span class="pill-soon">SOON</span>'}
                </li>`;
            }).join('')}
          </ul>
          <img class="unit-photo" src="${u.img}" alt="Unit ${u.num} — ${u.en}" loading="lazy">
        </div>
      </article>`;
  });
}

/* ---------------- unit switching ---------------- */
function switchUnit(n){
  document.querySelectorAll('.unit-btn').forEach(b=>b.classList.remove('active'));
  const btn = document.getElementById('u'+n);
  if(btn) btn.classList.add('active');
  window.__lessonMode = false;
  document.body.classList.remove('lesson-mode');
  showView('unitCover'+n);
  const u = UNITS.find(x=>x.num===n);
  showNotification('success','📘','Unit '+n, u ? u.en : 'Unit '+n);
  window.scrollTo({top:0,behavior:'smooth'});
}

/* ---------------- lesson viewer ---------------- */
function openLesson(unitNum, lessonIndex){
  const u = UNITS.find(x=>x.num===unitNum);
  if(!u) return;
  const l = u.lessons[lessonIndex];
  if(!l) return;
  if(!(l.href && l.pages && l.pages.length)){
    showNotification('fail','⏳','Coming soon','This lesson page has not been added yet.');
    return;
  }
  currentUnit = u;
  currentLesson = l;
  currentLessonIndex = lessonIndex;
  currentPage = 0;
  window.__lessonMode = true;
  document.body.classList.add('lesson-mode');
  window.__keepTopOnLoad = true;

  const head = document.getElementById('lessonHead');
  head.style.setProperty('--uc',  u.color);
  head.style.setProperty('--uc2', u.color2);
  head.innerHTML = `
      <span class="lh-badge">Unit ${u.num} — ${u.enShort}</span>
      <h2>${l.en}</h2>
      <div class="lh-ar">${l.ar}</div>`;

  document.getElementById('prevBtn').disabled = !hasNeighbour(-1);
  document.getElementById('nextBtn').disabled = !hasNeighbour(1);

  renderTabs();
  loadPage(0, true);
  showView('lessonPage');
  window.scrollTo({top:0,behavior:'smooth'});
}

function hasNeighbour(step){
  if(!currentUnit) return false;
  const i = currentLessonIndex + step;
  const n = currentUnit.lessons[i];
  return !!(n && n.href && n.pages && n.pages.length);
}

function stepLesson(step){
  const i = currentLessonIndex + step;
  if(hasNeighbour(step)) openLesson(currentUnit.num, i);
}

function renderTabs(){
  const tabs = document.getElementById('pageTabs');
  if(!currentLesson){tabs.innerHTML='';return;}
  tabs.innerHTML = currentLesson.pages.map((p,i)=>
    `<button class="page-tab${i===currentPage?' active':''}" onclick="loadPage(${i})">${i+1}. ${p.label}</button>`
  ).join('');
  tabs.scrollLeft = 0;
}

function loadPage(i, fresh){
  if(!currentLesson) return;
  currentPage = i;
  const p = currentLesson.pages[i];
  const frame = document.getElementById('lessonFrame');
  const loader = document.getElementById('pageLoader');
  const url = currentLesson.href + p.hash;

  document.querySelectorAll('.page-tab').forEach((t,k)=>t.classList.toggle('active', k===i));
  document.getElementById('openTab').href = url;

  if(fresh){
    loader.classList.remove('off');
    setTimeout(()=>loader.classList.add('off'), 4000);   /* safety net */
  }
  frame.setAttribute('src', url);
  if(!fresh){ hideLoader(); }
}

function bindFrame(){
  const f = document.getElementById('lessonFrame');
  if(f) f.addEventListener('load', hideLoader);
}

function hideLoader(){
  const loader = document.getElementById('pageLoader');
  if(loader) loader.classList.add('off');
  /* an iframe that receives focus makes the browser scroll it into view —
     bring the lesson header back to the top instead */
  if(window.__keepTopOnLoad){
    window.__keepTopOnLoad = false;
    setTimeout(function(){ window.scrollTo(0,0); }, 60);
  }
}

function openFeedback(){
  window.__lessonMode = false;
  document.body.classList.remove('lesson-mode');
  showView('feedbackView');
  showNotification('success','🃏','Flashcards','Feedback & self-check area.');
  window.scrollTo({top:0,behavior:'smooth'});
}

function backToUnits(){
  window.__lessonMode = false;
  document.body.classList.remove('lesson-mode');
  const n = currentUnit ? currentUnit.num : 1;
  showView('unitCover'+n);
  window.scrollTo({top:0,behavior:'smooth'});
}

document.addEventListener('keydown', function(e){
  if(e.key === 'Escape'){
    const lessonOpen = document.getElementById('lessonPage').classList.contains('active');
    if(lessonOpen) backToUnits();
  }
});

/* ---------------- flashcards (feedback component) ---------------- */
function renderFlashcards(list){
  const grid = document.getElementById('flashcardGrid');
  const empty = document.getElementById('fbEmpty');
  if(!grid) return;
  const items = list || formulas;
  grid.innerHTML = '';
  items.forEach(item=>{
    const card = document.createElement('div');
    card.className = 'flashcard-container';
    card.dataset.search = (item.name + ' ' + item.formula).toLowerCase();
    card.innerHTML = `
      <div class="flashcard" onclick="this.classList.toggle('flipped')">
        <div class="flashcard-front">
          <div class="flashcard-text">${item.name}</div>
          <div class="flashcard-hint">👆 Click to flip</div>
        </div>
        <div class="flashcard-back">
          <div class="flashcard-text">${item.formula}</div>
          <div class="flashcard-hint">🧪 Formula</div>
        </div>
      </div>`;
    grid.appendChild(card);
  });
  const total = items.length;
  const counter = document.getElementById('fbCount');
  if(counter) counter.textContent = total + (total===1 ? ' flashcard' : ' flashcards');
  if(empty) empty.style.display = total ? 'none' : 'block';
}

function filterFlashcards(query){
  const q = (query||'').trim().toLowerCase();
  let shown = 0;
  document.querySelectorAll('#flashcardGrid .flashcard-container').forEach(card=>{
    const hit = !q || (card.dataset.search||'').includes(q);
    card.style.display = hit ? '' : 'none';
    if(hit) shown++;
  });
  const counter = document.getElementById('fbCount');
  if(counter) counter.textContent = shown + (shown===1 ? ' flashcard' : ' flashcards');
  const empty = document.getElementById('fbEmpty');
  if(empty) empty.style.display = shown ? 'none' : 'block';
}

function shuffleFlashcards(){
  const items = formulas.slice();
  for(let i=items.length-1;i>0;i--){
    const j = Math.floor(Math.random()*(i+1));
    const t = items[i]; items[i]=items[j]; items[j]=t;
  }
  renderFlashcards(items);
  showNotification('success','🔀','Shuffled','Flashcards shuffled for a fresh round.');
  playClickSound();
}

function resetFlashcards(){
  document.querySelectorAll('#flashcardGrid .flashcard.flipped').forEach(c=>c.classList.remove('flipped'));
  const s = document.getElementById('fbSearch');
  if(s) s.value='';
  renderFlashcards();
  playClickSound();
}
"""

# ------------------------------------------------------------------
# 3) NEW BODY MARKUP
# ------------------------------------------------------------------
NEW_BODY = r"""<div class="container">

  <!-- ================= LESSON VIEWER ================= -->
  <main id="lessonPage" class="unit-view">
    <div class="back-bar">
      <button class="btn back" id="backBtn" onclick="backToUnits()"><i class="fa-solid fa-arrow-left"></i> Back to Units</button>
      <button class="btn" id="prevBtn" onclick="stepLesson(-1)">&#8249; Previous lesson</button>
      <button class="btn" id="nextBtn" onclick="stepLesson(1)">Next lesson &#8250;</button>
      <button class="btn" onclick="openFeedback()"><i class="fa-solid fa-layer-group"></i> Flashcards</button>
      <a class="btn" id="openTab" target="_blank" rel="noopener"><i class="fa-solid fa-up-right-from-square"></i> Open in new tab</a>
    </div>
    <div class="lesson-head" id="lessonHead"></div>
    <div class="page-tabs" id="pageTabs"></div>
    <div class="page-content">
      <div class="page-loader" id="pageLoader">
        <div class="pl-inner">
          <div class="spinner"></div>
          <div>Loading lesson page…</div>
          <div class="pl-hint">Tip: keep index.html and the lesson HTML files together in the same folder.</div>
        </div>
      </div>
      <iframe class="lesson-frame" id="lessonFrame" title="Lesson content"></iframe>
    </div>
  </main>

  <!-- ================= UNIT COVERS (main study topics) ================= -->
  <section id="unitCover1" class="unit-view active"></section>
  <section id="unitCover2" class="unit-view"></section>
  <section id="unitCover3" class="unit-view"></section>
  <section id="unitCover4" class="unit-view"></section>

  <!-- ================= FEEDBACK (flashcards only) ================= -->
  <section id="feedbackView" class="unit-view">
    <div class="auto-unit-intro">
      <h2><i class="fa-solid fa-layer-group"></i> Feedback &amp; Self-Check</h2>
      <p>Flip the flashcards, test yourself, then open the full lesson to revise any point you missed.</p>
    </div>

    <h3 class="section-title"><i class="fa-solid fa-bolt"></i> Quick Formula Flashcards — Unit One</h3>

    <div class="fb-toolbar">
      <div class="fb-search">
        <input class="search" id="fbSearch" type="search" placeholder="🔍 Search a term or a formula…" oninput="filterFlashcards(this.value)">
      </div>
      <button class="btn" onclick="shuffleFlashcards()"><i class="fa-solid fa-shuffle"></i> Shuffle</button>
      <button class="btn" onclick="resetFlashcards()"><i class="fa-solid fa-rotate-left"></i> Reset</button>
      <span class="fb-count" id="fbCount"></span>
    </div>

    <div class="flashcard-grid" id="flashcardGrid"></div>
    <div class="fb-empty" id="fbEmpty" style="display:none">No flashcard matches your search.</div>
  </section>
</div>"""

CONTROL_PANEL = r"""<div class="control-panel">
  <div class="cp-header">
    <div class="cp-title"><i class="fa-solid fa-layer-group"></i> Unit Selector</div>
    <div class="toolbar">
      <button class="btn" onclick="openFeedback()"><i class="fa-solid fa-bolt"></i> Flashcards</button>
      <button class="btn" onclick="toggleTheme()"><i class="fa-solid fa-circle-half-stroke"></i> Theme</button>
    </div>
  </div>
  <div class="unit-selector">
    <button class="unit-btn active" onclick="switchUnit(1)" id="u1">Unit One<br><small>Chemical Reactions &mdash; الكيمياء</small></button>
    <button class="unit-btn" onclick="switchUnit(2)" id="u2">Unit Two<br><small>Electricity &mdash; الكهرباء</small></button>
    <button class="unit-btn" onclick="switchUnit(3)" id="u3">Unit Three<br><small>Variation of Traits</small></button>
    <button class="unit-btn" onclick="switchUnit(4)" id="u4">Unit Four<br><small>History of Earth</small></button>
  </div>
</div>"""

NEW_INIT = r"""
function syncTopbarHeight(){
  const tb = document.querySelector('.topbar');
  if(tb) document.documentElement.style.setProperty('--topbar-h', tb.offsetHeight + 'px');
}
window.addEventListener('resize', syncTopbarHeight);

function init(){
  syncTopbarHeight();
  bindFrame();
  setTimeout(syncTopbarHeight, 400);
  renderCovers();
  renderFlashcards();

  try{
    if(localStorage.getItem('chemTheme')==='light'){
      document.body.setAttribute('data-theme','light');
    }
  }catch(e){}

  initProtection();
  showNotification('success','📚','Ready','Science Code loaded — 4 units • 2 lessons live.');
}
"""

# ------------------------------------------------------------------
# 4) ASSEMBLE
# ------------------------------------------------------------------
# -- 4a) inject CSS --
css_close = src.rindex("</style>")
src = src[:css_close] + NEW_CSS + "\n  " + src[css_close:]

# -- 4b) replace the control panel --
cp_start = src.index('<div class="control-panel">')
cp_end   = src.index('<div class="container">', cp_start)
src = src[:cp_start] + CONTROL_PANEL + "\n\n" + src[cp_end:]

# -- 4c) replace the container body (unit content holders) --
old_container_start = src.index('<div class="container">')
contact_marker = '<div class="contact-buttons">'
old_container_end = src.index(contact_marker, old_container_start)
src = src[:old_container_start] + NEW_BODY + "\n\n" + src[old_container_end:]

# -- 4d) rebuild the script --
data_start = src.index("const termsData = [")
render_start = src.index("function renderFlashcards(){")
protection_start = src.index("/* =================== FULL PROTECTION SUITE")
init_call = src.rindex("init();")

part_data = src[data_start:render_start]              # data + helpers (kept as-is)
part_protection = src[protection_start:init_call]     # full protection suite (kept)

# small patch: don't blur the whole hub while a lesson iframe is focused
part_protection = part_protection.replace(
    "function protectOn(){ document.body.classList.add('protected-blur'); if(shield) shield.classList.add('on'); }",
    "function protectOn(){ if(window.__lessonMode && !document.hidden) return; document.body.classList.add('protected-blur'); if(shield) shield.classList.add('on'); }"
)

new_script = part_data + NEW_JS + "\n" + NEW_INIT + "\n" + part_protection + "\ninit();\n"

script_start = src.rindex("<script>", 0, data_start)
script_end = src.rindex("</script>")
src = src[:script_start+len("<script>")] + new_script + src[script_end:]

META = '''  <meta name="description" content="Science Code — Grade 9 science hub by Prof. Ayman Mansour. Unit One: Chemical Reactions and Their Environmental Effects (Lesson 1: Types of Chemical Reactions — Lesson 2: Combustion Reactions and Environmental Pollution) with interactive lesson pages and flashcards. Unit Two: Electricity and Magnetism. Unit Three: Variation of Traits in Living Organisms. Unit Four: The History of Planet Earth." />
  <meta name="author" content="Prof. Ayman Mansour" />
'''
src = src.replace('  <meta name="theme-color" content="#16233b" />', META + '  <meta name="theme-color" content="#16233b" />', 1)

io.open(OUT, "w", encoding="utf-8").write(src)
print("written:", OUT, len(src), "bytes")

# -- 4e) extract the JS for a syntax check --
js = new_script
io.open("/tmp/check.js", "w", encoding="utf-8").write(js)
print("js bytes:", len(js))
