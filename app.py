import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- Google Sheets Connection Settings ---
# Your Spreadsheet ID
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Page Configuration
st.set_page_config(page_title="West Yorkshire Promotion Tracker", layout="wide")

st.title("🗺️ West Yorkshire Promotion Map")
st.markdown("This map updates automatically from your Google Sheets data.")

# Function to fetch data from the Google Sheet
@st.cache_data(ttl=60)
def get_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Clean column names (lowercase and remove spaces)
        df.columns = [c.lower().replace(" ", "") for c in df.columns]
        if 'postcode' in df.columns:
            return df['postcode'].dropna().unique().tolist()
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
    st.info("Tip: Add new postcodes to your Google Sheet, then click Refresh.")

# Initialize the Map
# Centered around West Yorkshire (Leeds/Bradford area)
m = folium.Map(location=[53.7997, -1.5492], zoom_start=10)
geolocator = Nominatim(user_agent="west_yorkshire_promo_tracker")

if postcodes:
    for pc in postcodes:
        try:
            # Geocoding: Search for postcode specifically within West Yorkshire, UK
            location = geolocator.geocode(f"{str(pc)}, West Yorkshire, UK", timeout=10)
            if location:
                folium.Circle(
                    location=[location.latitude, location.longitude],
                    radius=1300, # Radius of coverage in meters
                    color='green',
                    fill=True,
                    fill_opacity=0.6,
                    popup=f"Postcode: {pc}"
                ).add_to(m)
        except:
            # Skip errors silently if a postcode is invalid
            continue

# Render the Map in the App
st_folium(m, width="100%", height=600)
