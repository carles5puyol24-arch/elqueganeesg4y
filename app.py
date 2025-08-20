import streamlit as st
import random
import json

st.set_page_config(page_title="Sorteo Automático 30K", layout="centered")
st.title("🎮 Sorteo Automático de Seguidores (30.000 jugadores)")

# -----------------------------
# Generador de nombres estilo Instagram (aleatorio)
# -----------------------------
NOMBRES = [
    "andrea","maria","juan","carlos","sofia","laura","alejandro","martin","paula","natalia",
    "sergio","javier","clara","beatriz","diego","lucia","ana","pablo","antonio","david",
    "noa","irene","alba","valeria","hugo","adrian","marcos","bruno","emma","ines",
]
APELLIDOS = ["gomez", "garcia", "ruiz", "lopez", "diaz", "perez", "sanchez", "navarro", "romero", "suarez"]
SUFIJOS = ["_", ".", "x", "xx", "97", "14", "22", "99", "real", "oficial"]

def ig_name():
    base = random.choice(NOMBRES)
    if len(base) > 2 and random.random() < 0.35:
        base = base[:-1] + base[-1] * random.randint(2, 4)
    if random.random() < 0.55:
        base = f"{base}_{random.choice(APELLIDOS)}"
    if random.random() < 0.7:
        s = random.choice(SUFIJOS)
        base = f"{base}{s}"
    return base

# -----------------------------
# Crear 30.000 seguidores
# -----------------------------
followers_py = []
used = set()
while len(followers_py) < 30000:
    n = ig_name()
    if n in used:
        continue
    used.add(n)
    img_id = random.randint(1, 70)
    followers_py.append({"name": n, "avatar": f"https://i.pravatar.cc/150?img={img_id}"})

followers_json = json.dumps(followers_py)

