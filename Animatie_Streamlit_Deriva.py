import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from geopy.distance import geodesic
import math
import random
import numpy as np
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Animatie Derivă SAR", layout="wide")
st.title("🌊 Animație Derivă SAR cu Particule Multiple")

# Inputuri
lat = st.sidebar.number_input("Latitudine inițială", value=44.17, format="%.5f")
lon = st.sidebar.number_input("Longitudine inițială", value=28.65, format="%.5f")
duration = st.sidebar.slider("Durata (ore)", 1, 24, 12)
particles = st.sidebar.slider("Număr particule", 10, 300, 100)
alpha = st.sidebar.slider("Coeficient derivă vânt (%)", 0.0, 10.0, 3.0) / 100.0

# Simulare simplificată
v_curent = 0.1
bearing_curent = 45
wind_speed = 5
wind_direction = 90

if st.button("🎬 Generează animația"):

    paths = [[(lat, lon)] for _ in range(particles)]

    for hour in range(duration):
        for p in paths:
            lat_i, lon_i = p[-1]
            dir_rad = math.radians(wind_direction + random.uniform(-5, 5))

            v_wind_x = wind_speed * math.sin(dir_rad)
            v_wind_y = wind_speed * math.cos(dir_rad)

            v_total_x = (v_curent * math.sin(math.radians(bearing_curent))) + (alpha * v_wind_x)
            v_total_y = (v_curent * math.cos(math.radians(bearing_curent))) + (alpha * v_wind_y)

            dx = v_total_x * 3600
            dy = v_total_y * 3600
            dist_m = math.sqrt(dx**2 + dy**2)
            bearing = math.degrees(math.atan2(dx, dy))

            new_point = geodesic(meters=dist_m).destination(point=(lat_i, lon_i), bearing=bearing)
            p.append((new_point.latitude, new_point.longitude))

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.set_xlim(lon - 0.5, lon + 0.5)
    ax.set_ylim(lat - 0.5, lat + 0.5)
    ax.set_title("Derivă SAR – Simulare cu Particule")
    scat = ax.scatter([], [], s=10, color='blue')

    def init():
        scat.set_offsets(np.empty((0, 2)))
        return scat,

    def animate(i):
        frame = [p[i] if i < len(p) else p[-1] for p in paths]
        scat.set_offsets(np.array(frame))
        return scat,

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=duration+1, interval=500, blit=True)

    gif_io = BytesIO()
   ani.save(gif_io, writer=animation.PillowWriter(fps=2))

    gif_io.seek(0)

    st.image(Image.open(gif_io), caption="Animație deriva particule", use_column_width=True)
    st.download_button("📥 Descarcă animația GIF", gif_io, file_name="deriva_animatie.gif", mime="image/gif")
