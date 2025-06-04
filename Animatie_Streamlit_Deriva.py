
import streamlit as st
import numpy as np
import folium
from folium import Map, Marker
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from io import BytesIO
import base64

st.set_page_config(layout="wide")
st.title("Simulare Derivă SAR - Particule Multiple + Animație")

# Setări introduse de utilizator
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitudine inițială", value=44.165, format="%.6f")
    lon = st.number_input("Longitudine inițială", value=28.650, format="%.6f")
with col2:
    num_particles = st.slider("Număr de particule", 10, 200, 50)
    duration_h = st.slider("Durată simulare (ore)", 1, 48, 24)

steps = duration_h  # fiecare oră = un pas

# Simulare derivă simplificată
np.random.seed(42)
traiectorii = []
for _ in range(num_particles):
    x = [lon]
    y = [lat]
    for _ in range(steps):
        x.append(x[-1] + np.random.normal(scale=0.01))
        y.append(y[-1] + np.random.normal(scale=0.01))
    traiectorii.append((x, y))

# Harta
m = Map(location=[lat, lon], zoom_start=10)
Marker([lat, lon], tooltip="Start").add_to(m)
st.markdown("### Harta cu punctul de start")
st_folium(m, width=700)

# Animatie
st.markdown("### Animație derulare particule")
fig, ax = plt.subplots()
ax.set_xlim(lon - 0.5, lon + 0.5)
ax.set_ylim(lat - 0.5, lat + 0.5)
lines = [ax.plot([], [], lw=1)[0] for _ in range(num_particles)]

def init():
    for line in lines:
        line.set_data([], [])
    return lines

def update(frame):
    for i, line in enumerate(lines):
        line.set_data(traiectorii[i][0][:frame], traiectorii[i][1][:frame])
    return lines

ani = animation.FuncAnimation(fig, update, frames=steps, init_func=init, blit=True)

buf = BytesIO()
ani.save(buf, format="gif", writer='pillow', fps=3)
gif_bytes = buf.getvalue()
gif_b64 = base64.b64encode(gif_bytes).decode("utf-8")
st.markdown(f'<img src="data:image/gif;base64,{gif_b64}" width="700"/>', unsafe_allow_html=True)
