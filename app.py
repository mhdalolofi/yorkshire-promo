import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
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
    """Formats UK postcodes and removes illegal characters."""
    if pd.isna(pc) or str(pc).strip() == "": return None
    val = re.sub(r'[^A-Z0-9]', '', str(pc).upper())
    if len(val) > 3:
        return val[:-3] + " " + val[-3:]
    return val

@st.cache_data(ttl=5)
def load_and_clean_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if df.empty: return []
        
        # Take Column A (Postcode) and Column B (Site Name)
        raw_data = df.iloc[:, [0, 1]].copy()
        raw_data.columns = ['raw_pc', 'name']
        
        # Fix: Proper string cleaning for names and postcodes
        raw_data['clean_pc'] = raw_data['raw_pc'].apply(clean_pc)
        raw_data['name'] = raw_data['name'].fillna("Unnamed Site").astype(str).str.strip()
        
        # Remove entries without a postcode
        valid_data = raw_data.dropna(subset=['clean_pc']).to_dict('records')
        return valid_data
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return []

# --- 3. SMART GEOCODING ---
@st.cache_data(ttl=86400)
def get_coords_smart(pc):
    geolocator = Nominatim(user_agent="wyca_precision_v14_final")
    # Try multiple search variations for maximum accuracy
    queries = [f"{pc}, West Yorkshire, UK", f"{pc}, UK"]
    for q in queries:
        try:
            loc = geolocator.geocode(q, timeout=5)
            if loc: return (loc.latitude, loc.longitude)
        except: continue
    return None

def process_parallel(locations):
    with ThreadPoolExecutor(max_workers=10) as executor:
        pcs = [l['clean_pc'] for l in locations]
        return list(executor.map(get_coords_smart, pcs))

# --- 4. APP LOGIC ---
locations = load_and_clean_data()

with st.sidebar:
    st.header("📊 Campaign Audit")
    if locations:
        st.info(f"Sites found in Sheet: {len(locations)}")
    if st.button("🔄 Force Global Sync"):
        st.cache_data.clear()
        st.rerun()

m = folium.Map(location=[53.8, -1.5], zoom_start=11)

if locations:
    with st.spinner('🚀 Analyzing 250+ locations...'):
        all_coords = process_parallel(locations)
    
    found_count = 0
    failed_list = []

    for i, row in enumerate(locations):
        coords = all_coords[i]
        if coords:
            folium.Marker(
                location=coords,
                popup=folium.Popup(f"<b>{row['name']}</b><br>{row['clean_pc']}", max_width=300),
                tooltip=row['name'],
                icon=folium.Icon(color='green', icon='map-pin', prefix='fa')
            ).add_to(m)
            found_count += 1
        else:
            failed_list.append(f"{row['raw_pc']} - {row['name']}")

    st.sidebar.success(f"✅ Displayed: {found_count}")
    if failed_list:
        with st.sidebar.expander(f"⚠️ Failed to locate ({len(failed_list)})"):
            st.write("Postcodes not found (check for typos):")
            for item in failed_list:
                st.error(item)

# --- 5. RENDER ---
st_folium(m, width="100%", height=650)        # Apply cleaning
        raw_data['clean_pc'] = raw_data['raw_pc'].apply(clean_pc)
        raw_data['name'] = raw_data['name'].fillna("Unnamed Site").strip()
        
        # Remove rows where postcode is absolutely missing
        valid_data = raw_data.dropna(subset=['clean_pc']).to_dict('records')
        return valid_data
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return []

# --- 3. HIGH-SPEED SMART SEARCH ---
@st.cache_data(ttl=86400)
def get_coords_smart(pc):
    """Tries multiple ways to find a postcode if it's tricky."""
    geolocator = Nominatim(user_agent="wyca_ultra_precision_v12")
    search_queries = [
        f"{pc}, West Yorkshire, UK",
        f"{pc}, UK",
        pc
    ]
    for query in search_queries:
        try:
            location = geolocator.geocode(query, timeout=5)
            if location:
                return (location.latitude, location.longitude)
        except:
            continue
    return None

def process_locations_parallel(locations):
    """Runs 10 searches at once for maximum speed."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        postcodes = [loc['clean_pc'] for loc in locations]
        results = list(executor.map(get_coords_smart, postcodes))
    return results

# --- 4. MAIN APP LOGIC ---
locations = load_and_clean_data()

# Sidebar for Stats and Audit
with st.sidebar:
    st.header("📊 Campaign Audit")
    if locations:
        st.info(f"Total rows in Sheet: {len(locations)}")
    
    if st.button("🔄 Force Global Sync"):
        st.cache_data.clear()
        st.rerun()

# Initialize Map
m = folium.Map(location=[53.8, -1.5], zoom_start=11)

if locations:
    with st.spinner('🚀 Processing 250+ locations using High-Speed Engine...'):
        all_coords = process_locations_parallel(locations)
    
    found_count = 0
    failed_list = []

    for i, row in enumerate(locations):
        coords = all_coords[i]
        if coords:
            folium.Marker(
                location=coords,
                popup=folium.Popup(f"<b>{row['name']}</b><br>{row['clean_pc']}", max_width=300),
                tooltip=row['name'],
                icon=folium.Icon(color='green', icon='map-pin', prefix='fa')
            ).add_to(m)
            found_count += 1
        else:
            failed_list.append(f"{row['raw_pc']} - {row['name']}")

    # Display status in Sidebar
    st.sidebar.success(f"✅ Displayed: {found_count}")
    if failed_list:
        with st.sidebar.expander(f"⚠️ Failed to locate ({len(failed_list)})"):
            st.write("Check these postcodes for typos in your Google Sheet:")
            for item in failed_list:
                st.error(item)

# 5. RENDER MAP
st_folium(m, width="100%", height=650)
