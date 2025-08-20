import streamlit as st
import random
import json

st.set_page_config(page_title="Sorteo Automático", layout="centered")
st.title("🎮 Sorteo Automático de Seguidores (300 jugadores)")

# -----------------------------
# Generador de nombres estilo Instagram (se regeneran en cada carga)
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
    # A veces repetir la última letra: "mariaaa"
    if len(base) > 2 and random.random() < 0.35:
        base = base[:-1] + base[-1] * random.randint(2, 4)
    # A veces añadir apellido
    if random.random() < 0.55:
        base = f"{base}_{random.choice(APELLIDOS)}"
    # Añadir sufijo o números
    if random.random() < 0.7:
        s = random.choice(SUFIJOS)
        if s.isdigit():
            base = f"{base}{s}"
        else:
            base = f"{base}{s}"
    return base

# -----------------------------
# Crear 300 seguidores con nombres y avatares
# -----------------------------
followers_py = []
used = set()
while len(followers_py) < 300:
    n = ig_name()
    if n in used:
        continue
    used.add(n)
    img_id = random.randint(1, 70)
    followers_py.append({"name": n, "avatar": f"https://i.pravatar.cc/100?img={img_id}"})

followers_json = json.dumps(followers_py)  # para insertarlo seguro en JS

# -----------------------------
# HTML + JS (con optimizaciones)
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
  const maxW = Math.min(window.innerWidth * 0.95, 1000);
  canvas.width  = Math.floor(maxW);
  canvas.height = Math.floor(Math.max(420, Math.min(700, maxW * 0.62)));
}}
sizeCanvas();

class Ball {{
  constructor(follower, id) {{
    this.id = id;
    this.follower = follower;
    this.radius = 8; // tamaño base (cambiará dinámicamente)
    // Posición aleatoria segura
    this.x = Math.random() * (canvas.width - 40) + 20;
    this.y = Math.random() * (canvas.height - 40) + 20;
    const speed = 2.0;
    const ang = Math.random() * Math.PI * 2;
    this.vx = Math.cos(ang) * speed;
    this.vy = Math.sin(ang) * speed;
    this.life = 10;
    this.image = new Image();
    this.image.src = follower.avatar;
  }}
  draw() {{
    // Base
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();

    // Avatar recortado
    ctx.save();
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(1, this.radius - 1), 0, Math.PI*2);
    ctx.clip();
    ctx.drawImage(this.image, this.x - this.radius, this.y - this.radius, this.radius*2, this.radius*2);
    ctx.restore();

    // Vida (número)
    ctx.fillStyle = "red";
    ctx.font = "bold 10px Arial";
    ctx.textAlign = "center";
    ctx.fillText(this.life, this.x, this.y + 3);
  }}
  update(dt) {{
    // Integración simple
    this.x += this.vx * dt;
    this.y += this.vy * dt;

    // Rebote con paredes
    if (this.x - this.radius < 0) {{ this.x = this.radius; this.vx *= -1; }}
    if (this.x + this.radius > canvas.width) {{ this.x = canvas.width - this.radius; this.vx *= -1; }}
    if (this.y - this.radius < 0) {{ this.y = this.radius; this.vy *= -1; }}
    if (this.y + this.radius > canvas.height) {{ this.y = canvas.height - this.radius; this.vy *= -1; }}

    // Limitar velocidad máxima para que no "se desboque"
    const vmax = 3.2;
    const sp = Math.hypot(this.vx, this.vy);
    if (sp > vmax) {{
      this.vx = this.vx / sp * vmax;
      this.vy = this.vy / sp * vmax;
    }}
  }}
}}

let balls = followers.map((f, i) => new Ball(f, i));
const initialCount = balls.length;

let running = false;
let raf = null;
let lastTs = null;

// Crecimiento controlado del radio (limitado a un máximo del 6% del lado menor)
function scaleBalls() {{
  const base = 8;
  const maxR = Math.min(canvas.width, canvas.height) * 0.06; // ~24-40px según pantalla
  const factor = Math.sqrt(initialCount / Math.max(1, balls.length)); // crece suave
  const newR = Math.min(base * factor, maxR);
  balls.forEach(b => b.radius = newR);
}}

