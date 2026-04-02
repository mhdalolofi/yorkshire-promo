import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="West Yorkshire Promotion Tracker", layout="wide")
st.title("📍 Precision Promotion Map")

def clean_postcode(pc):
    if pd.isna(pc): return None
    clean_pc = "".join(filter(str.isalnum, str(pc))).upper()
    if len(clean_pc) > 3:
        return clean_pc[:-3] + " " + clean_pc[-3:]
    return clean_pc

@st.cache_data(ttl=10)
def get_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            first_col_data = df.iloc[:, 0].dropna().unique().tolist()
            return [clean_postcode(p) for p in first_col_data if p]
        return []
    except:
        return []

postcodes = get_data()

with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(postcodes)} Locations Tracked")
    if st.button("🔄 Force Refresh Map"):
        st.cache_data.clear()
        st.rerun()

# Map initialization
m = folium.Map(location=[53.7997, -1.5492], zoom_start=12) # زوم أقرب قليلاً
geolocator = Nominatim(user_agent="west_yorkshire_precision_v4")

if postcodes:
    for pc in postcodes:
        try:
            location = geolocator.geocode(f"{pc}, West Yorkshire, UK", timeout=10)
            if location:
                # استخدام Marker للدقة العالية
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup=f"Target: {pc}",
                    icon=folium.Icon(color='green', icon='cloud')
                ).add_to(m)
        except:
            continue

st_folium(m, width="100%", height=600)
