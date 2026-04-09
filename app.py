import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import ArcGIS
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import re

# --- 1. CONFIGURATION ---
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")
st.title("📍 WYCA HEWY Outreach - Precision Dashboard")

# --- 2. DATA CLEANING FUNCTIONS ---
def clean_pc(pc):
    """Clean and format UK postcodes."""
    if pd.isna(pc) or str(pc).strip() == "":
        return None
    # Remove special characters and spaces, convert to uppercase
    val = re.sub(r'[^A-Z0-9]', '', str(pc).upper())
    # Format with space (e.g., LS146HH -> LS14 6HH)
    if len(val) > 3:
        return val[:-3] + " " + val[-3:]
    return val

@st.cache_data(ttl=5)
def load_and_clean_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if df.empty:
            return []
            
        # Check if the sheet has at least 3 columns (Postcode, Name, Status)
        if len(df.columns) >= 3:
            raw_data = df.iloc[:, [0, 1, 2]].copy()
            raw_data.columns = ['raw_pc', 'name', 'status']
        else:
            # Fallback if the Status column hasn't been created yet
            raw_data = df.iloc[:, [0, 1]].copy()
            raw_data.columns = ['raw_pc', 'name']
            raw_data['status'] = 'To Visit' 
            
        # Clean data and remove extra spaces
        raw_data['clean_pc'] = raw_data['raw_pc'].apply(clean_pc)
        raw_data['name'] = raw_data['name'].fillna("Unnamed Site").astype(str).str.strip()
        raw_data['status'] = raw_data['status'].fillna("To Visit").astype(str).str.strip()
        
        # Drop rows without a valid postcode
        valid_data = raw_data.dropna(subset=['clean_pc']).to_dict('records')
        return valid_data
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return []

# --- 3. SMART GEOCODING (ArcGIS Engine) ---
@st.cache_data(ttl=86400)
def get_coords_smart(pc):
    """Fetch coordinates using ArcGIS for better accuracy and speed."""
    geolocator = ArcGIS()
    queries = [f"{pc}, West Yorkshire, UK", f"{pc}, UK"]
    for q in queries:
        try:
            loc = geolocator.geocode(q, timeout=10)
            if loc:
                return (loc.latitude, loc.longitude)
        except:
            continue
    return None

def process_parallel(locations):
    """Process multiple locations at the same time to speed up loading."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        pcs = [l['clean_pc'] for l in locations]
        return list(executor.map(get_coords_smart, pcs))

# --- 4. APP MAIN LOGIC ---
locations = load_and_clean_data()

with st.sidebar:
    st.header("📊 Campaign Audit")
    if locations:
        # Count visited vs to visit locations
        visited_count = sum(1 for loc in locations if 'visited' in loc['status'].lower() and 'to visit' not in loc['status'].lower())
        to_visit_count = len(locations) - visited_count
        
        st.info(f"Total entries: {len(locations)}")
        st.success(f"🟢 Visited: {visited_count}")
        st.error(f"🔴 To Visit: {to_visit_count}")
        
    if st.button("🔄 Force Global Sync"):
        st.cache_data.clear()
        st.rerun()

m = folium.Map(location=[53.8, -1.5], zoom_start=11)

if locations:
    with st.spinner('🚀 Processing locations and updating statuses...'):
        all_coords = process_parallel(locations)
    
    found_count = 0
    failed_list = []

    for i, row in enumerate(locations):
        coords = all_coords[i]
        if coords:
            # Determine color and icon based on status
            is_visited = 'visited' in row['status'].lower() and 'to visit' not in row['status'].lower()
            marker_color = 'green' if is_visited else 'red'
            icon_type = 'check' if is_visited else 'info-sign'
            status_text = '🟢 Visited' if is_visited else '🔴 To Visit'
            
            # Create popup HTML content
            popup_html = f"<b>{row['name']}</b><br>{row['clean_pc']}<br><br><b>Status:</b> {status_text}"
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['name']} ({status_text})",
                icon=folium.Icon(color=marker_color, icon=icon_type, prefix='fa')
            ).add_to(m)
            found_count += 1
        else:
            failed_list.append(f"{row['raw_pc']} - {row['name']}")

    if failed_list:
        with st.sidebar.expander(f"⚠️ Failed to Locate ({len(failed_list)})"):
            st.write("Please check these postcodes in your Google Sheet:")
            for item in failed_list:
                st.error(item)

# --- 5. RENDER MAP ---
st_folium(m, width="100%", height=650)
