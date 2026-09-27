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
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from add_tools import find_array          # bracket-matcher — do NOT regex the TOYS array

# Read the tools straight out of the live index.html. Self-contained: no temp files, and
# running this never touches the data — the array is spliced back byte-identical.
_here = os.path.dirname(os.path.abspath(__file__))
_html = open(os.path.join(_here, "index.html"), encoding="utf-8").read()
_s, _e = find_array(_html)
TOYS = _html[_s:_e]

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>🎰 AI Slot Tool Finder</title>
<meta name="description" content="Pull the lever, discover a tool you'd never find yourself — __N__ hand-curated free tools, toys, and AI wonders. No signup, no tracking, one HTML file.">
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

/* ---------- jackpot: the rare pull ---------- */
/* A different KIND of result needs a different kind of frame, or it reads as the same
   card with a word added. Gold ground, dark ink, and a ribbon that names it. */
.card.jackpot{
  background:linear-gradient(135deg,#FFE86B,#FFD700 42%,#E0AC00);
  box-shadow:0 24px 70px rgba(0,0,0,.6), 0 0 0 2px #FFF6C9, 0 0 60px rgba(255,215,0,.5);
}
.card.jackpot h2, .card.jackpot p{color:#141310}
.card.jackpot a.open{background:#141310; color:var(--gold)}
.card.jackpot .tell{border-color:#141310; color:#141310}
.card.jackpot .tell:hover{background:#141310; color:var(--gold)}
.ribbon{display:none; font:700 10px var(--mono); letter-spacing:.2em; color:#6d4b00; margin:0 0 8px}
.card.jackpot .ribbon{display:block}
.machine.jackpot .cabinet,.machine.jackpot .leverbox{
  border-color:var(--gold); box-shadow:0 0 50px rgba(255,215,0,.45), 0 22px 60px rgba(0,0,0,.6)}

/* ---------- near-miss: reel 3 stops on the wrong symbol and stares ----------
   A frozen reel reads as a bug. A breathing one reads as a machine deciding. The pulse is
   slow and small on purpose — it should register as hesitation, not as a new animation. */
.reel.tease{animation:teasebreath 900ms ease-in-out infinite}
@keyframes teasebreath{
  0%,100%{box-shadow:
    0 0 0 2px #8a6a00, 0 0 0 3px #2a2418, 0 0 0 4px #8a7233,
    inset 0 14px 22px rgba(0,0,0,.92), inset 0 -14px 22px rgba(0,0,0,.92),
    0 0 10px rgba(255,215,0,.16)}
  50%{box-shadow:
    0 0 0 2px #c79a00, 0 0 0 3px #2a2418, 0 0 0 4px #8a7233,
    inset 0 14px 22px rgba(0,0,0,.86), inset 0 -14px 22px rgba(0,0,0,.86),
    0 0 22px rgba(255,215,0,.40)}
}
/* the symbol it is stuck on leans very slightly — the reel straining against the stop */
.reel.tease .cell{transform:translateY(1.5px)}

/* ---------- sound + counter, sitting with the categories ---------- */
#meta{display:flex; gap:10px; align-items:center; justify-content:center; flex-wrap:wrap; margin:0 0 18px}
#snd{background:#221d13; color:#c9c4b6; border:1px solid var(--line); border-radius:16px;
  padding:6px 13px; font:700 11px var(--mono); letter-spacing:.08em; cursor:pointer; transition:.18s}
#snd:hover{border-color:var(--gold-dim); color:var(--text)}
#snd[aria-pressed="true"]{background:var(--gold); color:#141310; border-color:var(--gold)}
#snd:focus-visible,.cat:focus-visible{outline:2px solid var(--gold); outline-offset:2px}
#found{font:700 11px var(--mono); letter-spacing:.08em; color:var(--dim)}
#found b{color:var(--gold); font-weight:700; font-variant-numeric:tabular-nums}

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
<p class="sub"><b>__N__ hand-curated</b> tools, toys and AI wonders — the stuff you'd never find on your own. Pick a category, <b>pull the lever</b>, and the winner opens instantly. Free forever, no signup.</p>

<div id="cats"></div>
<p id="catdesc">All __N__ in one machine — pure discovery chaos.</p>
<div id="meta">
  <button id="snd" type="button" aria-pressed="false">🔇 SOUND OFF</button>
  <span id="found">FOUND <b>0</b> OF __N__</span>
</div>

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
  <p class="ribbon" id="tribbon">★ JACKPOT PULL</p>
  <h2 id="tname"></h2>
  <p id="tdesc"></p>
  <div class="btns">
    <a class="open" id="topen" href="#" target="_blank" rel="noopener">OPEN IT →</a>
    <button class="tell" id="ttell" type="button">COPY FOR YOUR AI ASSISTANT</button>
    <button class="tell" id="tlink" type="button">COPY LINK TO THIS</button>
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

  /* A win already lights the reels; the ROOM should react too, or the payoff stops at
     the cabinet edge. Sparks are spawned on demand and die off — they are not part of
     the three standing layers, so an idle machine costs nothing extra. */
  var sparks=[];
  window.__burst=function(n,gold){
    for(var i=0;i<n;i++){
      var ang=Math.random()*6.2832, sp=(Math.random()*0.9+0.25);
      sparks.push({x:.5,y:.42,vx:Math.cos(ang)*sp*.0042,vy:Math.sin(ang)*sp*.0042-.0006,
                   life:1,r:Math.random()*2.6+1.2,g:!!gold});
    }
    if(sparks.length>420) sparks.splice(0,sparks.length-420);
  };
  function drawSparks(){
    for(var i=sparks.length-1;i>=0;i--){
      var s=sparks[i];
      s.x+=s.vx; s.y+=s.vy; s.vy+=0.000085;         // a little gravity so they arc, not drift
      s.life-=0.016;
      if(s.life<=0){ sparks.splice(i,1); continue; }
      var px=s.x*W, py=s.y*H, r=s.r*DPR, R=r*5;
      var g=x.createRadialGradient(px,py,0,px,py,R);
      var hh=s.g?48:hue, al=s.life*0.85;
      g.addColorStop(0,'hsla('+hh+',100%,72%,'+al+')');
      g.addColorStop(1,'hsla('+hh+',100%,60%,0)');
      x.fillStyle=g; x.beginPath(); x.arc(px,py,R,0,6.2832); x.fill();
    }
  }

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
    drawSparks();
    x.globalCompositeOperation='source-over';
  })(0);
})();

/* ============ sound ============
   A slot machine with no sound is half a slot machine — the tension lives in the three
   staggered clacks, not in the chime at the end. All of it is synthesised at runtime:
   no files, no network, nothing added to the one-HTML-file promise.

   OFF by default, and it stays off until the visitor asks. Browsers refuse audio before
   a gesture anyway, but the real reason is simpler: people open links at work. */
var SFX=(function(){
  var ac=null, on=false;
  function ctx(){
    if(!ac){ var C=window.AudioContext||window.webkitAudioContext; if(!C) return null; ac=new C(); }
    if(ac.state==='suspended') ac.resume();
    return ac;
  }
  var nb=null;                                    // one noise buffer, reused
  function noise(a){
    if(!nb){
      nb=a.createBuffer(1, Math.floor(a.sampleRate*0.3), a.sampleRate);
      var d=nb.getChannelData(0);
      for(var i=0;i<d.length;i++) d[i]=Math.random()*2-1;
    }
    var s=a.createBufferSource(); s.buffer=nb; return s;
  }
  function shape(g,t,peak,dur){
    g.gain.setValueAtTime(0.0001,t);
    g.gain.exponentialRampToValueAtTime(peak,t+0.004);
    g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
  }
  function tone(freq,dur,peak,type,when){
    var a=ctx(); if(!a||!on) return;
    var t=a.currentTime+(when||0);
    var o=a.createOscillator(), g=a.createGain();
    o.type=type||'sine'; o.frequency.setValueAtTime(freq,t);
    shape(g,t,peak,dur); o.connect(g); g.connect(a.destination);
    o.start(t); o.stop(t+dur+0.02);
  }
  function thud(freq,dur,peak,when){
    var a=ctx(); if(!a||!on) return;
    var t=a.currentTime+(when||0);
    var o=a.createOscillator(), g=a.createGain();
    o.type='sine';
    o.frequency.setValueAtTime(freq,t);
    o.frequency.exponentialRampToValueAtTime(Math.max(20,freq*0.4),t+dur);
    shape(g,t,peak,dur); o.connect(g); g.connect(a.destination);
    o.start(t); o.stop(t+dur+0.02);
  }
  function clack(pitch,when,peak){
    var a=ctx(); if(!a||!on) return;
    var t=a.currentTime+(when||0);
    var s=noise(a), f=a.createBiquadFilter(), g=a.createGain();
    f.type='bandpass'; f.frequency.setValueAtTime(pitch,t); f.Q.value=7;
    shape(g,t,peak||0.30,0.075);
    s.connect(f); f.connect(g); g.connect(a.destination);
    s.start(t); s.stop(t+0.1);
    thud(pitch*0.32,0.09,(peak||0.30)*0.5,when||0);   // the body under the click
  }
  return {
    toggle:function(){ on=!on; if(on){ ctx(); clack(900,0,0.18); } return on; },
    lever:function(){ clack(420,0,0.22); thud(90,0.16,0.30,0.01); },
    reel:function(i){ clack(520+i*190, 0, 0.30); },
    tease:function(){ tone(660,0.09,0.10,'square'); tone(640,0.09,0.09,'square',0.13); },
    win:function(){ [784,988,1319].forEach(function(f,i){ tone(f,0.34,0.13,'triangle',i*0.085); }); },
    jackpot:function(){
      [523,659,784,1047,1319].forEach(function(f,i){ tone(f,0.5,0.14,'triangle',i*0.075); });
      [0,.07,.14,.21,.28,.35].forEach(function(d){ clack(1500+Math.random()*900,d,0.10); });
    }
  };
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
 ['all','🎰 Everything',45,'All __N__ in one machine — pure discovery chaos.'],
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

/* ---- what you've actually seen, across visits ----
   The bag stops repeats inside one session; it forgets on reload. Keeping the set of
   URLs you've landed on turns __N__ from a number in the copy into a number about YOU.
   Storage can be blocked or full (private windows, cleared site data) — every read and
   write is guarded, and the machine works identically when it fails. */
var SEEN=(function(){
  try{ return new Set(JSON.parse(localStorage.getItem('astf.seen')||'[]')); }
  catch(e){ return new Set(); }
})();
var foundEl=document.getElementById('found');
function paintFound(){
  if(foundEl) foundEl.innerHTML='FOUND <b>'+SEEN.size+'</b> OF '+TOYS.length;
}
function markSeen(u){
  if(SEEN.has(u)) return;
  SEEN.add(u);
  try{ localStorage.setItem('astf.seen', JSON.stringify(Array.from(SEEN))); }catch(e){}
  paintFound();
}
paintFound();

/* ---- a spin you can send someone ----
   Every pull used to be a social dead end: a great find, and no way to point at it.
   The slug is derived from the name, so no id has to be stored in tools.json. */
function slug(n){ return n.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); }
function findBySlug(s){
  for(var i=0;i<TOYS.length;i++) if(slug(TOYS[i].n)===s) return TOYS[i];
  return null;
}
function buildStrip(el, winner, decoy){
  var h='';
  for(var i=0;i<SPINS;i++) h+='<div class="cell">'+rand(E)+'</div>';
  // A near-miss needs a WRONG symbol sitting one cell short of the payline, so the reel
  // can stop on it, hold, and then click one more. Without a real cell there, "nearly"
  // is just a pause — and a pause reads as a bug, not as tension.
  if(decoy) h+='<div class="cell">'+decoy+'</div>';
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
  machine.classList.remove('jackpot');
  var toy=draw();
  SFX.lever();

  // A slot machine is compulsive because of the pulls that ALMOST pay, not the ones that
  // do. Two rolls decide the shape of this spin, and they are deliberately lopsided: the
  // jackpot is rare enough to stay special, the near-miss common enough to be felt.
  var jackpot = Math.random() < 0.08;

  // Three of a kind, and on a jackpot they are diamonds instead of the tool's own symbol.
  // A split payline was tried and pulled on 2026-09-27: emoji carry concrete things well
  // and abstract categories badly — a blue circle cannot say "creator", a globe cannot say
  // "website", and labelling the columns only explained a code nobody wanted to learn.
  var symbol = jackpot ? '💎' : toy.e;
  // The wrong symbol reel three creeps onto before it moves one more. ALWAYS built now:
  // the near-miss stopped being an occasional event and became the house move.
  var decoy  = (function(){ var d; do { d=rand(E); } while(d===symbol); return d; })();
  // Vary the stare so the machine never feels metronomic, and let a jackpot hang longer.
  var HOLD   = (jackpot ? 1250 : 820) + Math.round(Math.random()*280);

  reels.forEach(function(r){ r.classList.add('blur') });
  strips.forEach(function(s,i){ buildStrip(s, symbol, i===2?decoy:null) });
  // Cells are 124px on desktop but 92px on mobile (CSS media query). The strip
  // travel is SPINS*CELL, so a HARDCODED CELL landed the reel between cells on
  // phones — the winning symbol fell outside the window and read as blank/glitchy
  // even on a match. Measure the real rendered cell height each spin so it lands
  // dead-center on any screen or orientation.
  CELL = (strips[0].firstElementChild && strips[0].firstElementChild.offsetHeight) || CELL;

  if(window.__pulse) window.__pulse();                    // shockwave through the background

  // the bounce: a real reel overshoots the payline and kicks back
  function bounce(i, cells){
    var y=cells*CELL;
    strips[i].style.transition='transform 320ms cubic-bezier(.34,1.7,.5,1)';
    strips[i].style.transform='translateY(-'+(y-7)+'px)';
    setTimeout(function(){
      strips[i].style.transition='transform 180ms ease-out';
      strips[i].style.transform='translateY(-'+y+'px)';
    },160);
    reels[i].classList.add('hit');                         // small flash as THIS reel lands
    setTimeout(function(){ reels[i].classList.remove('hit') }, 520);
    SFX.reel(i);
  }

  function payout(){
    // ALL THREE LANDED — the win. Everything fires at once.
    var reelsEl=document.querySelector('.reels');
    reels.forEach(function(r){ r.classList.remove('hit','win','tease'); });
    reelsEl.classList.remove('win');
    void reels[0].offsetWidth;                             // restart the animation cleanly
    reels.forEach(function(r){ r.classList.add('win') });
    reelsEl.classList.add('win');
    if(window.__pulse) window.__pulse();                   // background shockwave on the win
    if(window.__burst) window.__burst(jackpot?150:48, jackpot);
    if(jackpot){ machine.classList.add('jackpot'); SFX.jackpot(); } else { SFX.win(); }
    setTimeout(function(){
      reels.forEach(function(r){ r.classList.remove('win') });
      reelsEl.classList.remove('win');
      machine.classList.remove('jackpot');
    }, jackpot?2400:1550);
    setTimeout(function(){ land(toy, jackpot) }, 340);     // card lands INTO the glow
  }

  // ---- reels one and two: they land early and hand the moment over ----
  [1700,2400].forEach(function(dur,i){
    requestAnimationFrame(function(){
      // rips away, decelerates hard, then SETTLES past the mark and snaps back
      strips[i].style.transition='transform '+dur+'ms cubic-bezier(.08,.82,.16,1.04)';
      strips[i].style.transform='translateY(-'+(SPINS*CELL)+'px)';
    });
    // un-blur just BEFORE it stops — the symbol sharpens as it slows. That's the tell.
    setTimeout(function(){ reels[i].classList.remove('blur') }, dur-380);
    setTimeout(function(){ bounce(i, SPINS); }, dur);
  });

  // ---- reel three: the whole point of the pull ----
  // Four phases, and every one of them is doing a job:
  //   1 RIP     it tears down to the cell BEFORE the payline, decelerating the whole way
  //   2 CRAWL   it inches the last cell onto a symbol that does NOT match the other two
  //   3 STARE   it sits there, wrong, long enough that the pull reads as dead
  //   4 CLICK   one more cell, slowly, and the line completes
  // The crawl and the stare ARE the effect. A fast hop between the same positions reads
  // as a stutter; it has to be slow enough that you give up on it first.
  var P1=2600, P2=900, P3=HOLD, P4=560;
  requestAnimationFrame(function(){
    strips[2].style.transition='transform '+P1+'ms cubic-bezier(.05,.75,.12,1)';
    strips[2].style.transform='translateY(-'+((SPINS-1)*CELL)+'px)';
  });
  setTimeout(function(){ reels[2].classList.remove('blur'); }, P1-520);
  setTimeout(function(){
    // the crawl — eased so you can watch it arrive, never a snap
    strips[2].style.transition='transform '+P2+'ms cubic-bezier(.25,.6,.2,1)';
    strips[2].style.transform='translateY(-'+(SPINS*CELL)+'px)';
    SFX.reel(2);
  }, P1);
  setTimeout(function(){
    reels[2].classList.add('tease');        // amber ring: it has stopped, and it is wrong
    SFX.tease();
  }, P1+P2);
  setTimeout(function(){
    reels[2].classList.remove('tease');
    strips[2].style.transition='transform '+P4+'ms cubic-bezier(.3,.85,.25,1.02)';
    strips[2].style.transform='translateY(-'+((SPINS+1)*CELL)+'px)';
    setTimeout(function(){ bounce(2, SPINS+1); payout(); }, P4);
  }, P1+P2+P3);
}

function land(toy, jackpot){
  spinning=false; machine.classList.remove('spinning');
  document.getElementById('tname').textContent=toy.n;
  document.getElementById('tdesc').textContent=toy.d;
  document.getElementById('topen').href=toy.u;
  card.classList.toggle('jackpot', !!jackpot);
  markSeen(toy.u);

  // the pull, addressable. Same page, one query param — nothing to store server-side.
  var link=document.getElementById('tlink');
  link.classList.remove('done'); link.textContent='COPY LINK TO THIS';
  link.onclick=function(){
    var url=location.origin+location.pathname+'?t='+slug(toy.n);
    var ok=function(){ link.classList.add('done'); link.textContent='LINK COPIED'; };
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(url).then(ok,function(){ showFallback(url,link); });
    } else showFallback(url,link);
  };

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
var dragging=false, startY=0, pull=0, MAXPULL=104, moved=false;
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
  dragging=true; moved=false; startY=e.clientY; lever.setPointerCapture(e.pointerId);
});
lever.addEventListener('pointermove',function(e){
  if(!dragging) return;
  var d = e.clientY-startY;
  if(Math.abs(d) > 3) moved=true;                        // a real drag, not a shaky click
  setPull(d);
});
lever.addEventListener('pointerup',release);
lever.addEventListener('pointercancel',release);
/* Click and keyboard still work — dragging is a delight, not a requirement.
   But a drag ALSO emits a click when the pointer comes up, and release() has already
   zeroed `pull` by then. Without this guard that click sails through and spins the
   machine — so a half-hearted nudge you deliberately abandoned would fire anyway,
   and the lever's whole "commit to it" feel would be a lie. If the pointer moved,
   release() already made the call. Say nothing. */
