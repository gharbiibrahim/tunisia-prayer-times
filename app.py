import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
import time
import base64

# إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة في تونس", page_icon="🕌", layout="centered")

# دالة لتشغيل صوت الأذان
def play_adhan():
    # رابط صوت أذان (يمكنك استبداله برابط مباشر لملف mp3)
    adhan_url = "https://www.islamcan.com/adhan/duas/adhan-makkah.mp3"
    audio_html = f"""
        <audio autoplay>
            <source src="{adhan_url}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# تنسيق RTL والجمالية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] {
        direction: RTL; text-align: right; font-family: 'Cairo', sans-serif;
    }
    .countdown-section {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white; padding: 30px; border-radius: 20px;
        text-align: center; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .prayer-card {
        background: white; padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid #eee; margin-bottom: 15px;
    }
    .prayer-time { font-size: 1.6rem; font-weight: bold; color: #1a237e; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕌 مواقيت الصلاة في تونس")

# تفعيل الصوت
enable_sound = st.checkbox("🔔 تفعيل صوت الأذان عند دخول الوقت")

# الموقع
place = st.text_input("📍 أدخل المدينة أو المعتمدية:", "ماطر")
geolocator = Nominatim(user_agent="tunisia_prayer_final")
location = geolocator.geocode(place + ", Tunisia")

if location:
    calc = PrayerTimesCalculator(
        latitude=location.latitude, longitude=location.longitude,
        calculation_method="mwl", date=str(date.today())
    )
    times = calc.fetch_prayer_times()
    prayers_ar = {"Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}

    # --- منطق العداد ---
    now = datetime.now()
    next_p_name = ""
    next_p_time = None

    for eng, ar in prayers_ar.items():
        p_time = datetime.strptime(times[eng], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        if p_time > now:
            next_p_name = ar
            next_p_time = p_time
            break
    
    if not next_p_time:
        next_p_name = "الفجر"
        next_p_time = datetime.strptime(times["Fajr"], "%H:%M").replace(year=now.year, month=now.month, day=now.day) + timedelta(days=1)

    # حساب الفرق
    diff = next_p_time - now
    total_seconds = int(diff.total_seconds())
    
    # تشغيل الأذان إذا حان الوقت
    if total_seconds <= 1 and enable_sound:
        play_adhan()
        st.balloons()
        st.success(f"حان الآن موعد صلاة {next_p_name}")

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # عرض العداد
    st.markdown(f"""
        <div class="countdown-section">
            <p style='font-size: 1.2rem;'>الوقت المتبقي لصلاة {next_p_name}</p>
            <h1 style='font-size: 4.5rem; margin: 0;'>{hours:02d}:{minutes:02d}:{seconds:02d}</h1>
        </div>
    """, unsafe_allow_html=True)

    # عرض جدول الأوقات
    cols = st.columns(3)
    p_items = list(prayers_ar.items())
    for i, (eng, ar) in enumerate(p_items):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="prayer-card">
                    <div style='color: #666;'>{ar}</div>
                    <div class="prayer-time">{times[eng]}</div>
                </div>
            """, unsafe_allow_html=True)

    # تحديث كل ثانية
    time.sleep(1)
    st.rerun()
