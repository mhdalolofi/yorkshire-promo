import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd
import re

# --- Google Sheets Connection Settings ---
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Page Configuration
st.set_page_config(page_title="West Yorkshire Promotion Tracker", layout="wide")

st.title("🗺️ West Yorkshire Promotion Map")
st.markdown("Automated tracking system for your business promotion areas.")

# Function to clean and format UK postcodes automatically
def clean_postcode(pc):
    if pd.isna(pc): return None
    # Remove all spaces and convert to uppercase
    clean_pc = str(pc).replace(" ", "").upper()
    # If it's a standard UK postcode, insert a space before the last 3 characters
    if len(clean_pc) > 3:
        formatted_pc = clean_pc[:-3] + " " + clean_pc[-3:]
        return formatted_pc
    return clean_pc

# Function to fetch data from the Google Sheet
@st.cache_data(ttl=60)
def get_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Find the column that contains 'post' (to avoid spelling errors in header)
        target_col = None
        for col in df.columns:
            if 'post' in col.lower():
                target_col = col
                break
        
        if target_col:
            raw_list = df[target_col].dropna().unique().tolist()
            # Clean each postcode in the list
            return [clean_postcode(p) for p in raw_list if p]
        else:
            return []
    except Exception as e:
        return []

# Execute Data Fetching
postcodes = get_data()

# Sidebar UI
with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(postcodes)} Areas Completed")
    
    if st.button("🔄 Refresh Map Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.write("---")
    st.info("The system now automatically fixes spacing and typing errors from your sheet.")

# Initialize the Map
m = folium.Map(location=[53.7997, -1.5492], zoom_start=11)
geolocator = Nominatim(user_agent="west_yorkshire_promo_final")

if postcodes:
    for pc in postcodes:
        try:
            # Geocoding: Force search within West Yorkshire for accuracy
            location = geolocator.geocode(f"{pc}, West Yorkshire, UK", timeout=10)
            if location:
                folium.Circle(
                    location=[location.latitude, location.longitude],
                    radius=1200,
                    color='green',
                    fill=True,
                    fill_opacity=0.6,
                    popup=f"Postcode: {pc}"
                ).add_to(m)
        except:
            continue

# Render the Map in the App
st_folium(m, width="100%", height=600)
