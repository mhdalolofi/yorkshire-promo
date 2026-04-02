import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")
st.title("📍 WYCA HEWY Outreach")
st.markdown("High-Speed Map Engine enabled for 250+ locations.")

# --- DATA LOADING ---
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            data = df.iloc[:, [0, 1]].dropna()
            data.columns = ['pc', 'name']
            return data.to_dict('records')
        return []
    except:
        return []

# --- FAST GEOCODING ENGINE ---
@st.cache_data(ttl=86400) # Cache coordinates for 24 hours
def get_coords(pc):
    geo = Nominatim(user_agent="wyca_ultra_fast_v9")
    try:
        res = geo.geocode(f"{pc}, West Yorkshire, UK", timeout=3)
        if res: return (res.latitude, res.longitude)
    except: return None
    return None

# --- PARALLEL PROCESSING ---
def fetch_all_coords(locations):
    with ThreadPoolExecutor(max_workers=10) as executor:
        # This runs 10 searches at the same time
        results = list(executor.map(lambda x: get_coords(x['pc']), locations))
    return results

# --- MAIN LOGIC ---
locations = load_data()

with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(locations)} Sites in Database")
    if st.button("🔄 Clear Cache & Fast Sync"):
        st.cache_data.clear()
        st.rerun()

# Processing markers
m = folium.Map(location=[53.7997, -1.5492], zoom_start=11)

if locations:
    # Get all coordinates using the fast engine
    with st.spinner('🚀 Optimizing map markers for 268+ locations...'):
        all_coords = fetch_all_coords(locations)
    
    for i, row in enumerate(locations):
        coords = all_coords[i]
        if coords:
            folium.Marker(
                location=coords,
                popup=f"<b>{row['name']}</b><br>{row['pc']}",
                tooltip=row['name'],
                icon=folium.Icon(color='green', icon='map-pin', prefix='fa')
            ).add_to(m)

# Display
st_folium(m, width="100%", height=600)
