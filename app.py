import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from hijri_converter import Gregorian
from streamlit_js_eval import streamlit_js_eval
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة - تونس الشاملة", page_icon="🕌", layout="centered")

# 2. قاعدة بيانات الولايات الرئيسية
TUNISIA_STATES = ["تونس", "بنزرت", "أريانة", "منوبة", "بن عروس", "نابل", "باجة", "جندوبة", "الكاف", "سليانة", "سوسة", "المنستير", "المهدية", "القيروان", "سيدي بوزيد", "القصرين", "صفاقس", "قفصة", "توزر", "قبلي", "قابس", "مدنين", "تطاوين", "زغوان"]

# 3. تنسيق الواجهة RTL
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #d32f2f; color: white; }
    .current-time-box { background-color: #f1f3f4; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #d32f2f; }
    .countdown-section { background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); color: white; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 20px; }
    .prayer-card { background: white; padding: 10px; border-radius: 12px; text-align: center; border: 1px solid #eee; margin-bottom: 8px; }
    .prayer-time { font-size: 1.4rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇹🇳 مواقيت الصلاة في تونس")

# 4. جلب الموقع (GPS أو يدوي)
lat, lon, address = None, None, "لم يتم تحديد موقع"

st.subheader("📍 تحديد الموقع بدقة")
col_gps, col_manual = st.columns([1, 2])

with col_gps:
    if st.button("🌐 استعمل GPS"):
        loc = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition(pos => {return [pos.coords.latitude, pos.coords.longitude]})', key='get_location')
        if loc:
            lat, lon = loc[0], loc[1]
            address = "تم تحديد موقعك عبر GPS"

with col_manual:
    state = st.selectbox("اختر الولاية:", [""] + TUNISIA_STATES)
    detail = st.text_input("المعتمدية، العمادة، الحي أو النهج:", placeholder="مثال: نهج ابن خلدون، ماطر")

if not lat and state:
    with st.spinner('جاري تحديد الإحداثيات...'):
        try:
            geolocator = Nominatim(user_agent="tunisia_prayer_2026_pro")
            query = f"{detail}, {state}, Tunisia" if detail else f"{state}, Tunisia"
            location = geolocator.geocode(query, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
                address = location.address
            else:
                st.error("لم نجد هذا العنوان بدقة، حاول كتابة الاسم بشكل أوضح.")
        except:
            st.error("خطأ في الاتصال بخدمة الخرائط.")

# 5. عرض البيانات إذا توفر الموقع
if lat and lon:
    now = datetime.now()
    today = date.today()
    
    # التاريخ الهجري
    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    months_ar = ["محرّم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

    st.info(f"📍 الموقع المحدد: {address}")

    # حساب الأوقات
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
    raw_times = calc.fetch_prayer_times()

    # التعديلات الشرعية (7 دقائق للظهر، 2 للمغرب)
    def adjust(t_str, m):
        return (datetime.strptime(t_str, "%H:%M") + timedelta(minutes=m)).strftime("%H:%M")

    adj_times = {
        "Fajr": raw_times["Fajr"], "Sunrise": raw_times["Sunrise"],
        "Dhuhr": adjust(raw_times["Dhuhr"], 7), "Asr": raw_times["Asr"],
        "Maghrib": adjust(raw_times["Maghrib"], 2), "Isha": raw_times["Isha"]
    }
    prayers_ar = {"Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}

    # العداد والوقت الحالي
    st.markdown(f"<div class='current-time-box'>الوقت الحالي الآن: <b>{now.strftime('%H:%M')}</b><br><small>{hijri.day} {months_ar[hijri.month-1]} {hijri.year} هـ</small></div>", unsafe_allow_html=True)

    # حساب الصلاة القادمة
    next_p_name, next_p_time = "الفجر", datetime.strptime(adj_times["Fajr"], "%H:%M").replace(year=now.year, month=now.month, day=now.day) + timedelta(days=1)
    for eng, ar in prayers_ar.items():
        p_t = datetime.strptime(adj_times[eng], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        if p_t > now:
            next_p_name, next_p_time = ar, p_t
            break

    diff = next_p_time - now
    h, m = divmod(diff.seconds // 60, 60)
    st.markdown(f"<div class='countdown-section'>بقي على صلاة {next_p_name}<br><h1 style='margin:0;'>{h:02d}:{m:02d}</h1></div>", unsafe_allow_html=True)

    # عرض الجدول
    cols = st.columns(3)
    for i, (eng, ar) in enumerate(prayers_ar.items()):
        with cols[i % 3]:
            st.markdown(f"<div class='prayer-card'>{ar}<br><span class='prayer-time'>{adj_times[eng]}</span></div>", unsafe_allow_html=True)

    time.sleep(60 - now.second)
    st.rerun()
else:
    st.write("👈 يرجى اختيار الولاية وكتابة المعتمدية/الحي أو الضغط على زر GPS للبدء.")
