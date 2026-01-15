import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from streamlit_js_eval import streamlit_js_eval # لجلب الموقع الجغرافي GPS

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة وخدمات الموقع", page_icon="🕌", layout="wide")

# --- تحسين التصميم CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Amiri:wght@700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL; text-align: right; font-family: 'Cairo', sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    .prayer-card {
        background: white; padding: 15px; border-radius: 12px; text-align: center;
        border-bottom: 4px solid #d4af37; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stSelectbox label { font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- جلب البيانات الجغرافية (GPS) ---
st.sidebar.title("🌍 تحديد الموقع الذكي")
use_gps = st.sidebar.checkbox("استخدام موقعي الحالي (GPS)")

loc = None
if use_gps:
    loc = streamlit_js_eval(js_expressions='screen.width', key='viewport') # تفعيل JS
    loc = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition(pos => { return pos.coords; }, err => { return null; })', key='gps')

# --- معالجة التاريخ والوقت ---
days_ar = {
    "Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
    "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
}
today = date.today()
day_name = days_ar[today.strftime('%A')]
hijri = HijriDate.get_hijri_date(today)
current_time = datetime.now().strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")

# --- واجهة التاريخ ---
st.markdown(f"""
    <div class="header-box">
        <h2 style='font-family: Amiri;'>{day_name}</h2>
        <p style='font-size: 1.2rem;'>
            🗓️ ميلادي: {today.strftime('%d / %m / %Y')} | 🌙 هجري: {hijri}
        </p>
        <h3>⌚ الوقت الآن: {current_time}</h3>
    </div>
    """, unsafe_allow_html=True)

# --- تحميل البيانات ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'])
    except: return None

df = load_data()

# --- واجهة اختيار المناطق المحسنة ---
if df is not None and not (use_gps and loc):
    st.markdown("### 📍 اختيار المنطقة يدوياً")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        sel_state = st.selectbox("📌 الولاية", ["-- اختر --"] + sorted(df['الولاية'].unique().tolist()))
    with c2:
        if sel_state != "-- اختر --":
            districts = sorted(df[df['الولاية'] == sel_state]['المعتمدية'].unique())
            sel_district = st.selectbox("🏢 المعتمدية", districts)
        else: st.selectbox("🏢 المعتمدية", ["انتظر اختيار الولاية"], disabled=True)
    with c3:
        if sel_state != "-- اختر --":
            villages = sorted(df[(df['الولاية'] == sel_state) & (df['المعتمدية'] == sel_district)]['العمادة'].unique())
            sel_village = st.selectbox("🏡 العمادة", villages)
        else: st.selectbox("🏡 العمادة", ["انتظر اختيار المعتمدية"], disabled=True)

# --- حساب المواقيت ---
# إذا تم تفعيل GPS نستخدم إحداثياته، وإلا نستخدم إحداثيات افتراضية لتونس
lat, lon = (36.8, 10.1) # العاصمة كافتراض
if use_gps and loc:
    lat, lon = loc['latitude'], loc['longitude']
    st.success(f"📍 تم تحديد موقعك بدقة عبر GPS")

calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
times = calc.fetch_prayer_times()

# عرض النتائج
st.divider()
p_cols = st.columns(5)
prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]

for i, (ar, en) in enumerate(prayers):
    with p_cols[i]:
        st.markdown(f"""
            <div class="prayer-card">
                <div style='color: #2e7d32; font-weight: bold;'>{ar}</div>
                <div style='font-size: 1.5rem;'>{times[en]}</div>
            </div>
            """, unsafe_allow_html=True)
