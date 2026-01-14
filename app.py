import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
import time

st.set_page_config(page_title="مواقيت الصلاة في تونس", page_icon="🕌", layout="centered")

# تحسين المظهر ودعم RTL
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] {
        direction: RTL; text-align: right; font-family: 'Cairo', sans-serif;
    }
    .countdown-box {
        background: #1e88e5; color: white; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .prayer-card {
        background: white; border-radius: 12px; padding: 15px;
        text-align: center; border: 1px solid #eee; margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🇹🇳 أوقات الصلاة بتونس")

place = st.text_input("📍 أدخل المكان (مدينة، معتمدية، قرية):", "ماطر")
geolocator = Nominatim(user_agent="tunisia_prayer_app_v4")
location = geolocator.geocode(place + ", Tunisia")

if location:
    calc = PrayerTimesCalculator(
        latitude=location.latitude, longitude=location.longitude,
        calculation_method="mwl", date=str(date.today())
    )
    times = calc.fetch_prayer_times()
    prayers_ar = {"Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}

    # --- منطق العداد التنازلي ---
    now = datetime.now()
    next_p_name = ""
    next_p_time = None

    for eng, ar in prayers_ar.items():
        p_time = datetime.strptime(times[eng], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        if p_time > now:
            next_p_name = ar
            next_p_time = p_time
            break
    
    # إذا انتهت صلوات اليوم، الصلاة القادمة هي فجر الغد
    if not next_p_time:
        next_p_name = "الفجر"
        next_p_time = datetime.strptime(times["Fajr"], "%H:%M").replace(year=now.year, month=now.month, day=now.day) + timedelta(days=1)

    # حساب الفرق الزمني للعداد
    diff = next_p_time - now
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # عرض العداد التنازلي
    st.markdown(f"""
        <div class="countdown-box">
            <h4>بقي على صلاة {next_p_name}</h4>
            <h1 style='font-size: 3rem;'>{hours:02d}:{minutes:02d}:{seconds:02d}</h1>
        </div>
    """, unsafe_allow_html=True)

    # عرض بقية الأوقات
    cols = st.columns(3)
    p_list = list(prayers_ar.items())
    for i, (eng, ar) in enumerate(p_list):
        with cols[i % 3]:
            st.markdown(f"""<div class="prayer-card"><b>{ar}</b><br><span style='font-size:1.5rem;'>{times[eng]}</span></div>""", unsafe_allow_html=True)

    # تحديث الصفحة تلقائياً كل دقيقة ليبقى العداد دقيقاً
    time.sleep(1)
    st.rerun()

else:
    st.error("الموقع غير معروف.")
