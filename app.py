import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from streamlit_js_eval import streamlit_js_eval

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", layout="wide")

# --- مظهر التطبيق (RTL وجمالية الواجهة) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Amiri:wght@700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL; text-align: right; font-family: 'Cairo', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .prayer-card {
        background: #ffffff; padding: 15px; border-radius: 12px; text-align: center;
        border-top: 5px solid #d4af37; box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .prayer-time { font-size: 1.6rem; font-weight: bold; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# --- معالجة التاريخ والوقت بالعربية ---
days_ar = {"Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
today = date.today()
hijri = HijriDate.get_hijri_date(today)
current_time = datetime.now().strftime("%I:%M").replace("AM", "صباحاً").replace("PM", "مساءً")

st.markdown(f"""
    <div class="main-header">
        <h1 style='font-family: Amiri; margin:0;'>🕌 مواقيت الصلاة بتونس</h1>
        <p style='font-size: 1.2rem; margin:10px 0;'>
            {days_ar[today.strftime('%A')]} : {today.strftime('%d / %m / %Y')} م | {hijri} هـ
        </p>
        <h2 style='margin:0;'>⏰ الوقت الآن: {current_time}</h2>
    </div>
    """, unsafe_allow_html=True)

# --- تفعيل GPS ---
st.sidebar.title("🌍 خدمات الموقع")
gps_active = st.sidebar.checkbox("تفعيل الموقع التلقائي (GPS)")
gps_data = None
if gps_active:
    gps_data = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition(pos => { return pos.coords; }, err => { return null; })', key='gps')

# --- تحميل البيانات وتحسين الخيارات ---
@st.cache_data
def load_data():
    return pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'])

df = load_data()

# قاعدة بيانات مبسطة للإحداثيات (لتتغير الأوقات حسب الولاية)
# ملاحظة: هذه الإحداثيات تقريبية وتتغير حسب اختيارك
STATE_COORDS = {
    "تونس": (36.80, 10.18), "بنزرت": (37.27, 9.87), "توزر": (33.91, 8.13), 
    "صفاقس": (34.74, 10.76), "مدنين": (33.35, 10.49), "جندوبة": (36.50, 8.77)
}

lat, lon = (36.80, 10.18) # القيمة الافتراضية

if gps_active and gps_data:
    lat, lon = gps_data['latitude'], gps_data['longitude']
    st.success(f"📍 تم التحديث حسب موقعك الفعلي: {lat:.2f}, {lon:.2f}")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_state = st.selectbox("📌 الولاية", ["-- اختر --"] + sorted(df['الولاية'].unique().tolist()))
    if sel_state != "-- اختر --":
        # تحديث الإحداثيات بناءً على الولاية المختارة
        lat, lon = STATE_COORDS.get(sel_state, (36.80, 10.18))
        with col2:
            sel_district = st.selectbox("🏢 المعتمدية", sorted(df[df['الولاية'] == sel_state]['المعتمدية'].unique()))
        with col3:
            sel_village = st.selectbox("🏡 العمادة", sorted(df[(df['الولاية'] == sel_state) & (df['المعتمدية'] == sel_district)]['العمادة'].unique()))

# --- حساب المواقيت بناءً على الموقع المختار ---
calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
times = calc.fetch_prayer_times()

# --- عرض المواقيت في بطاقات ---
st.divider()
p_cols = st.columns(5)
prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]

for i, (name, key) in enumerate(prayers):
    with p_cols[i]:
        st.markdown(f"""
            <div class="prayer-card">
                <div style='color: #1b5e20; font-weight: bold;'>{name}</div>
                <div class="prayer-time">{times[key]}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #888;'>يتم تغيير الأوقات تلقائياً عند تغيير الولاية أو تفعيل GPS</p>", unsafe_allow_html=True)
