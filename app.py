import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from hijri_converter import Gregorian
from streamlit_js_eval import streamlit_js_eval
import time
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة بتونس الشاملة", page_icon="🕌", layout="centered")

# 2. تنسيق الواجهة RTL (من اليمين لليسار) بألوان تونسية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .stSelectbox label, .stTextInput label { font-size: 1.1rem !important; font-weight: bold; color: #d32f2f; }
    .current-time-box { background-color: #f8f9fa; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #d32f2f; margin-bottom: 20px; }
    .countdown-section { background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); color: white; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3); }
    .prayer-card { background: white; padding: 12px; border-radius: 12px; text-align: center; border: 1px solid #eee; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .prayer-time { font-size: 1.5rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 3. دالة تحميل البيانات من الملف المرفوع
@st.cache_data
def load_full_data():
    try:
        # قراءة الملف الذي قدمته 'nouveau 2085.txt'
        df = pd.read_csv('nouveau 2085.txt', sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'], engine='python', encoding='utf-8')
        # تنظيف البيانات من المسافات الزائدة
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except:
        st.error("يرجى التأكد من وجود ملف 'nouveau 2085.txt' في نفس المجلد.")
        return pd.DataFrame(columns=['الولاية', 'المعتمدية', 'العمادة'])

df = load_full_data()

st.title("🇹🇳 مواقيت الصلاة في تونس")

# 4. اختيار الموقع (هرمي حسب الملف)
st.subheader("📍 تحديد الموقع بدقة")
col1, col2, col3 = st.columns(3)

with col1:
    state = st.selectbox("1. الولاية", ["اختر"] + sorted(df['الولاية'].unique().tolist()))

with col2:
    districts = df[df['الولاية'] == state]['المعتمدية'].unique().tolist() if state != "اختر" else []
    district = st.selectbox("2. المعتمدية", ["اختر"] + sorted(districts))

with col3:
    villages = df[(df['الولاية'] == state) & (df['المعتمدية'] == district)]['العمادة'].unique().tolist() if district != "اختر" else []
    village = st.selectbox("3. العمادة", ["اختر"] + sorted(villages))

street = st.text_input("4. الحي أو النهج (اختياري):", placeholder="مثال: نهج ابن خلدون")

# زر GPS كخيار بديل
if st.button("🌐 أو استعمل GPS لجلب موقعي الحالي"):
    loc = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition(pos => {return [pos.coords.latitude, pos.coords.longitude]})', key='gps')
    if loc: st.session_state.lat, st.session_state.lon = loc[0], loc[1]

# 5. معالجة الإحداثيات والحسابات
lat, lon = st.session_state.get('lat'), st.session_state.get('lon')

if not lat and village != "اختر":
    with st.spinner('جاري تحديد الإحداثيات...'):
        geolocator = Nominatim(user_agent="tunisia_prayer_pro_2026")
        query = f"{street}, {village}, {district}, {state}, Tunisia" if street else f"{village}, {district}, {state}, Tunisia"
        location = geolocator.geocode(query)
        if location:
            lat, lon = location.latitude, location.longitude
        else:
            # محاولة أخيرة بالمعتمدية فقط إذا فشل البحث التفصيلي
            location = geolocator.geocode(f"{district}, {state}, Tunisia")
            if location: lat, lon = location.latitude, location.longitude

if lat and lon:
    now = datetime.now()
    today = date.today()
    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    months_ar = ["محرّم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

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

    # عرض الوقت الحالي والتاريخ
    st.markdown(f"""
        <div class="current-time-box">
            <span style='color: #555;'>الوقت الحالي: <b>{now.strftime('%H:%M')}</b></span><br>
            <span style='color: #d32f2f; font-weight: bold;'>{hijri.day} {months_ar[hijri.month-1]} {hijri.year} هـ</span>
        </div>
    """, unsafe_allow_html=True)

    # حساب الصلاة القادمة والعداد (ساعات:دقائق)
    prayers_ar = {"Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}
    next_p_name, next_p_time = "الفجر", datetime.strptime(adj_times["Fajr"], "%H:%M").replace(year=now.year, month=now.month, day=now.day) + timedelta(days=1)
    
    for eng, ar in prayers_ar.items():
        p_t = datetime.strptime(adj_times[eng], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        if p_t > now:
            next_p_name, next_p_time = ar, p_t
            break

    diff = next_p_time - now
    h, m = divmod(diff.seconds // 60, 60)

    st.markdown(f"""
        <div class="countdown-section">
            <p style='margin:0;'>المتبقي لصلاة {next_p_name}</p>
            <h1 style='font-size: 3.5rem; margin:0;'>{h:02d}:{m:02d}</h1>
        </div>
    """, unsafe_allow_html=True)

    # عرض الجدول
    cols = st.columns(3)
    for i, (eng, ar) in enumerate(prayers_ar.items()):
        with cols[i % 3]:
            st.markdown(f"<div class='prayer-card'>{ar}<br><span class='prayer-time'>{adj_times[eng]}</span></div>", unsafe_allow_html=True)

    # التحديث كل دقيقة
    time.sleep(60 - now.second)
    st.rerun()
else:
    st.info("👈 يرجى اختيار المنطقة من القوائم أعلاه لعرض المواقيت.")
