import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- Google Sheets Connection Settings ---
# Your fixed Spreadsheet ID
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Page Configuration
st.set_page_config(page_title="West Yorkshire Promotion Tracker", layout="wide")

st.title("🗺️ West Yorkshire Promotion Map")
st.markdown("Direct tracking from Google Sheets. Postcodes are fetched from the FIRST column.")

# Improved cleaning function
def clean_postcode(pc):
    if pd.isna(pc): return None
    # Remove all spaces and special characters, convert to uppercase
    clean_pc = "".join(filter(str.isalnum, str(pc))).upper()
    # Format for UK (Space before last 3 chars)
    if len(clean_pc) > 3:
        return clean_pc[:-3] + " " + clean_pc[-3:]
    return clean_pc

# Function to fetch data (Now reading ONLY the first column regardless of its name)
@st.cache_data(ttl=10) # Refresh very fast (every 10 seconds)
def get_data():
    try:
        # Read the sheet
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            # Take the very first column by position (index 0)
            first_col_data = df.iloc[:, 0].dropna().unique().tolist()
            # Clean and return
            return [clean_postcode(p) for p in first_col_data if p]
        return []
    except Exception as e:
        return []

# Execute Data Fetching
postcodes = get_data()

# Sidebar UI
with st.sidebar:
    st.header("Campaign Progress")
    if postcodes:
        st.success(f"✅ {len(postcodes)} Postcodes Found")
    else:
        st.warning("⚠️ No postcodes detected in the first column.")
    
    if st.button("🔄 Force Refresh Map"):
        st.cache_data.clear()
        st.rerun()
    
    st.write("---")
    st.info("Make sure your postcodes are in the FIRST column (Column A) of your sheet.")

# Initialize the Map (Leeds Center)
m = folium.Map(location=[53.7997, -1.5492], zoom_start=11)
geolocator = Nominatim(user_agent="west_yorkshire_final_v3")

if postcodes:
    for pc in postcodes:
        try:
            # Specific search for West Yorkshire
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

# Render the Map
st_folium(m, width="100%", height=600)
