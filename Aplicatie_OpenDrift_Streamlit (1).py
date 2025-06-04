import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import math
from datetime import datetime, timedelta

st.set_page_config(page_title="Derivă realistă SAR", layout="wide")
st.title("🌊 Simulare Derivă Maritimă (Realistă) – Marea Neagră")

# Input de la utilizator
lat = st.number_input("Latitudine inițială", value=44.17, format="%.5f")
lon = st.number_input("Longitudine inițială", value=28.65, format="%.5f")
duration_hours = st.slider("Durată simulare (ore)", 1, 24, 6)
alpha = st.slider("Coeficient de derivă α (%)", 0.0, 10.0, 3.0) / 100.0
v_curent = 0.1  # m/s simplificat
bearing_curent = 45  # N-E

# Obține date reale de vânt pe ore
def get_wind_hourly(lat, lon, hours):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=windspeed_10m,winddirection_10m&forecast_days=1&timezone=auto"
    )
    r = requests.get(url)
    data = r.json()
    speeds = data['hourly']['windspeed_10m'][:hours]
    directions = data['hourly']['winddirection_10m'][:hours]
    return list(zip(speeds, directions))

# Simulare derivă pas cu pas
positions = [(lat, lon)]
wind_data = get_wind_hourly(lat, lon, duration_hours)

for hour in range(duration_hours):
    wind_speed, wind_dir = wind_data[hour]
    angle_rad = math.radians(wind_dir)
    v_wind_x = wind_speed * math.sin(angle_rad)
    v_wind_y = wind_speed * math.cos(angle_rad)

    # Derivă totală
    v_total_x = v_curent * math.sin(math.radians(bearing_curent)) + alpha * v_wind_x
    v_total_y = v_curent * math.cos(math.radians(bearing_curent)) + alpha * v_wind_y

    # Timp: 1 oră = 3600s, distanță = v * t
    dx = v_total_x * 3600
    dy = v_total_y * 3600
    dist_m = math.sqrt(dx**2 + dy**2)
    bearing = math.degrees(math.atan2(dx, dy))

    # Noua poziție
    last_point = positions[-1]
    new_point = geodesic(meters=dist_m).destination(point=last_point, bearing=bearing)
    positions.append((new_point.latitude, new_point.longitude))

# Hartă
m = folium.Map(location=positions[0], zoom_start=8)
folium.Marker(positions[0], tooltip="Start", icon=folium.Icon(color="blue")).add_to(m)
folium.Marker(positions[-1], tooltip="Final", icon=folium.Icon(color="red")).add_to(m)
folium.PolyLine(positions, color="green", weight=2.5, tooltip="Traiectorie derivă").add_to(m)

st.markdown(f"**Poziție finală estimată:** {positions[-1][0]:.4f}, {positions[-1][1]:.4f}")
folium_static(m)

st.caption("Simulare realistă cu deriva orară calculată din date meteo. Fără integrare curenți reali (demo).")
