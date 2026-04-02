import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# 1. Config
st.set_page_config(page_title="WYCA HEWY Outreach", layout="wide")
st.title("📍 WYCA HEWY Outreach")

# 2. Connection
ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
URL = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv"

# 3. Data Fetch
@st.cache_data(ttl=5)
def load():
    try:
        df = pd.read_csv(URL)
        # Take first column, clean spaces, convert to upper
        return [str(x).strip().upper() for x in df.iloc[:, 0].dropna()]
    except:
        return []

pc_list = load()
st.sidebar.success(f"Total Sites: {len(pc_list)}")

# 4. Map
m = folium.Map(location=[53.8, -1.5], zoom_start=11)
geo = Nominatim(user_agent="wyca_final_test")

for pc in pc_list:
    try:
        res = geo.geocode(f"{pc}, West Yorkshire, UK")
        if res:
            folium.Marker([res.latitude, res.longitude], popup=pc, icon=folium.Icon(color='green')).add_to(m)
    except:
        continue

st_folium(m, width="100%", height=600)
