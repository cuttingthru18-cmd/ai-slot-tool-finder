#!/usr/bin/env python3
"""Rebuild index.html with the new machine. TOYS is spliced in untouched.

The old machine REVEALED a tool. This one makes you want to pull again — which is the
entire point of a slot machine and the thing the old one was missing.

  1. A real LEVER you physically drag down. It resists, springs back, and fires on release.
  2. Real REEL STRIPS that spin, blur, decelerate, and overshoot before settling.
  3. A living BACKGROUND — drifting particles that shift colour with the category.

Everything that worked is preserved: the no-repeat bag shuffle, categories, the card,
copy-for-AI, and the full browsable inventory.
"""
import json, io, os

TOYS = open("/tmp/toys.json", encoding="utf-8").read()

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🎰 AI Slot Tool Finder</title>
<meta name="description" content="Pull the lever, discover a tool you'd never find yourself — 210 hand-curated free tools, toys, and AI wonders. No signup, no tracking, one HTML file.">
<style>
:root{
  --ink:#1c1b18; --bg:#0e0d0b; --panel:#191713; --line:#3a3222;
  --gold:#FFD700; --gold-dim:#8a6a00; --text:#e8e3d6; --dim:#8a8478;
  --mono:'SF Mono',ui-monospace,Menlo,monospace;
  --glow: 0 0 24px rgba(255,215,0,.25);
  --hue: 45;                      /* shifts per category — the bg listens to this */
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--text); min-height:100vh;
  font:400 15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,sans-serif;
  display:flex; flex-direction:column; align-items:center;
  padding:34px 16px 70px; position:relative; overflow-x:hidden;
  -webkit-font-smoothing:antialiased;
}
/* ---------- living background ---------- */
#bg{position:fixed; inset:0; z-index:0; pointer-events:none}
#vig{position:fixed; inset:0; z-index:1; pointer-events:none;
  background:radial-gradient(ellipse at 50% 38%, transparent 30%, rgba(8,7,6,.82) 100%)}
