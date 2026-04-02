import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- Google Sheets Connection Settings ---
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Page Configuration
st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")

# The New Project Title
st.title("📍 WYCA HEWY Outreach")
st.markdown("Real-time tracking for outreach campaign across West Yorkshire.")

# Function to clean and format UK postcodes automatically
def clean_postcode(pc):
    if pd.isna(pc): return None
    clean_pc = "".join(filter(str.isalnum, str(pc))).upper()
    if len(clean_pc) > 3:
        return clean_pc[:-3] + " " + clean_pc[-3:]
    return clean_pc

# Function to fetch data from the FIRST column
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

# Execute Data Fetching
postcodes = get_data()

# Sidebar UI
with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(postcodes)} Locations Covered")
    
    if st.button("🔄 Force Refresh Map"):
        st.cache_data.clear()
        st.rerun()
    
    st.write("---")
    st.info("The map shows precise markers for every postcode added to Column A of your sheet.")

# Initialize the Map (Centered on West Yorkshire)
m = folium.Map(location=[53.7997, -1.5492], zoom_start=11)
geolocator = Nominatim(user_agent="wyca_hewy_outreach_tracker")

if postcodes:
    for pc in postcodes:
        try:
            # Geocoding for precise location
            location = geolocator.geocode(f"{pc}, West Yorkshire, UK", timeout=10)
            if location:
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup=f"Outreach Site: {pc}",
                    icon=folium.Icon(color='green', icon='map-marker')
                ).add_to(m)
        except:
            continue

# Render the Map
st_folium(m, width="100%", height=600)
