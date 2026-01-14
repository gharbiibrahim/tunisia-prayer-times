import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
import time

# إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة في تونس", page_icon="🕌", layout="centered")

# قاعدة بيانات سريعة للولايات (لتجنب أخطاء الخدمة الخارجية)
TUNISIA_CITIES = {
    "تونس العاصمة": (36.8065, 10.1815),
    "بنزرت": (37.2744, 9.8739),
    "ماطر": (37.0400, 9.6650),
    "أريانة": (36.8665, 10.1647),
    "منوبة": (36.8078, 10.0863),
    "بن عروس": (36.7531, 10.2222),
    "نابل": (36.4561, 10.7376),
    "باجة": (36.7256, 9.1906),
    "جندوبة": (36.5011, 8.7802),
    "الكاف": (36.1822, 8.7148),
    "سليانة": (36.0840, 9.3708),
    "سوسة": (35.8256, 10.6084),
    "المنستير": (35.7780, 10.8262),
    "المهدية": (35.5047, 11.0622),
    "القيروان": (35.6781, 10.0963),
    "سيدي بوزيد": (35.0382, 9.4849),
    "القصرين": (35.1676, 8.8365),
    "صفاقس": (34.7400, 10.7600),
    "قفصة": (34.4250, 8.7842),
    "توزر": (33.9197, 8.1335),
    "قبلي": (33.7050, 8.9714),
    "قابس": (33.8815, 10.0982),
    "مدنين": (33.3550, 10.4922),
    "تطاوين": (32.9297, 10.4518)
}

# تنسيق RTL والجمالية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] {
        direction: RTL; text-align: right; font-family: 'Cairo', sans-serif;
    }
    .countdown-section {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        color: white; padding: 25px; border-radius: 20px;
        text-align: center; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .prayer-card {
        background: white; padding: 15px; border-radius: 12px;
        text-align: center; border: 1px solid #eee; margin-bottom: 10px;
    }
    .prayer-time { font-size: 1.5rem; font-weight: bold; color: #0d47a1; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕌 أوقات الصلاة في تونس")

# اختيار الموقع (قائمة سريعة + بحث يدوي)
col1, col2 = st.columns([1, 1])
with col1:
    city_choice = st.selectbox("اختر الولاية:", list(TUNISIA_CITIES.keys()))
with col2:
    manual_search = st.text_input("أو ابحث عن معتمدية/قرية:")

# تحديد الإحداثيات النهائية
if manual_search:
    try:
        geolocator = Nominatim(user_agent="Tunisia_Prayer_Unique_2026")
        location = geolocator.geocode(manual_search + ", Tunisia", timeout=5)
        if location:
            lat, lon = location.latitude, location.longitude
            st.caption(f"📍 الموقع: {location.address}")
        else:
            lat, lon = TUNISIA_CITIES[city_choice]
            st.warning("لم يتم العثور على المكان، تم استخدام إحداثيات الولاية.")
    except:
        lat, lon = TUNISIA_CITIES[city_choice]
else:
    lat, lon = TUNISIA_CITIES[city_choice]

# حساب الأوقات
calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
times = calc.fetch_prayer_times()
prayers_ar = {"Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}

# منطق العداد التنازلي
now = datetime.now()
next_p_name, next_p_time = "", None

for eng, ar in prayers_ar.items():
    p_time = datetime.strptime(times[eng], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    if p_time > now:
        next_p_name, next_p_time = ar, p_time
        break

if not next_p_time:
    next_p_name = "الفجر"
    next_p_time = datetime.strptime(times["Fajr"], "%H:%M").replace(year=now.year, month=now.month, day=now.day) + timedelta(days=1)

diff = next_p_time - now
hours, remainder = divmod(diff.seconds, 3600)
minutes, seconds = divmod(remainder, 60)

# عرض العداد
st.markdown(f"""
    <div class="countdown-section">
        <p style='margin:0;'>بقي على صلاة {next_p_name}</p>
        <h1 style='font-size: 3.5rem; margin:0;'>{hours:02d}:{minutes:02d}:{seconds:02d}</h1>
    </div>
""", unsafe_allow_html=True)

# عرض الأوقات
cols = st.columns(3)
for i, (eng, ar) in enumerate(prayers_ar.items()):
    with cols[i % 3]:
        st.markdown(f"<div class='prayer-card'><div>{ar}</div><div class='prayer-time'>{times[eng]}</div></div>", unsafe_allow_html=True)

# تشغيل الأذان (تلقائي عند الصفر)
if diff.seconds == 0:
    st.audio("https://www.islamcan.com/adhan/duas/adhan-makkah.mp3", autoplay=True)
    st.balloons()

time.sleep(1)
st.rerun()
