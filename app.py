import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from hijri_converter import Gregorian
import time

# إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة في تونس", page_icon="🕌", layout="centered")

# قاعدة بيانات الولايات
TUNISIA_CITIES = {
    "تونس العاصمة": (36.8065, 10.1815), "بنزرت": (37.2744, 9.8739), "ماطر": (37.0400, 9.6650),
    "سوسة": (35.8256, 10.6084), "صفاقس": (34.7400, 10.7600), "القيروان": (35.6781, 10.0963),
    "قابس": (33.8815, 10.0982), "مدنين": (33.3550, 10.4922), "تطاوين": (32.9297, 10.4518)
}

# تنسيق RTL والجمالية (ألوان العلم التونسي)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .countdown-section {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        color: white; padding: 25px; border-radius: 20px;
        text-align: center; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .date-section {
        background-color: #f8f9fa; padding: 10px; border-radius: 10px;
        text-align: center; margin-bottom: 20px; border: 1px solid #dee2e6;
    }
    .prayer-card {
        background: white; padding: 15px; border-radius: 12px;
        text-align: center; border: 1px solid #eee; margin-bottom: 10px;
    }
    .prayer-time { font-size: 1.5rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕌 أوقات الصلاة في تونس")

# حساب التاريخ الهجري
today = date.today()
hijri = Gregorian(today.year, today.month, today.day).to_hijri()
months_ar = ["محرّم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

st.markdown(f"""
    <div class="date-section">
        <b>{today.strftime('%Y-%m-%d')} م</b> | 
        <b>{hijri.day} {months_ar[hijri.month-1]} {hijri.year} هـ</b>
    </div>
""", unsafe_allow_html=True)

# اختيار الموقع
city_choice = st.selectbox("اختر الولاية:", list(TUNISIA_CITIES.keys()))
lat, lon = TUNISIA_CITIES[city_choice]

# حساب الأوقات
calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
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
    next_p_name, next_p_time = "الفجر", datetime.strptime(times["Fajr"], "%H:%M").replace(year=now.year, month=now.month, day=now.day) + timedelta(days=1)

diff = next_p_time - now
hours, remainder = divmod(diff.seconds, 3600)
minutes, _ = divmod(remainder, 60)

# عرض العداد (ساعات ودقائق فقط للتحديث كل دقيقة)
st.markdown(f"""
    <div class="countdown-section">
        <p style='margin:0;'>بقي على صلاة {next_p_name}</p>
        <h1 style='font-size: 3.5rem; margin:0;'>{hours:02d}:{minutes:02d}</h1>
    </div>
""", unsafe_allow_html=True)

# عرض الأوقات
cols = st.columns(3)
for i, (eng, ar) in enumerate(prayers_ar.items()):
    with cols[i % 3]:
        st.markdown(f"<div class='prayer-card'><div>{ar}</div><div class='prayer-time'>{times[eng]}</div></div>", unsafe_allow_html=True)

# التحديث عند تغير الدقيقة
time.sleep(60 - now.second)
st.rerun()
