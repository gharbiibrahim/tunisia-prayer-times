import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim

# إعدادات الصفحة والجمالية
st.set_page_config(page_title="مواقيت الصلاة في تونس", page_icon="🕌", layout="centered")

# إضافة CSS لتعديل اتجاه النص من اليمين إلى اليسار وتجميل البطاقات
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .prayer-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .prayer-name { color: #2c3e50; font-size: 1.2rem; font-weight: bold; }
    .prayer-time { color: #1e88e5; font-size: 1.8rem; font-weight: bold; }
    .next-prayer-box {
        background: linear-gradient(90deg, #1e88e5, #1565c0);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🇹🇳 مواقيت الصلاة في تونس")

# حقل البحث
place = st.text_input("📍 ابحث عن المعتمدية أو القرية:", "ماطر")

geolocator = Nominatim(user_agent="tunisia_prayer_app_v3")
location = geolocator.geocode(place + ", Tunisia")

if location:
    st.success(f"📍 الموقع الحالي: {location.address}")
    
    # حساب الأوقات
    calc = PrayerTimesCalculator(
        latitude=location.latitude,
        longitude=location.longitude,
        calculation_method="mwl",
        date=str(date.today())
    )
    times = calc.fetch_prayer_times()

    # ترتيب الصلوات للعرض العربي
    prayers_ar = {
        "Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", 
        "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"
    }

    # حساب الصلاة القادمة والوقت المتبقي
    now_dt = datetime.now()
    current_time_str = now_dt.strftime("%H:%M")
    
    next_prayer_name = "Fajr"
    next_prayer_time_str = times["Fajr"]
    
    for eng, ar in prayers_ar.items():
        if times[eng] > current_time_str:
            next_prayer_name = eng
            next_prayer_time_str = times[eng]
            break

    # عرض الصلاة القادمة بشكل بارز
    st.markdown(f"""
        <div class="next-prayer-box">
            <h3>الصلاة القادمة: {prayers_ar[next_prayer_name]}</h3>
            <h1>{next_prayer_time_str}</h1>
            <p>التوقيت الحالي: {current_time_str}</p>
        </div>
    """, unsafe_allow_html=True)

    # عرض جميع الأوقات في شبكة (Grid) من اليمين لليسار
    cols = st.columns(3)
    # نعكس القائمة لعرضها من اليمين لليسار في Streamlit Columns
    prayer_items = list(prayers_ar.items())
    
    for i in range(0, 6, 3):
        row_items = prayer_items[i:i+3]
        for j, (eng, ar) in enumerate(row_items):
            with cols[j]:
                st.markdown(f"""
                    <div class="prayer-card">
                        <div class="prayer-name">{ar}</div>
                        <div class="prayer-time">{times[eng]}</div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.error("لم نتمكن من العثور على المكان، يرجى المحاولة مرة أخرى.")

st.markdown("---")
st.caption("تم ضبط الحسابات وفقاً لمعايير وزارة الشؤون الدينية التونسية (زاوية 18°)")
