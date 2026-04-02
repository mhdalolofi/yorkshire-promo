import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- CONNECTION SETTINGS ---
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- PAGE CONFIG ---
st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")

# --- HEADER ---
st.title("📍 WYCA HEWY Outreach")
st.markdown("Precision tracking with High-Speed Caching.")

# --- FAST DATA LOADING ---
@st.cache_data(ttl=10) # Refresh data from sheet every 10 seconds
def load_sheet_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            # Get unique postcodes from column A, clean them and uppercase
            raw_pcs = df.iloc[:, 0].dropna().unique().tolist()
            return [str(x).strip().upper() for x in raw_pcs if len(str(x)) > 4]
        return []
    except:
        return []

# --- SMART GEOCODING (The Speed Secret) ---
@st.cache_data(ttl=3600) # Keep location coordinates in memory for 1 hour
def get_location_coordinates(pc):
    geo = Nominatim(user_agent="wyca_fast_v7_final")
    try:
        res = geo.geocode(f"{pc}, West Yorkshire, UK", timeout=5)
        if res:
            return (res.latitude, res.longitude)
    except:
        return None
    return None

# --- MAIN APP LOGIC ---
postcodes = load_sheet_data()

with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(postcodes)} Locations Processed")
    if st.button("🔄 Clear Cache & Sync"):
        st.cache_data.clear()
        st.rerun()
    st.write("---")
    st.info("The map is now cached. Repeated visits will be instant.")

# Initialize Map
m = folium.Map(location=[53.7997, -1.5492], zoom_start=11, tiles="OpenStreetMap")

if postcodes:
    for pc in postcodes:
        coords = get_location_coordinates(pc)
        if coords:
            folium.Marker(
                location=coords,
                popup=f"Site: {pc}",
                icon=folium.Icon(color='green', icon='map-pin', prefix='fa')
            ).add_to(m)

# Display Map
st_folium(m, width="100%", height=600)