lever.addEventListener('click',function(){
  if(moved){ moved=false; return; }
  if(!spinning && pull===0) spin();
});
lever.addEventListener('keydown',function(e){
  if(e.key==='Enter'||e.key===' '){ e.preventDefault(); if(!spinning) spin(); }
});

/* Clipboard is refused often enough (permissions, older browsers, embedded views) that a
   silent failure would just look like a dead button. Fall back to text you can select. */
function showFallback(text, btn){
  var box=document.getElementById('linkbox')||document.createElement('textarea');
  box.id='linkbox'; box.value=text; box.rows=2;
  box.style.cssText='width:100%;margin-top:10px;padding:8px;font-size:12px;border:1.5px solid #141310;border-radius:6px';
  btn.parentElement.parentElement.appendChild(box); box.select();
  btn.textContent='COPY THIS ↓';
}

/* ---- sound toggle ---- */
var sndBtn=document.getElementById('snd');
sndBtn.addEventListener('click',function(){
  var on=SFX.toggle();
  sndBtn.setAttribute('aria-pressed', on?'true':'false');
  sndBtn.textContent = on ? '🔊 SOUND ON' : '🔇 SOUND OFF';
});

/* ---- spacebar pulls the lever ----
   The lever already takes Enter and Space when it HAS focus. Making space work anywhere
   is what turns it from a page into a machine you sit at. Ignore it while typing, or
   while a control has focus and space already means "activate that". */
