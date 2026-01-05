import streamlit as st
import random
import folium
import requests
import polyline
from geopy.distance import geodesic
from streamlit_folium import st_folium

st.set_page_config(page_title="Emergency Response System", layout="wide")
st.title("🚨 AI-Based Accident Detection & Emergency Response")

# -------------------------------
# Helper Functions
# -------------------------------
def generate_random_location():
    lat = random.uniform(12.90, 13.15)   # Chennai region
    lon = random.uniform(80.10, 80.35)
    return lat, lon

def find_nearest(source, locations):
    return min(locations, key=lambda x: geodesic(source, x).km)

def get_osrm_route(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=polyline"
    res = requests.get(url).json()

    route = polyline.decode(res["routes"][0]["geometry"])
    distance_km = res["routes"][0]["distance"] / 1000
    duration_min = res["routes"][0]["duration"] / 60

    return route, distance_km, duration_min

# -------------------------------
# Simulated Data
# -------------------------------
ambulances = [
    (12.9716, 80.2210),
    (13.0500, 80.2500),
    (12.9900, 80.1800)
]

hospitals = [
    (13.0600, 80.2400),
    (12.9800, 80.2100),
    (13.0200, 80.3000)
]

# -------------------------------
# Accident Detection
# -------------------------------
if st.button("🚧 Detect Accident"):
    st.session_state.accident = generate_random_location()
    st.success("Accident detected successfully!")

# -------------------------------
# Show Accident Location
# -------------------------------
if "accident" in st.session_state:
    acc = st.session_state.accident

    st.write("📍 **Accident Location**")
    m = folium.Map(location=acc, zoom_start=13)
    folium.Marker(acc, popup="Accident", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, width=700, height=400)

# -------------------------------
# Ambulance Assignment
# -------------------------------
if "accident" in st.session_state:
    if st.button("🚑 Check Ambulance Availability"):
        st.session_state.ambulance = find_nearest(st.session_state.accident, ambulances)
        st.session_state.hospital = find_nearest(st.session_state.accident, hospitals)
        st.success("Nearest ambulance assigned!")

# -------------------------------
# Route + ETA Visualization
# -------------------------------
if "ambulance" in st.session_state:
    acc = st.session_state.accident
    amb = st.session_state.ambulance
    hosp = st.session_state.hospital

    route1, dist1, time1 = get_osrm_route(amb, acc)
    route2, dist2, time2 = get_osrm_route(acc, hosp)

    m = folium.Map(location=acc, zoom_start=12)

    folium.Marker(amb, popup="Ambulance", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(acc, popup="Accident", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(hosp, popup="Hospital", icon=folium.Icon(color="green")).add_to(m)

    folium.PolyLine(route1, color="blue", weight=5, tooltip="Ambulance → Accident").add_to(m)
    folium.PolyLine(route2, color="green", weight=5, tooltip="Accident → Hospital").add_to(m)

    st.write("🗺️ **Road Route & ETA**")
    st_folium(m, width=900, height=450)

    st.markdown("### ⏱️ Time & Distance")
    st.write(f"Distance: **{dist1:.2f} km**, **{time1:.1f} mins**")
    st.write(f"Distance: **{dist2:.2f} km**, **{time2:.1f} mins**")
