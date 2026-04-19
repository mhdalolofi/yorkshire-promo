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

# --- 2. DATA LOADING & GROUPING ---
def clean_pc(pc):
    if pd.isna(pc) or str(pc).strip() == "": return None
    val = re.sub(r'[^A-Z0-9]', '', str(pc).upper())
    if len(val) > 3: return val[:-3] + " " + val[-3:]
    return val

@st.cache_data(ttl=5)
def load_and_group_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if df.empty: return []
            
        # Ensure we have the necessary columns
        if len(df.columns) >= 3:
            raw_data = df.iloc[:, [0, 1, 2]].copy()
            raw_data.columns = ['raw_pc', 'name', 'status']
        else:
            raw_data = df.iloc[:, [0, 1]].copy()
            raw_data.columns = ['raw_pc', 'name']
            raw_data['status'] = 'To Visit' 
            
        raw_data['clean_pc'] = raw_data['raw_pc'].apply(clean_pc)
        raw_data['name'] = raw_data['name'].fillna("Unnamed Site").astype(str).str.strip()
        raw_data['status'] = raw_data['status'].fillna("To Visit").astype(str).str.strip()
        
        # Filter out invalid postcodes
        valid_df = raw_data.dropna(subset=['clean_pc'])
        
        # GROUPING LOGIC: Group by postcode to handle multiple sites in one location
        grouped = valid_df.groupby('clean_pc').apply(lambda x: x.to_dict('records')).reset_index()
        grouped.columns = ['clean_pc', 'sites']
        return grouped.to_dict('records')
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return []

# --- 3. GEOCODING ---
@st.cache_data(ttl=86400)
def get_coords_smart(pc):
    geolocator = ArcGIS()
    try:
        loc = geolocator.geocode(f"{pc}, West Yorkshire, UK", timeout=10)
        return (loc.latitude, loc.longitude) if loc else None
    except: return None

def process_parallel(locations):
    with ThreadPoolExecutor(max_workers=10) as executor:
        pcs = [l['clean_pc'] for l in locations]
        return list(executor.map(get_coords_smart, pcs))

# --- 4. APP LOGIC ---
grouped_locations = load_and_group_data()

with st.sidebar:
    st.header("📊 Campaign Audit")
    if grouped_locations:
        all_sites = [site for group in grouped_locations for site in group['sites']]
        visited_count = sum(1 for s in all_sites if 'visited' in s['status'].lower() and 'to visit' not in s['status'].lower())
        st.info(f"Unique Locations: {len(grouped_locations)}")
        st.success(f"🟢 Total Visited: {visited_count}")
        st.error(f"🔴 Total To Visit: {len(all_sites) - visited_count}")
    if st.button("🔄 Force Global Sync"):
        st.cache_data.clear()
        st.rerun()

m = folium.Map(location=[53.8, -1.5], zoom_start=11)

if grouped_locations:
    with st.spinner('🚀 Processing groups...'):
        coords_list = process_parallel(grouped_locations)
    
    for i, group in enumerate(grouped_locations):
        coords = coords_list[i]
        if coords:
            # Build an HTML list for the popup
            popup_content = f"<b>Postcode: {group['clean_pc']}</b><hr>"
            has_visited = False
            has_to_visit = False
            
            for site in group['sites']:
                status = site['status'].lower()
                is_visited = 'visited' in status and 'to visit' not in status
                color = "green" if is_visited else "red"
                symbol = "✅" if is_visited else "⭕"
                popup_content += f"<div style='color:{color}; margin-bottom:5px;'>{symbol} {site['name']}</div>"
                if is_visited: has_visited = True
                else: has_to_visit = True
            
            # Determine overall marker color
            # If all visited -> green. If any needs visit -> red. Or "mixed" color.
            final_color = 'green' if (has_visited and not has_to_visit) else 'red'
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{len(group['sites'])} sites at {group['clean_pc']}",
                icon=folium.Icon(color=final_color, icon='map-pin', prefix='fa')
            ).add_to(m)

st_folium(m, width="100%", height=650)
