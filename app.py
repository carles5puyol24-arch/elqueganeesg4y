import streamlit as st
import random
import string

st.set_page_config(page_title="Sorteo Automático", layout="centered")

st.title("🎮 Sorteo Automático de Seguidores (300 jugadores)")

# ==========================
# Generador de nombres estilo Instagram
# ==========================
def random_instagram_name():
    nombres = ["andrea", "maria", "juan", "carlos", "sofia", "laura", "alejandro", "martin", "paula", "natalia", "sergio", "javier", "clara", "beatriz", "diego", "lucia", "ana", "pablo", "antonio", "david"]
    sufijos = ["_", ".", "x", "xx", "97", "14", "22", "gomez", "garcia", "99", "lol", "ok", "real", "oficial"]
    
    base = random.choice(nombres)
    extra = random.choice(sufijos)
    
    # a veces repetir letras (ej: "mariaaa")
    if random.random() < 0.3:
        base = base[:-1] + base[-1] * random.randint(2,4)
    
    # unir con guion bajo o seguido
    if random.random() < 0.5:
        return base + "_" + extra
    else:
        return base + extra

# ==========================
# Generar 300 jugadores
# ==========================
followers = []
for i in range(300):
    followers.append({
        "name": random_instagram_name(),
        "avatar": f"https://i.pravatar.cc/100?img={(i % 70) + 1}"  # rota entre 70 avatares
    })

# ==========================
# Botones de control
# ==========================
col1, col2, col3 = st.columns(3)
with col1:
    st.button("▶️ Iniciar", key="start")
with col2:
    st.button("⏸️ Pausar", key="pause")
with col3:
    st.button("🔄 Reiniciar", key="reset")

# ==========================
# Código del juego en JS
# ==========================
game_code = f"""
<canvas id="gameCanvas" width="800" height="600" style="border:2px solid white; background:#111;"></canvas>
<div id="counter" style="color:white; font-size:18px; margin-top:10px;"></div>
<div id="winner" style="color:yellow; font-size:22px; margin-top:20px;"></div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const followers = {followers};

class Ball {{
  constructor(follower) {{
    this.follower = follower;
    this.radius = 8;
    this.x = Math.random() * (canvas.width - this.radius * 2) + this.radius;
    this.y = Math.random() * (canvas.height - this.radius * 2) + this.radius;
    const speed = 2.2;
    this.vx = (Math.random() - 0.5) * speed * 2;
    this.vy = (Math.random() - 0.5) * speed * 2;
    this.life = 10;
    this.image = new Image();
    this.image.src = follower.avatar;
  }}
  draw() {{
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2);
    ctx.fillStyle = "white";
    ctx.fill();
    ctx.closePath();
    ctx.save();
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius-1, 0, Math.PI*2);
    ctx.clip();
    ctx.drawImage(this.image, this.x-this.radius, this.y-this.radius, this.radius*2, this.radius*2);
    ctx.restore();
    ctx.fillStyle = "red";
    ctx.font = "10px Arial";
    ctx.fillText(this.life, this.x-4, this.y+3);
  }}
  update() {{
    this.x += this.vx;
    this.y += this.vy;
    if (this.x - this.radius < 0 || this.x + this.radius > canvas.width) this.vx *= -1;
    if (this.y - this.radius < 0 || this.y + this.radius > canvas.height) this.vy *= -1;
  }}
}}

let balls = followers.map(f => new Ball(f));
let running = true;

function gameLoop() {{
  ctx.clearRect(0,0,canvas.width,canvas.height);

  for (let i=0; i<balls.length; i++) {{
    for (let j=i+1; j<balls.length; j++) {{
      let a=balls[i], b=balls[j];
      let dx=b.x-a.x, dy=b.y-a.y;
      let dist=Math.sqrt(dx*dx+dy*dy);
      if (dist < a.radius+b.radius) {{
        [a.vx, b.vx] = [b.vx, a.vx];
        [a.vy, b.vy] = [b.vy, a.vy];
        if (a.life===b.life) (Math.random()<0.5?a:b).life--;
        else if (a.life>b.life) b.life--; else a.life--;
      }}
    }}
  }}

  balls = balls.filter(b=>b.life>0);

  // crecimiento dinámico
  const base = 8;
  const gained = (followers.length - balls.length) * 1.8;
  const newRadius = base + gained;
  balls.forEach(b => b.radius=newRadius);

  balls.forEach(b=>{{b.update(); b.draw();}});

  document.getElementById("counter").innerHTML = "Pelotas vivas: " + balls.length;

  if (balls.length===1) {{
    document.getElementById("winner").innerHTML = "🎉 Ganador: " + balls[0].follower.name;
    return;
  }}
  if (running) requestAnimationFrame(gameLoop);
}}

gameLoop();
</script>
"""

st.components.v1.html(game_code, height=650)
