import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- CONNECTION SETTINGS ---
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- PAGE CONFIG ---
st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")

st.title("📍 WYCA HEWY Outreach")
st.markdown("Precision tracking with Site Names and High-Speed Caching.")

# --- FAST DATA LOADING ---
@st.cache_data(ttl=10)
def load_sheet_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            # نأخذ العمود الأول (الرمز) والعمود الثاني (الاسم)
            # نستخدم .iloc لضمان الترتيب بغض النظر عن أسماء الأعمدة
            data = df.iloc[:, [0, 1]].dropna()
            data.columns = ['pc', 'name']
            
            # تنظيف الرموز البريدية
            data['pc'] = data['pc'].apply(lambda x: str(x).strip().upper())
            return data.values.tolist()
        return []
    except:
        return []

# --- SMART GEOCODING ---
@st.cache_data(ttl=3600)
def get_location_coordinates(pc):
    geo = Nominatim(user_agent="wyca_fast_v8_names")
    try:
        res = geo.geocode(f"{pc}, West Yorkshire, UK", timeout=5)
        if res:
            return (res.latitude, res.longitude)
    except:
        return None
    return None

# --- MAIN APP LOGIC ---
locations_data = load_sheet_data()

with st.sidebar:
    st.header("Campaign Progress")
    st.success(f"✅ {len(locations_data)} Sites Processed")
    if st.button("🔄 Clear Cache & Sync"):
        st.cache_data.clear()
        st.rerun()
    st.write("---")
    st.info("Now showing Site Names instead of just postcodes.")

# Initialize Map
m = folium.Map(location=[53.7997, -1.5492], zoom_start=11)

if locations_data:
    for row in locations_data:
        pc = row[0]   # الرمز البريدي
        name = row[1] # اسم المكان
        
        coords = get_location_coordinates(pc)
        if coords:
            folium.Marker(
                location=coords,
                popup=f"<b>{name}</b><br>Postcode: {pc}", # يظهر الاسم بخط عريض
                tooltip=name, # يظهر الاسم بمجرد مرور الماوس فوق الدبوس
                icon=folium.Icon(color='green', icon='map-pin', prefix='fa')
            ).add_to(m)

# Display Map
st_folium(m, width="100%", height=600)
