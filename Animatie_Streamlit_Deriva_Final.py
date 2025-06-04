import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import io

# Titlu
st.title("Animație Derivă SAR cu Particule Multiple")

# Parametri ajustabili
lat_start = st.number_input("Latitudine de start", value=44.8)
lon_start = st.number_input("Longitudine de start", value=29.6)
num_particles = st.slider("Număr particule", 10, 200, 100)
sim_duration = st.slider("Durată simulare (ore)", 1, 48, 24)
coef_deriva = st.slider("Coeficient de derivă (%)", 1.0, 10.0, 3.0)

# Simulare simplificată a traiectoriei (aleatoare controlată)
np.random.seed(0)
lat_paths = [lat_start + np.cumsum(np.random.randn(sim_duration) * 0.001) for _ in range(num_particles)]
lon_paths = [lon_start + np.cumsum(np.random.randn(sim_duration) * 0.001) for _ in range(num_particles)]

# Hartă cu traiectorii
st.subheader("Hartă traiectorii particule")
m = folium.Map(location=[lat_start, lon_start], zoom_start=9)
folium.Marker(location=[lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)

# Adaugă traiectorii
for lat, lon in zip(lat_paths, lon_paths):
    points = list(zip(lat, lon))
    folium.PolyLine(points, color="blue", weight=1, opacity=0.6).add_to(m)

st_data = st_folium(m, width=700, height=500)

# Animație (Matplotlib)
st.subheader("Animație derulare particule")

fig, ax = plt.subplots()
ax.set_xlim(min(lon_start - 0.1, np.min(lon_paths)), max(lon_start + 0.1, np.max(lon_paths)))
ax.set_ylim(min(lat_start - 0.1, np.min(lat_paths)), max(lat_start + 0.1, np.max(lat_paths)))
scat = ax.scatter([], [], s=10, c="blue")

def init():
    scat.set_offsets([])
    return scat,

def update(frame):
    coords = np.array([[lon_paths[i][frame], lat_paths[i][frame]] for i in range(num_particles)])
    scat.set_offsets(coords)
    return scat,

ani = animation.FuncAnimation(fig, update, frames=sim_duration, init_func=init, blit=True)

buf = io.BytesIO()
ani.save(buf, format="gif", writer="pillow", fps=3)
st.image(buf.getvalue(), format="gif", caption="Simulare animată a derivei")
