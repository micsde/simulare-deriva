
import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
from datetime import datetime
import random

st.set_page_config(page_title="Simulare Derivă SAR", layout="wide")

st.title("🌊 Simulare Derivă Maritimă (SAR) – România / Marea Neagră")

st.markdown("Această aplicație simplificată estimează deriva unui obiect în derivă pe mare pe baza direcției vântului și a poziției inițiale. Datele reale pot fi extinse.")

# Poziție de start
lat = st.number_input("Latitudine inițială", value=44.15, format="%.6f")
lon = st.number_input("Longitudine inițială", value=28.65, format="%.6f")

# Direcție vânt (simplificat)
wind_speed = st.slider("Viteză vânt (m/s)", 0.0, 20.0, 5.0)
wind_direction = st.slider("Direcție vânt (grade – 0=N, 90=E)", 0, 360, 90)

duration_hours = st.slider("Durată simulare (ore)", 1, 24, 6)

# Coeficient leeway (proporția din vânt preluată de obiect)
alpha = st.slider("Coeficient de derivă α (%)", 0.0, 10.0, 3.0) / 100.0

# Calcule simple (ignorând curenți și valuri pentru acest demo)
distance_km = wind_speed * alpha * 3.6 * duration_hours
direction_rad = wind_direction * 3.14159 / 180

# Conversie simplificată lat/lon (funcționează pentru distanțe mici)
delta_lat = (distance_km / 111) * math.cos(direction_rad)
delta_lon = (distance_km / (111 * math.cos(lat * 3.14159 / 180))) * math.sin(direction_rad)

final_lat = lat + delta_lat
final_lon = lon + delta_lon

m = folium.Map(location=[lat, lon], zoom_start=7)
folium.Marker([lat, lon], tooltip="Poziție Inițială", icon=folium.Icon(color="blue")).add_to(m)
folium.Marker([final_lat, final_lon], tooltip="Poziție Estimată", icon=folium.Icon(color="red")).add_to(m)
folium.PolyLine(locations=[[lat, lon], [final_lat, final_lon]], color="green").add_to(m)

st.markdown(f"**Distanță estimată derivă:** `{distance_km:.2f}` km")
folium_static(m)

st.caption("Simulare simplificată – fără date reale de curent sau valuri. Versiune demonstrativă.")
