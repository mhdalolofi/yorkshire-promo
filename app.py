import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- CONNECTION ---
# Your Sheet ID: 102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- PAGE CONFIG ---
st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")

# --- HEADER ---
st.title("📍 WYCA HEWY Outreach")
st.subheader("West Yorkshire Outreach Campaign Tracking")

# Cleaning Function
def fix_pc(pc):
    if pd.isna(pc): return None
    p = str(pc).replace(" ", "").upper()
    if len(p) >= 5:
        return p[:-3] + " " + p[-3:]
    return p

# Data Fetching (Fast Refresh)
@st.cache_data(ttl=2) 
def load_sheet():
    try:
        # Use a fresh request to avoid old data
        data = pd.read_csv(SHEET_URL)
        if not data.empty:
            # Force take column 0
            raw = data.iloc[:, 0].dropna().tolist()
            return [fix_pc(x) for x in raw if x]
        return []
    except:
        return []

# Sidebar
postcodes = load_sheet()
with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(postcodes)} Sites Found")
    if st.button("🔄 REFRESH DATA"):
        st.cache_data.clear()
        st.rerun()

# Map Setup
m = folium.Map(location=[53.8, -1.5], zoom_start=11)
geo = Nominatim(user_agent="wyca_final_unique_id_99")

for p in postcodes:
    try:
        loc = geo.geocode(f"{p}, West Yorkshire, UK", timeout=10)
        if loc:
            folium.Marker(
                location=[loc.latitude, loc.longitude],
                popup=f"Site: {p}",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
    except:
        continue

st_folium(m, width="100%", height=600)