body>*:not(#bg):not(#vig){position:relative; z-index:2}

h1{font-size:clamp(26px,5vw,38px); margin:0 0 10px; letter-spacing:-.01em; text-align:center;
   text-shadow:0 0 30px rgba(255,215,0,.18)}
.sub{color:var(--dim); max-width:600px; text-align:center; margin:0 0 22px; font-size:14.5px}
.sub b{color:var(--gold); font-weight:600}

/* ---------- categories ---------- */
#cats{display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-bottom:14px}
.cat{background:#221d13; color:#c9c4b6; border:1px solid var(--line); border-radius:16px;
  padding:7px 14px; font:700 12px var(--mono); cursor:pointer; transition:.18s}
.cat:hover{border-color:var(--gold-dim); color:var(--text)}
.cat.on{background:var(--gold); color:#141310; border-color:var(--gold); box-shadow:var(--glow)}
#catdesc{font:400 11px/1.6 var(--mono); color:var(--dim); text-align:center;
  max-width:520px; margin:0 auto 24px}

/* ---------- the machine ---------- */
.machine{display:flex; align-items:stretch; gap:0; margin-bottom:34px}
.cabinet{
  background:linear-gradient(#241f16,#171410);
  border:2px solid var(--line); border-right:none;
  border-radius:18px 0 0 18px; padding:22px 24px;
  box-shadow:inset 0 1px 0 rgba(255,215,0,.10), 0 22px 60px rgba(0,0,0,.6);
}
.reels{display:flex; gap:12px; position:relative}
/* the payline — a real slot has one, and it's what your eye locks onto */
.reels::before{content:""; position:absolute; left:-10px; right:-10px; top:50%; height:2px;
  margin-top:-1px; background:linear-gradient(90deg,transparent,rgba(255,215,0,.55),transparent);
  z-index:3; pointer-events:none}
.reel{
  width:104px; height:124px; overflow:hidden; position:relative; border-radius:10px;
  background:linear-gradient(#07060a,#141118 40%,#07060a);
  /* brass rim, not a flat border */
  box-shadow:
    0 0 0 2px #6b5a2e, 0 0 0 3px #2a2418, 0 0 0 4px #8a7233,
    inset 0 14px 22px rgba(0,0,0,.92), inset 0 -14px 22px rgba(0,0,0,.92),
    0 6px 20px rgba(0,0,0,.6);
  transition:box-shadow .35s;
}
/* curved glass: highlight top, shadow bottom, so the strip reads as a CYLINDER */
.reel::after{content:""; position:absolute; inset:0; pointer-events:none; z-index:2;
  background:linear-gradient(180deg,
    rgba(255,255,255,.14) 0%, rgba(255,255,255,.03) 22%,
    transparent 45%, transparent 55%,
    rgba(0,0,0,.30) 78%, rgba(0,0,0,.55) 100%)}
/* each reel flashes as IT lands — the small hit */
.reel.hit{box-shadow:
    0 0 0 2px var(--gold), 0 0 0 3px #2a2418, 0 0 0 4px #8a7233,
    inset 0 14px 22px rgba(0,0,0,.85), inset 0 -14px 22px rgba(0,0,0,.85),
    0 0 26px rgba(255,215,0,.55), 0 6px 20px rgba(0,0,0,.6)}

/* THE WIN — all three fire together once the third one lands. This is the payoff. */
.reel.win{animation:winglow 1.5s cubic-bezier(.22,1,.36,1) 1}
@keyframes winglow{
  0%   {box-shadow:0 0 0 2px var(--gold),0 0 0 3px #2a2418,0 0 0 4px #8a7233,
        inset 0 14px 22px rgba(0,0,0,.85),inset 0 -14px 22px rgba(0,0,0,.85),
        0 0 30px rgba(255,215,0,.6); transform:scale(1)}
  14%  {box-shadow:0 0 0 3px #fff6c9,0 0 0 5px var(--gold),0 0 0 7px #8a7233,
        inset 0 10px 20px rgba(0,0,0,.6),inset 0 -10px 20px rgba(0,0,0,.6),
        0 0 74px rgba(255,215,0,.95), 0 0 130px rgba(255,180,0,.55); transform:scale(1.055)}
  34%  {box-shadow:0 0 0 2px var(--gold),0 0 0 4px #8a7233,
        inset 0 12px 22px rgba(0,0,0,.8),inset 0 -12px 22px rgba(0,0,0,.8),
        0 0 40px rgba(255,215,0,.6); transform:scale(1)}
  52%  {box-shadow:0 0 0 3px #fff6c9,0 0 0 5px var(--gold),0 0 0 7px #8a7233,
        inset 0 10px 20px rgba(0,0,0,.6),inset 0 -10px 20px rgba(0,0,0,.6),
        0 0 66px rgba(255,215,0,.85), 0 0 110px rgba(255,180,0,.45); transform:scale(1.04)}
  100% {box-shadow:0 0 0 2px #6b5a2e,0 0 0 3px #2a2418,0 0 0 4px #8a7233,
        inset 0 14px 22px rgba(0,0,0,.92),inset 0 -14px 22px rgba(0,0,0,.92),
        0 6px 20px rgba(0,0,0,.6); transform:scale(1)}
}
/* the symbol itself pops on the win */
.reel.win .cell{animation:symbolpop 1.5s cubic-bezier(.22,1.5,.36,1) 1}
@keyframes symbolpop{
  0%{transform:scale(1)} 14%{transform:scale(1.18)} 34%{transform:scale(1)}
  52%{transform:scale(1.12)} 100%{transform:scale(1)}
}
/* and the payline blazes across all three */
.reels.win::before{animation:payline 1.5s ease-out 1}
@keyframes payline{
  0%,100%{background:linear-gradient(90deg,transparent,rgba(255,215,0,.55),transparent); height:2px; margin-top:-1px}
  14%,52%{background:linear-gradient(90deg,rgba(255,215,0,0),#fff6c9,rgba(255,215,0,0)); height:4px; margin-top:-2px;
          box-shadow:0 0 22px rgba(255,215,0,.9)}
}
.strip{display:flex; flex-direction:column; will-change:transform}
.cell{height:124px; display:flex; align-items:center; justify-content:center;
  font-size:56px; line-height:1; user-select:none;
  filter:drop-shadow(0 3px 6px rgba(0,0,0,.6))}
.reel.blur .strip{filter:blur(4px) brightness(1.15)}

/* ---------- the lever ---------- */
.leverbox{
  width:78px; background:linear-gradient(#241f16,#171410);
  border:2px solid var(--line); border-left:1px solid #2a2418;
  border-radius:0 18px 18px 0; position:relative;
  box-shadow:0 22px 60px rgba(0,0,0,.6);
}
/* the mount the arm pivots on — a real bolt on the cabinet */
.mount{position:absolute; bottom:16px; left:50%; margin-left:-16px; width:32px; height:14px;
  border-radius:7px; background:linear-gradient(#4a4238,#1b1712);
  box-shadow:inset 0 2px 5px rgba(0,0,0,.8), 0 1px 0 rgba(255,215,0,.08)}
/* the slot the arm rides in */
.track{position:absolute; top:44px; bottom:24px; left:50%; margin-left:-4px; width:8px;
  background:linear-gradient(#050403,#191510); border-radius:4px;
  box-shadow:inset 0 0 8px #000, inset 0 2px 4px rgba(0,0,0,.9)}
.lever{
  position:absolute; top:14px; left:50%; margin-left:-24px;
  width:48px; height:120px; cursor:grab; touch-action:none;
  transition:transform .5s cubic-bezier(.34,1.6,.5,1);   /* springs back and overshoots */
  will-change:transform;
}
.lever:active{cursor:grabbing}
.arm{position:absolute; left:50%; top:40px; width:10px; height:80px; margin-left:-5px;
  background:linear-gradient(90deg,#332e28,#b3aa9b 44%,#332e28);
  border-radius:5px; box-shadow:0 2px 10px rgba(0,0,0,.7)}
.knob{
  position:absolute; top:0; left:0; width:48px; height:48px; border-radius:50%;
  background:radial-gradient(circle at 34% 30%, #ff6055, #c2160b 60%, #6d0a04);
  box-shadow:0 8px 20px rgba(0,0,0,.7), inset 0 -6px 14px rgba(0,0,0,.45),
             inset 0 5px 12px rgba(255,255,255,.30);
}
.hint{position:absolute; bottom:-24px; left:50%; transform:translateX(-50%);
  font:700 9px var(--mono); letter-spacing:.16em; color:var(--gold-dim); white-space:nowrap;
  animation:hintpulse 2.2s ease-in-out infinite; pointer-events:none}
@keyframes hintpulse{0%,100%{opacity:.35; transform:translateX(-50%) translateY(0)}
                     50%{opacity:1; transform:translateX(-50%) translateY(3px)}}
.machine.spinning .hint{opacity:0}

/* ---------- the card ---------- */
.card{display:none; background:linear-gradient(#fffdf5,#f3edda); color:#141310;
  border-radius:16px; padding:22px 24px; margin-top:26px; max-width:520px; width:100%;
  box-shadow:0 24px 60px rgba(0,0,0,.55), 0 0 0 1px rgba(255,215,0,.35);
  animation:land .55s cubic-bezier(.22,1.4,.36,1)}
@keyframes land{0%{opacity:0; transform:translateY(-16px) scale(.94)}
                60%{opacity:1; transform:translateY(3px) scale(1.02)}
                100%{opacity:1; transform:none}}
.card h2{margin:0 0 6px; font-size:23px; letter-spacing:-.01em}
.card p{margin:0 0 16px; color:#4a4438; font-size:15px; line-height:1.55}
.btns{display:flex; gap:9px; flex-wrap:wrap}
.card a.open,.tell{flex:1; min-width:170px; text-align:center; border-radius:9px;
  padding:12px 14px; font:700 12px var(--mono); letter-spacing:.06em; cursor:pointer;
  text-decoration:none; border:1.5px solid #141310; transition:.15s}
.card a.open{background:#141310; color:var(--gold)}
.card a.open:hover{background:#2a2418}
.tell{background:transparent; color:#141310}
.tell:hover{background:#141310; color:var(--gold)}
.tell.done{background:#1a7a45; border-color:#1a7a45; color:#fff}

#inv{margin-top:28px; max-width:660px; width:100%; text-align:center}
#inv summary{font:700 10px var(--mono); letter-spacing:.08em; color:var(--dim); cursor:pointer}
#inv summary:hover{color:var(--gold)}
#inv a{display:inline-block; background:#221d13; border:1px solid var(--line); border-radius:12px;
  padding:4px 10px; margin:3px; font-size:11px; color:#c9c4b6; text-decoration:none; transition:.15s}
#inv a:hover{border-color:var(--gold); color:var(--gold)}
footer{margin-top:34px; font:400 11px var(--mono); color:#544e42; text-align:center}
footer a{color:var(--gold-dim)}

@media (prefers-reduced-motion: reduce){
  *{animation:none !important; transition:none !important}
  .reel.blur .strip{filter:none}
}
@media (max-width:520px){
  .reel{width:76px; height:92px} .cell{height:92px; font-size:42px}
  .leverbox{width:62px} .lever{transform-origin:50% 160px}
}
</style>
</head>
<body>

<canvas id="bg"></canvas><div id="vig"></div>

<h1>🎰 AI Slot Tool Finder</h1>
<p class="sub"><b>210 hand-curated</b> tools, toys and AI wonders — the stuff you'd never find on your own. Pick a category, <b>pull the lever</b>, and the winner opens instantly. Free forever, no signup.</p>

<div id="cats"></div>
<p id="catdesc">All 210 in one machine — pure discovery chaos.</p>

<div class="machine" id="machine">
  <div class="cabinet">
    <div class="reels">
      <div class="reel" id="r1"><div class="strip"></div></div>
      <div class="reel" id="r2"><div class="strip"></div></div>
      <div class="reel" id="r3"><div class="strip"></div></div>
    </div>
  </div>
  <div class="leverbox">
    <div class="hint">PULL ↓</div>
    <div class="track"></div><div class="mount"></div>
    <div class="lever" id="lever" role="button" tabindex="0" aria-label="Pull the lever">
      <div class="arm"></div><div class="knob"></div>
    </div>
  </div>
</div>

<div class="card" id="card">
  <h2 id="tname"></h2>
  <p id="tdesc"></p>
  <div class="btns">
    <a class="open" id="topen" href="#" target="_blank" rel="noopener">OPEN IT →</a>
    <button class="tell" id="ttell" type="button">COPY FOR YOUR AI ASSISTANT</button>
  </div>
</div>

<div id="inv"></div>
<footer>No signup. No tracking. One HTML file. · <a href="https://github.com/cuttingthru18-cmd/ai-slot-tool-finder" target="_blank" rel="noopener">source</a></footer>

<script>
var TOYS=__TOYS__;

/* ============ living background ============
   Three layers so it reads as DEPTH, not a screensaver:
     - far: slow dust
     - mid: drifting orbs that actually travel across the screen
     - near: fast sparks that streak
   Every pull sends a shockwave through it. Hue swings with the category.
   Pauses when the tab is hidden — no reason to burn a laptop battery on decoration. */
(function(){
  var c=document.getElementById('bg'), x=c.getContext('2d');
  var W,H,DPR=Math.min(devicePixelRatio||1,2), hue=45, target=45, pulse=0;
  function size(){ W=c.width=innerWidth*DPR; H=c.height=innerHeight*DPR;
                   c.style.width=innerWidth+'px'; c.style.height=innerHeight+'px'; }
  size(); addEventListener('resize', size);

  function mk(n, cfg){
    var a=[]; for(var i=0;i<n;i++) a.push({
      x:Math.random(), y:Math.random(),
      vx:(Math.random()-.5)*cfg.vx, vy:-(Math.random()*cfg.vy+cfg.vy*.35),
      r:Math.random()*(cfg.r[1]-cfg.r[0])+cfg.r[0],
      a:Math.random()*(cfg.a[1]-cfg.a[0])+cfg.a[0],
      w:Math.random()*6.28, ws:(Math.random()*.5+.2)*cfg.wob
    });
    return a;
  }
  var far  = mk(90,  {vx:.00004, vy:.00008, r:[.6,1.8], a:[.06,.20], wob:.30});
  var mid  = mk(26,  {vx:.00012, vy:.00020, r:[3.0,7.5], a:[.05,.14], wob:.60});
  var near = mk(18,  {vx:.00030, vy:.00055, r:[1.0,2.4], a:[.25,.55], wob:1.0});

  window.__setHue=function(h){ target=h; };
  window.__pulse =function(){ pulse=1; };          // the machine calls this on every pull

  function layer(P,t,boost){
    for(var i=0;i<P.length;i++){
      var p=P[i];
      p.x += p.vx*(1+pulse*2.2); p.y += p.vy*(1+pulse*3.0);
      p.w += p.ws*0.012;
      if(p.y<-.06){ p.y=1.06; p.x=Math.random(); }
      if(p.x<-.06) p.x=1.06; if(p.x>1.06) p.x=-.06;
      var px=(p.x+Math.sin(p.w)*0.012)*W, py=p.y*H;
      var r=p.r*DPR*(1+pulse*0.5), R=r*(boost||6);
      var g=x.createRadialGradient(px,py,0,px,py,R);
      var al=Math.min(1,p.a*(1+pulse*1.6));
      g.addColorStop(0,'hsla('+hue+',92%,66%,'+al+')');
      g.addColorStop(.45,'hsla('+(hue+18)+',92%,58%,'+(al*.35)+')');
      g.addColorStop(1,'hsla('+hue+',92%,58%,0)');
      x.fillStyle=g; x.beginPath(); x.arc(px,py,R,0,6.2832); x.fill();
    }
  }

  var last=0;
  (function loop(t){
    requestAnimationFrame(loop);
    if(document.hidden) return;
    if(t-last<22) return; last=t;                 // ~45fps
    hue += (target-hue)*0.045;
    pulse *= 0.955;                               // shockwave decays
    x.clearRect(0,0,W,H);
    x.globalCompositeOperation='lighter';         // glows ADD — that's what makes it feel lit
    layer(far, t, 7);
    layer(mid, t, 5);
    layer(near,t, 4);
    x.globalCompositeOperation='source-over';
  })(0);
})();

/* ============ the machine ============ */
var E=["♾️","🖥️","🕸️","📼","🏗️","🖖","🧪","🎨","🌊","🎞️","🍬","🪞","🎧","🦖","🎰","💎","🔥","⚡","🎪","🛰️","🧭","🔮"];
var CELL=124, SPINS=34;                                  // strip length before the winner
var machine=document.getElementById('machine');
var lever=document.getElementById('lever'), card=document.getElementById('card');
var reels=[document.getElementById('r1'),document.getElementById('r2'),document.getElementById('r3')];
var strips=reels.map(function(r){return r.querySelector('.strip')});
var spinning=false, bag=[], cat='all';

var CATS=[
 ['all','🎰 Everything',45,'All 210 in one machine — pure discovery chaos.'],
 ['fun','🟣 Fun',285,'Pure toys: sites that exist only to amaze — globes, games, art, sound. Zero productivity, maximum wonder.'],
 ['candy','🟡 Mac Candy',45,'Free apps that make your Mac prettier or smoother — menu bar magic, window tricks, interface glow-ups.'],
 ['agent','🟢 Agent Power',140,'AI tools and playgrounds — things that build, write, research, or act on their own. The future, try-able today.'],
 ['creator','🔵 Creator',205,'Weapons for content makers — editors, converters, audio fixers, screenshot beautifiers.'],
 ['win','🪟 Windows Candy',195,'Free apps that glow up a Windows PC — the other side of the candy store.']
];
var catsEl=document.getElementById('cats');
CATS.forEach(function(c,i){
  var n = c[0]==='all' ? TOYS.length : TOYS.filter(function(t){return t.c===c[0]}).length;
  var b=document.createElement('button');
  b.className='cat'+(i===0?' on':''); b.textContent=c[1]+' ('+n+')';
  b.onclick=function(){
    cat=c[0]; bag=[];
    catsEl.querySelectorAll('.cat').forEach(function(x){x.classList.remove('on')});
    b.classList.add('on');
    document.getElementById('catdesc').textContent=c[3];
    if(window.__setHue) window.__setHue(c[2]);            // background listens
  };
  catsEl.appendChild(b);
});

function rand(a){return a[Math.floor(Math.random()*a.length)]}
/* no-repeat bag: you see everything in a category before anything repeats */
function draw(){
  if(!bag.length){
    bag = (cat==='all'? TOYS.slice() : TOYS.filter(function(t){return t.c===cat}));
    for(var i=bag.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=bag[i];bag[i]=bag[j];bag[j]=t}
  }
  return bag.pop();
}
function buildStrip(el, winner){
  var h='';
  for(var i=0;i<SPINS;i++) h+='<div class="cell">'+rand(E)+'</div>';
  h+='<div class="cell">'+winner+'</div>';
  el.innerHTML=h;
  el.style.transition='none';
  el.style.transform='translateY(0)';
  el.offsetHeight;                                        // force reflow so the reset lands
}
function idle(){ strips.forEach(function(s,i){ s.innerHTML='<div class="cell">'+['🎰','🎁','✨'][i]+'</div>'; }); }
idle();

function spin(){
  if(spinning) return;
  spinning=true; machine.classList.add('spinning'); card.style.display='none';
  var toy=draw();
  reels.forEach(function(r){ r.classList.add('blur') });
  strips.forEach(function(s){ buildStrip(s, toy.e) });

  if(window.__pulse) window.__pulse();                    // shockwave through the background

  [1700,2400,3150].forEach(function(dur,i){
    requestAnimationFrame(function(){
      // rips away, decelerates hard, then SETTLES past the mark and snaps back
      strips[i].style.transition='transform '+dur+'ms cubic-bezier(.08,.82,.16,1.04)';
      strips[i].style.transform='translateY(-'+(SPINS*CELL)+'px)';
    });
    // un-blur just BEFORE it stops — the symbol sharpens as it slows. That's the tell.
    setTimeout(function(){ reels[i].classList.remove('blur') }, dur-380);
    setTimeout(function(){
      // the bounce: a real reel overshoots the payline and kicks back
      strips[i].style.transition='transform 320ms cubic-bezier(.34,1.7,.5,1)';
      strips[i].style.transform='translateY(-'+(SPINS*CELL - 7)+'px)';
      setTimeout(function(){
        strips[i].style.transition='transform 180ms ease-out';
        strips[i].style.transform='translateY(-'+(SPINS*CELL)+'px)';
      },160);
      reels[i].classList.add('hit');                       // small flash as THIS reel lands
      setTimeout(function(){ reels[i].classList.remove('hit') }, 520);

      if(i===2){
        // ALL THREE LANDED — the win. Everything fires at once.
        var reelsEl=document.querySelector('.reels');
        reels.forEach(function(r){ r.classList.remove('hit','win'); });
        reelsEl.classList.remove('win');
        void reels[0].offsetWidth;                         // restart the animation cleanly
        reels.forEach(function(r){ r.classList.add('win') });
        reelsEl.classList.add('win');
        if(window.__pulse) window.__pulse();               // background shockwave on the win
        setTimeout(function(){
          reels.forEach(function(r){ r.classList.remove('win') });
          reelsEl.classList.remove('win');
        }, 1550);
        setTimeout(function(){ land(toy) }, 340);          // card lands INTO the glow
      }
    }, dur);
  });
}

function land(toy){
  spinning=false; machine.classList.remove('spinning');
  document.getElementById('tname').textContent=toy.n;
  document.getElementById('tdesc').textContent=toy.d;
  document.getElementById('topen').href=toy.u;
  var tell=document.getElementById('ttell');
  tell.classList.remove('done'); tell.textContent='COPY FOR YOUR AI ASSISTANT';
  tell.onclick=function(){
    var msg='Please vet and install '+toy.n+' for me: '+toy.u;
    var ok=function(){ tell.classList.add('done'); tell.textContent='COPIED — PASTE TO YOUR AI'; };
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(msg).then(ok,fb); } else fb();
    function fb(){
      var box=document.getElementById('fbbox')||document.createElement('textarea');
      box.id='fbbox'; box.value=msg;
      box.style.cssText='width:100%;margin-top:10px;padding:8px;font-size:12px;border:1.5px solid #141310;border-radius:6px';
      tell.parentElement.parentElement.appendChild(box); box.select();
      tell.textContent='COPY THIS ↓';
    }
  };
  card.style.display='block';
  card.style.animation='none'; card.offsetHeight; card.style.animation='';
}

/* ---- the lever: drag it, feel it resist, let go ---- */
var dragging=false, startY=0, pull=0, MAXPULL=104;
function setPull(p){
  pull=Math.max(0,Math.min(MAXPULL,p));
  lever.style.transition = dragging ? 'none' : '';
  // PULL DOWN. It slides the track. Squashes slightly at full travel so it feels like it bottoms out.
  var sq = 1 - (pull/MAXPULL)*0.06;
  lever.style.transform='translateY('+pull+'px) scaleY('+sq+')';
}
function release(){
  if(!dragging) return;
  dragging=false;
  var fired = pull > MAXPULL*0.55;                       // committed pulls only
  setPull(0);                                            // springs back (CSS bezier overshoots)
  if(fired) spin();
}
lever.addEventListener('pointerdown',function(e){
  if(spinning) return;
  dragging=true; startY=e.clientY; lever.setPointerCapture(e.pointerId);
});
lever.addEventListener('pointermove',function(e){ if(dragging) setPull(e.clientY-startY); });
lever.addEventListener('pointerup',release);
lever.addEventListener('pointercancel',release);
/* click and keyboard still work — dragging is a delight, not a requirement */
lever.addEventListener('click',function(){ if(!spinning && pull===0) spin(); });
lever.addEventListener('keydown',function(e){
  if(e.key==='Enter'||e.key===' '){ e.preventDefault(); if(!spinning) spin(); }
});

/* ---- the whole shelf, browsable ---- */
document.getElementById('inv').innerHTML =
  '<details><summary>INSIDE THE MACHINE — ALL '+TOYS.length+' (click to browse)</summary><div style="margin-top:10px">'
  + TOYS.map(function(t){
      return '<a href="'+t.u+'" target="_blank" rel="noopener">'+t.e+' '+t.n+'</a>';
    }).join('')
  + '</div></details>';
</script>
</body>
</html>
"""

open("index.html", "w", encoding="utf-8").write(HTML.replace("__TOYS__", TOYS))
print(f"  index.html rebuilt · {len(json.loads(TOYS))} tools spliced in untouched")
