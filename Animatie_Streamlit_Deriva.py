import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from io import BytesIO
import base64

st.set_page_config(page_title="Animație Derivă SAR", layout="wide")

st.title("🌊 Animație Derivă SAR cu Particule Multiple")

st.sidebar.header("Parametri simulare")
num_particles = st.sidebar.slider("Număr particule", 10, 300, 100)
durata_ore = st.sidebar.slider("Durata simulării (ore)", 1, 48, 12)
viteza = st.sidebar.slider("Viteza derivă (km/h)", 0.5, 5.0, 1.5, step=0.1)
directie = st.sidebar.slider("Direcție derivă (grade - 0=N, 90=E)", 0, 360, 135)

btn = st.button("🎬 Generează animația")

if btn:
    st.info("Se generează animația...")

    lat_start, lon_start = 44.15, 28.65
    directie_rad = np.deg2rad(directie)

    positions = np.zeros((num_particles, durata_ore + 1, 2))
    positions[:, 0, 0] = lat_start
    positions[:, 0, 1] = lon_start

    for t in range(1, durata_ore + 1):
        delta_lat = (viteza / 111) * np.cos(directie_rad)
        delta_lon = (viteza / (111 * np.cos(np.deg2rad(lat_start)))) * np.sin(directie_rad)

        zgomot = np.random.normal(0, 0.002, (num_particles, 2))
        positions[:, t, 0] = positions[:, t - 1, 0] + delta_lat + zgomot[:, 0]
        positions[:, t, 1] = positions[:, t - 1, 1] + delta_lon + zgomot[:, 1]

    fig, ax = plt.subplots()
    scat = ax.scatter([], [], s=10)
    ax.set_xlim(np.min(positions[:, :, 1]) - 0.01, np.max(positions[:, :, 1]) + 0.01)
    ax.set_ylim(np.min(positions[:, :, 0]) - 0.01, np.max(positions[:, :, 0]) + 0.01)
    ax.set_xlabel("Longitudine")
    ax.set_ylabel("Latitudine")

    def update(frame):
        scat.set_offsets(positions[:, frame, ::-1])
        return scat,

    ani = animation.FuncAnimation(fig, update, frames=durata_ore + 1, interval=500, blit=True)

    gif_io = BytesIO()
    ani.save(gif_io, writer=animation.PillowWriter(fps=2))
    gif_io.seek(0)
    gif_data = base64.b64encode(gif_io.read()).decode("utf-8")

    st.markdown("### Rezultat:")
    st.image(f"data:image/gif;base64,{gif_data}")
