
import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import math
import requests
import random
import pandas as pd

st.set_page_config(page_title="Simulare Derivă SAR", layout="wide")
st.title("🌊 Simulare Derivă SAR cu Particule Multiple (Marea Neagră)")

# --- Input de la utilizator ---
st.sidebar.header("⚙️ Parametri Simulare")
lat = st.sidebar.number_input("Latitudine inițială", value=44.17, format="%.5f")
lon = st.sidebar.number_input("Longitudine inițială", value=28.65, format="%.5f")
duration = st.sidebar.slider("Durata simulării (ore)", 1, 24, 12)
particles = st.sidebar.slider("Număr particule", 10, 300, 100)
alpha = st.sidebar.slider("Coeficient derivă vânt (%)", 0.0, 10.0, 3.0) / 100.0
curent_simplu = True  # Folosim curenți constanți simpli pentru început
v_curent = 0.1  # m/s
bearing_curent = 45  # NE

# Obține vânt orar real din API Open-Meteo
@st.cache_data
def get_wind_forecast(lat, lon, hours):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=windspeed_10m,winddirection_10m&forecast_days=1&timezone=auto"
    r = requests.get(url)
    data = r.json()
    speeds = data['hourly']['windspeed_10m'][:hours]
    directions = data['hourly']['winddirection_10m'][:hours]
    return list(zip(speeds, directions))

wind_data = get_wind_forecast(lat, lon, duration)

# --- Simulare Particule ---
results = []
m = folium.Map(location=(lat, lon), zoom_start=9)

for i in range(particles):
    p_lat, p_lon = lat, lon
    path = [(p_lat, p_lon)]

    # Variabilitate aleatorie pe particulă
    random_offset = random.uniform(-0.05, 0.05)

    for hour in range(duration):
        v_v, dir_v = wind_data[hour]
        dir_rad = math.radians(dir_v + random_offset * 10)

        v_wind_x = v_v * math.sin(dir_rad)
        v_wind_y = v_v * math.cos(dir_rad)

        v_total_x = (v_curent * math.sin(math.radians(bearing_curent))) + (alpha * v_wind_x)
        v_total_y = (v_curent * math.cos(math.radians(bearing_curent))) + (alpha * v_wind_y)

        dx = v_total_x * 3600
        dy = v_total_y * 3600
        dist_m = math.sqrt(dx**2 + dy**2)
        bearing = math.degrees(math.atan2(dx, dy))

        new_point = geodesic(meters=dist_m).destination(point=(p_lat, p_lon), bearing=bearing)
        p_lat, p_lon = new_point.latitude, new_point.longitude
        path.append((p_lat, p_lon))

    folium.PolyLine(path, color="blue", weight=1, opacity=0.6).add_to(m)
    results.append({"Particulă": i+1, "Lat_final": p_lat, "Lon_final": p_lon})

# --- Afișare rezultate ---
folium.Marker((lat, lon), tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
folium_static(m)

df = pd.DataFrame(results)
st.dataframe(df)

# Export
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descarcă rezultate CSV", data=csv, file_name="rezultate_derive.csv")

st.caption("Date de vânt: Open-Meteo.org | Curenți: model simplificat (NE, 0.1 m/s)")