# -----------------------------
# HTML + JS optimizado
# -----------------------------
html = f"""
<div style="text-align:center;">
  <div style="margin:10px 0;">
    <button id="startBtn">▶️ Iniciar</button>
    <button id="pauseBtn">⏸️ Pausar</button>
    <button id="resetBtn">🔄 Reiniciar</button>
  </div>
  <div style="margin:6px 0; color:white;">Pelotas vivas: <span id="aliveCount"></span></div>
  <canvas id="gameCanvas" style="border:2px solid white; background:#111; max-width:95vw;"></canvas>
  <div id="winner" style="color:yellow; font-size:20px; margin-top:14px;"></div>
</div>

<script>
const followers = {followers_json};

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const aliveEl = document.getElementById("aliveCount");
const winnerEl = document.getElementById("winner");

function sizeCanvas() {{
  const maxW = Math.min(window.innerWidth * 0.95, 1200);
  canvas.width  = Math.floor(maxW);
  canvas.height = Math.floor(Math.max(500, Math.min(800, maxW * 0.65)));
}}
sizeCanvas();

class Ball {{
  constructor(follower, id) {{
    this.id = id;
    this.follower = follower;
    this.radius = 4; // pequeño para 30k bolas
    this.x = Math.random() * (canvas.width - 10) + 5;
    this.y = Math.random() * (canvas.height - 10) + 5;
    const speed = 1.6; // base
    const ang = Math.random() * Math.PI * 2;
    this.vx = Math.cos(ang) * speed;
    this.vy = Math.sin(ang) * speed;
    this.life = 10;
    this.image = new Image();
    this.image.src = follower.avatar;
  }}
  draw() {{
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();
    ctx.save();
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(1, this.radius-1), 0, Math.PI*2);
    ctx.clip();
    ctx.drawImage(this.image, this.x-this.radius, this.y-this.radius, this.radius*2, this.radius*2);
    ctx.restore();
    
    // Barra de vida encima
    const barW = this.radius*2;
    const barH = 3;
    ctx.fillStyle = "#555";
    ctx.fillRect(this.x-barW/2, this.y-this.radius-6, barW, barH);
    ctx.fillStyle = "lime";
    ctx.fillRect(this.x-barW/2, this.y-this.radius-6, barW*(this.life/10), barH);
    ctx.strokeStyle = "#000";
    ctx.strokeRect(this.x-barW/2, this.y-this.radius-6, barW, barH);
  }}
  update(dt) {{
    // Velocidad extra si quedan <=10
    let speedFactor = 1;
    if (balls.length <= 10) speedFactor = 1.5;

    this.x += this.vx * dt * speedFactor;
    this.y += this.vy * dt * speedFactor;

    if (this.x - this.radius < 0) {{ this.x = this.radius; this.vx *= -1; }}
    if (this.x + this.radius > canvas.width) {{ this.x = canvas.width - this.radius; this.vx *= -1; }}
    if (this.y - this.radius < 0) {{ this.y = this.radius; this.vy *= -1; }}
    if (this.y + this.radius > canvas.height) {{ this.y = canvas.height - this.radius; this.vy *= -1; }}

    const vmax = 3.5;
    const sp = Math.hypot(this.vx, this.vy);
    if (sp > vmax) {{ this.vx = this.vx/sp*vmax; this.vy=this.vy/sp*vmax; }}
  }}
}}

let balls = followers.map((f,i)=> new Ball(f,i));
const initialCount = balls.length;
let running = false;
let raf = null;
let lastTs = null;

function scaleBalls() {{
  const base = 4;
  const maxR = Math.min(canvas.width, canvas.height)*0.06;
  const factor = Math.sqrt(initialCount / Math.max(1, balls.length));
  const newR = Math.min(base*factor, maxR);
  balls.forEach(b=>b.radius=newR);
}}

// Rejilla espacial optimizada
function handleCollisions() {{
  if (balls.length <= 1) return;
  const r = balls[0].radius||4;
  const cellSize = Math.max(8, r*2+2);
  const grid = new Map();
  function key(ix,iy){{return ix+","+iy;}}
  for(let i=0;i<balls.length;i++){{
    const b=balls[i];
    const ix=Math.floor(b.x/cellSize);
    const iy=Math.floor(b.y/cellSize);
    const k=key(ix,iy);
    if(!grid.has(k)) grid.set(k,[]);
    grid.get(k).push(i);
  }}
  for(let i=0;i<balls.length;i++){{
    const a=balls[i];
    const aix=Math.floor(a.x/cellSize);
    const aiy=Math.floor(a.y/cellSize);
    for(let gx=-1;gx<=1;gx++){{
      for(let gy=-1;gy<=1;gy++){{
        const k=key(aix+gx,aiy+gy);
        const arr=grid.get(k);
        if(!arr) continue;
        for(const j of arr){{
          if(j<=i) continue;
          const b=balls[j];
          const dx=b.x-a.x, dy=b.y-a.y;
          const dist=Math.hypot(dx,dy);
          const minD=a.radius+b.radius;
          if(dist<minD && dist>0){{
            const overlap=(minD-dist)/2;
            const nx=dx/dist, ny=dy/dist;
            a.x-=nx*overlap; a.y-=ny*overlap;
            b.x+=nx*overlap; b.y+=ny*overlap;
            const rvx=b.vx-a.vx, rvy=b.vy-a.vy;
            const vn=rvx*nx+rvy*ny;
            if(vn<0){{
              const imp=-vn;
              a.vx-=nx*imp; a.vy-=ny*imp;
              b.vx+=nx*imp; b.vy+=ny*imp;
            }}
            if(a.life===b.life) (Math.random()<0.5?a:b).life--;
            else if(a.life>b.life) b.life--;
            else a.life--;
          }}
        }}
      }}
    }}
  }}
}}

function drawAll(dt){{
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for(let b of balls) b.update(dt), b.draw();
}}

function step(ts){{
  if(!lastTs) lastTs=ts;
  const dt=Math.min(32,ts-lastTs)/16.6667;
  lastTs=ts;

  handleCollisions();
  balls=balls.filter(b=>b.life>0);
  scaleBalls();
  drawAll(dt);

  aliveEl.textContent=balls.length;

  if(balls.length===1){{
    winnerEl.textContent="🎉 Ganador: "+balls[0].follower.name;
    running=false; raf&&cancelAnimationFrame(raf); raf=null;
    return;
  }}
  if(running) raf=requestAnimationFrame(step);
}}

function start(){{if(running)return; winnerEl.textContent=""; running=true; lastTs=null; raf=requestAnimationFrame(step);}}
function pause(){{running=false; raf&&cancelAnimationFrame(raf); raf=null;}}
function reset(){{pause(); balls=followers.map((f,i)=>new Ball(f,i)); scaleBalls(); aliveEl.textContent=balls.length; winnerEl.textContent=""; ctx.clearRect(0,0,canvas.width,canvas.height); drawAll(1);}}

document.getElementById("startBtn").addEventListener("click",start);
document.getElementById("pauseBtn").addEventListener("click",pause);
document.getElementById("resetBtn").addEventListener("click",reset);

scaleBalls();
aliveEl.textContent=balls.length;
drawAll(1);
start();

window.addEventListener("resize",()=>{{
  const oldW=canvas.width, oldH=canvas.height;
  sizeCanvas();
  const sx=canvas.width/oldW, sy=canvas.height/oldH;
  balls.forEach(b=>{{b.x=Math.max(b.radius,Math.min(canvas.width-b.radius,b.x*sx)); b.y=Math.max(b.radius,Math.min(canvas.height-b.radius,b.y*sy));}});
}});
</script>
"""

st.components.v1.html(html, height=800)
