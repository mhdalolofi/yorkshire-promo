import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# --- إعدادات الربط ---
# استبدل الكود أدناه بـ ID الجدول الخاص بك الذي نسخته في الخطوة السابقة
SHEET_ID = "102kIAxa0-fZb4L6FCUBTj-ffg3Ob_3eIBYD1IZGJ2gA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="متابعة ترويج وست يوركشاير", layout="wide")

st.title("🗺️ خريطة مناطق الترويج المكتملة")
st.markdown("يتم جلب البيانات تلقائياً من جدول بيانات جوجل")

# دالة لجلب البيانات وتخزينها مؤقتاً لتسريع التطبيق
@st.cache_data(ttl=60) # تحديث البيانات كل دقيقة
def get_data():
    df = pd.read_csv(SHEET_URL)
    return df['postcode'].dropna().unique().tolist()

try:
    postcodes = get_data()
    
    # واجهة جانبية
    st.sidebar.success(f"تم تغطية {len(postcodes)} منطقة حتى الآن")
    if st.sidebar.button("تحديث يدوي"):
        st.cache_data.clear()
        st.rerun()

    # رسم الخريطة
    m = folium.Map(location=[53.7997, -1.5492], zoom_start=10)
    geolocator = Nominatim(user_agent="west_yorkshire_tracker")

    for pc in postcodes:
        location = geolocator.geocode(f"{pc}, West Yorkshire, UK")
        if location:
            folium.Circle(
                location=[location.latitude, location.longitude],
                radius=1300, 
                color='green',
                fill=True,
                fill_opacity=0.6,
                popup=f"المنطقة: {pc}"
            ).add_to(m)

    st_folium(m, width="100%", height=600)

except Exception as e:
    st.error("تأكد من وضع SHEET_ID الصحيح ومن أن الجدول 'عام' (Anyone with link can view)")