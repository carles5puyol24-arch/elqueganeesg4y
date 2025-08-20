import streamlit as st

st.set_page_config(page_title="Sorteo Automático", layout="centered")
st.title("🎮 Sorteo Automático de Seguidores")

html = """
<div style="text-align:center;">
  <div style="margin:10px 0;">
    <button id="startBtn">▶️ Iniciar</button>
    <button id="pauseBtn">⏸️ Pausar</button>
    <button id="resetBtn">🔄 Reiniciar</button>
  </div>
  <div style="margin:6px 0; color:white;">Pelotas vivas: <span id="aliveCount"></span></div>
  <canvas id="gameCanvas" style="border:2px solid white; background:#222; max-width:95vw;"></canvas>
  <div id="winner" style="color:white; font-size:20px; margin-top:16px;"></div>
</div>

<script>
// Ajuste de tamaño del canvas según pantalla
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
function sizeCanvas() {
  const maxW = Math.min(window.innerWidth * 0.95, 900);
  canvas.width  = Math.floor(maxW);
  canvas.height = Math.floor(Math.max(360, Math.min(560, maxW * 0.6)));
}
sizeCanvas();

const followers = [
  // 👇 Cambia esta lista por tus seguidores (nombre + URL de avatar)
  { name: "Ana",    avatar: "https://i.pravatar.cc/100?img=1" },
  { name: "Luis",   avatar: "https://i.pravatar.cc/100?img=2" },
  { name: "Marta",  avatar: "https://i.pravatar.cc/100?img=3" },
  { name: "Carlos", avatar: "https://i.pravatar.cc/100?img=4" },
  { name: "Sara",   avatar: "https://i.pravatar.cc/100?img=5" },
  { name: "Leo",    avatar: "https://i.pravatar.cc/100?img=6" }
];

class Ball {
  constructor(follower) {
    this.follower = follower;
    this.radius = 20;
    this.x = Math.random() * (canvas.width - this.radius * 2) + this.radius;
    this.y = Math.random() * (canvas.height - this.radius * 2) + this.radius;
    const speed = 3.2;
    const angle = Math.random() * Math.PI * 2;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.life = 10;
    this.image = new Image();
    this.image.src = follower.avatar;
  }

  draw() {
    // Círculo base
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();

    // Avatar recortado
    ctx.save();
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius - 2, 0, Math.PI * 2);
    ctx.clip();
    ctx.drawImage(this.image, this.x - this.radius, this.y - this.radius, this.radius * 2, this.radius * 2);
    ctx.restore();

    // Nombre
    ctx.fillStyle = "yellow";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    ctx.fillText(this.follower.name, this.x, this.y - this.radius - 6);

    // Vida
    ctx.fillStyle = "red";
    ctx.font = "bold 12px Arial";
    ctx.fillText(this.life, this.x, this.y + 4);
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    // Rebote con paredes
    if (this.x - this.radius < 0) { this.x = this.radius; this.vx *= -1; }
    if (this.x + this.radius > canvas.width) { this.x = canvas.width - this.radius; this.vx *= -1; }
    if (this.y - this.radius < 0) { this.y = this.radius; this.vy *= -1; }
    if (this.y + this.radius > canvas.height) { this.y = canvas.height - this.radius; this.vy *= -1; }
  }
}

let balls = followers.map(f => new Ball(f));
let running = false;
let animId = null;

const aliveCountEl = document.getElementById("aliveCount");
const winnerEl = document.getElementById("winner");
function updateAliveCounter() { aliveCountEl.textContent = String(balls.length); }
updateAliveCounter();

function handleCollisions() {
  for (let i = 0; i < balls.length; i++) {
    for (let j = i + 1; j < balls.length; j++) {
      const a = balls[i], b = balls[j];
      const dx = b.x - a.x, dy = b.y - a.y;
      const dist = Math.hypot(dx, dy);
      const minDist = a.radius + b.radius;

      if (dist < minDist) {
        // Rebote elástico (simplificado, intercambio de velocidades)
        [a.vx, b.vx] = [b.vx, a.vx];
        [a.vy, b.vy] = [b.vy, a.vy];

        // Separación mínima para evitar "pegado"
        const overlap = (minDist - dist) / 2;
        const nx = dx / (dist || 1), ny = dy / (dist || 1);
        a.x -= nx * overlap; a.y -= ny * overlap;
        b.x += nx * overlap; b.y += ny * overlap;

        // Pérdida de vida (regla)
        if (a.life === b.life) {
          (Math.random() < 0.5 ? a : b).life--;
        } else if (a.life > b.life) {
          b.life--;
        } else {
          a.life--;
        }
      }
    }
  }
}

function scaleBalls() {
  const base = 20;
  const gained = (followers.length - balls.length) * 5; // +5 px por baja
  const newRadius = base + gained;
  balls.forEach(b => b.radius = newRadius);
}

function drawAll() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  balls.forEach(b => { b.update(); b.draw(); });
}

function tick() {
  handleCollisions();
  balls = balls.filter(b => b.life > 0);
  scaleBalls();
  drawAll();
  updateAliveCounter();

  if (balls.length === 1) {
    winnerEl.textContent = "🎉 Ganador: " + balls[0].follower.name;
    running = false;
    animId && cancelAnimationFrame(animId);
    animId = null;
    return;
  }

  if (running) {
    animId = requestAnimationFrame(tick);
  }
}

// Controles
document.getElementById("startBtn").addEventListener("click", () => {
  if (!running) {
    winnerEl.textContent = "";
    running = true;
    animId = requestAnimationFrame(tick);
  }
});
document.getElementById("pauseBtn").addEventListener("click", () => {
  running = false;
  animId && cancelAnimationFrame(animId);
  animId = null;
});
document.getElementById("resetBtn").addEventListener("click", () => {
  running = false;
  animId && cancelAnimationFrame(animId);
  animId = null;
  balls = followers.map(f => new Ball(f));
  winnerEl.textContent = "";
  updateAliveCounter();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawAll();
});

// Dibujo inicial y ajuste en rotación de pantalla
drawAll();
window.addEventListener("resize", () => {
  const oldW = canvas.width, oldH = canvas.height;
  const snap = balls.map(b => ({ name: b.follower.name, life: b.life }));
  sizeCanvas();
  // Recolocar dentro de nuevo tamaño
  balls.forEach(b => {
    b.x = Math.max(b.radius, Math.min(canvas.width - b.radius, b.x * (canvas.width / oldW)));
    b.y = Math.max(b.radius, Math.min(canvas.height - b.radius, b.y * (canvas.height / oldH)));
  });
});
</script>
"""

st.components.v1.html(html, height=620)