// Rejilla espacial para acelerar colisiones
function handleCollisions() {{
  if (balls.length <= 1) return;

  // El tamaño de celda depende del radio actual
  const r = balls[0].radius || 10;
  const cellSize = Math.max(16, r * 2 + 6);

  // Construir grid: clave "ix,iy" -> array de índices
  const grid = new Map();
  function key(ix, iy) {{ return ix + "," + iy; }}

  for (let i = 0; i < balls.length; i++) {{
    const b = balls[i];
    const ix = Math.floor(b.x / cellSize);
    const iy = Math.floor(b.y / cellSize);
    const k = key(ix, iy);
    if (!grid.has(k)) grid.set(k, []);
    grid.get(k).push(i);
  }}

  // Colisiones sólo con vecinos cercanos (9 celdas)
  for (let i = 0; i < balls.length; i++) {{
    const a = balls[i];
    const aix = Math.floor(a.x / cellSize);
    const aiy = Math.floor(a.y / cellSize);

    for (let gx = -1; gx <= 1; gx++) {{
      for (let gy = -1; gy <= 1; gy++) {{
        const k = key(aix + gx, aiy + gy);
        const arr = grid.get(k);
        if (!arr) continue;
        for (const j of arr) {{
          if (j <= i) continue;
          const b = balls[j];

          const dx = b.x - a.x, dy = b.y - a.y;
          const dist = Math.hypot(dx, dy);
          const minD = a.radius + b.radius;

          if (dist < minD && dist > 0) {{
            // Separación mínima para evitar pegado
            const overlap = (minD - dist) / 2;
            const nx = dx / dist, ny = dy / dist;
            a.x -= nx * overlap; a.y -= ny * overlap;
            b.x += nx * overlap; b.y += ny * overlap;

            // Colisión elástica (masas iguales, sobre el eje normal)
            const rvx = b.vx - a.vx, rvy = b.vy - a.vy;
            const vn = rvx * nx + rvy * ny; // velocidad relativa en la normal
            if (vn < 0) {{
              const impulse = -vn;
              a.vx -= nx * impulse; a.vy -= ny * impulse;
              b.vx += nx * impulse; b.vy += ny * impulse;
            }}

            // Regla de vida: resta 1 a la de menor vida (o aleatorio si empatan)
            if (a.life === b.life) {{
              (Math.random() < 0.5 ? a : b).life--;
            }} else if (a.life > b.life) {{
              b.life--;
            }} else {{
              a.life--;
            }}
          }}
        }}
      }}
    }}
  }}
}}

function drawAll(dt) {{
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let i = 0; i < balls.length; i++) {{
    balls[i].update(dt);
    balls[i].draw();
  }}
}}

function step(ts) {{
  if (!lastTs) lastTs = ts;
  const dt = Math.min(32, ts - lastTs) / 16.6667; // dt ~ 1 a 2 para estabilizar
  lastTs = ts;

  handleCollisions();
  balls = balls.filter(b => b.life > 0);
  scaleBalls();
  drawAll(dt);

  aliveEl.textContent = String(balls.length);

  if (balls.length === 1) {{
    winnerEl.textContent = "🎉 Ganador: " + balls[0].follower.name;
    running = false;
    raf && cancelAnimationFrame(raf);
    raf = null;
    return;
  }}

  if (running) raf = requestAnimationFrame(step);
}}

function start() {{
  if (running) return;
  winnerEl.textContent = "";
  running = true;
  lastTs = null;
  raf = requestAnimationFrame(step);
}}

function pause() {{
  running = false;
  if (raf) cancelAnimationFrame(raf);
  raf = null;
}}

function reset() {{
  pause();
  balls = followers.map((f, i) => new Ball(f, i)); // MISMOS jugadores de esta sesión
  scaleBalls();
  aliveEl.textContent = String(balls.length);
  winnerEl.textContent = "";
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawAll(1);
}}

document.getElementById("startBtn").addEventListener("click", start);
document.getElementById("pauseBtn").addEventListener("click", pause);
document.getElementById("resetBtn").addEventListener("click", reset);

// Dibujo inicial y arranque
scaleBalls();
aliveEl.textContent = String(balls.length);
drawAll(1);

// Arranca automáticamente (puedes comentar esta línea si prefieres manual)
start();

// Redimensionar manteniendo posiciones dentro del canvas
window.addEventListener("resize", () => {{
  const oldW = canvas.width, oldH = canvas.height;
  sizeCanvas();
  const sx = canvas.width / oldW;
  const sy = canvas.height / oldH;
  balls.forEach(b => {{
    b.x = Math.max(b.radius, Math.min(canvas.width  - b.radius, b.x * 
    b.y = Math.max(b.radius, Math.min(canvas.height - b.radius, b.y * sy));
  }});
}});
</script>
"""

st.components.v1.html(html, height=720)