document.addEventListener('keydown',function(e){
  if(e.key!==' '&&e.code!=='Space') return;
  var a=document.activeElement, tag=a?a.tagName:'';
  if(tag==='INPUT'||tag==='TEXTAREA'||tag==='SELECT'||tag==='BUTTON'||tag==='A'||tag==='SUMMARY') return;
  if(a&&a.isContentEditable) return;
  e.preventDefault();
  if(!spinning) spin();
});

/* ---- arriving from someone else's link ----
   Land it already won, with no spin: they were sent THIS tool, and making them watch
   three reels to reach it would be theatre at the visitor's expense. */
(function(){
  var m=/[?&]t=([a-z0-9-]+)/i.exec(location.search);
  if(!m) return;
  var toy=findBySlug(m[1].toLowerCase());
  if(!toy) return;
  strips.forEach(function(s){ s.innerHTML='<div class="cell">'+toy.e+'</div>'; });
  land(toy,false);
  var c=document.getElementById('catdesc');
  if(c) c.textContent='Someone sent you this one. Pull the lever for a different find.';
})();

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

_out = os.path.join(_here, "index.html")   # write where we read — never the cwd
_n = len(json.loads(TOYS))   # self-updating count in the prose — never hand-edit again
open(_out, "w", encoding="utf-8").write(HTML.replace("__TOYS__", TOYS).replace("__N__", str(_n)))
print(f"  index.html rebuilt · {_n} tools spliced in untouched")

