import streamlit as st
import random
import json

st.set_page_config(page_title="Sorteo Automático 1111", layout="centered")
st.title("🎮 Sorteo Automático de Seguidores (1111 jugadores)")

# -----------------------------
# Generador de nombres estilo Instagram
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
# Crear 1111 seguidores
# -----------------------------
followers_py = []
used = set()
while len(followers_py) < 1111:
    n = ig_name()
    if n in used:
        continue
    used.add(n)
    img_id = random.randint(1, 70)
    followers_py.append({"name": n, "avatar": f"https://i.pravatar.cc/150?img={img_id}"})

followers_json = json.dumps(followers_py)

# -----------------------------
# HTML + JS optimizado para 1111 jugadores
# -----------------------------
html = f"""
<div style="text-align:center;">
  <div style="margin:10px 0;">
    <button id="startBtn">▶️ Iniciar</button>
    <button id="pauseBtn">⏸️ Pausar</button>
    <button id="resetBtn">🔄 Reiniciar</button>
  </div>