# The same shelf, in a container a browser is not required to open. The menu bar app
# reads this; without it an app would have to scrape 100KB of HTML and re-parse the
# TOYS array on every poll, which breaks the first time this file's shape changes.
#
# Written from the SAME spliced array, so it can never disagree with the site — there
# is still exactly one source of truth, and it is index.html.
_json_out = os.path.join(_here, "tools.json")
open(_json_out, "w", encoding="utf-8").write(TOYS)
print(f"  tools.json written  · {_n} tools, byte-identical to the site")

# ── README counts, synced from the same array ──────────────────────────────────────
# The page stopped carrying a hardcoded count in 05d566c. The README never did — it
# still said 379 in four places and carried five per-category counts that had to be
# hand-edited together or quietly go wrong. Prose cannot fail a test, so the build
# writes it instead. Every substitution is asserted: if the README wording changes and
# a pattern stops matching, this raises rather than silently leaving a stale number.
import re as _re
from collections import Counter as _Counter

_toys = json.loads(TOYS)
_by_cat = _Counter(t["c"] for t in _toys)
_readme = os.path.join(_here, "README.md")
_r = open(_readme, encoding="utf-8").read()

_subs = [
    (r"\*\*\d+ manually reviewed entries\*\*", f"**{_n} manually reviewed entries**"),
    (r"you'll see all \d+ before any repeat", f"you'll see all {_n} before any repeat"),
    (r"the same \d+ entries the site uses", f"the same {_n} entries the site uses"),
]
_cat_rows = [("🟣 \\*\\*Fun\\*\\*", "fun"), ("🟡 \\*\\*Mac Candy\\*\\*", "candy"),
             ("🟢 \\*\\*Agent Power\\*\\*", "agent"), ("🔵 \\*\\*Creator\\*\\*", "creator"),
             ("🪟 \\*\\*Windows Candy\\*\\*", "win")]
for _label, _key in _cat_rows:
    _subs.append((rf"(\| {_label} \| )\d+( \|)", rf"\g<1>{_by_cat[_key]}\g<2>"))

for _pat, _rep in _subs:
    _r, _k = _re.subn(_pat, _rep, _r)
    if _k == 0:
        raise SystemExit(
            f"README sync FAILED: pattern {_pat!r} matched nothing.\n"
            "The wording changed and a count is now stale. Fix the pattern — do not "
            "hand-edit the number, that is the failure this code exists to prevent."
        )

open(_readme, "w", encoding="utf-8").write(_r)
print(f"  README synced       · {_n} total · " +
      " ".join(f"{k}:{_by_cat[k]}" for k in ("fun", "candy", "agent", "creator", "win")))
