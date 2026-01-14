import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from hijri_converter import Gregorian
from streamlit_js_eval import streamlit_js_eval
import time
import io

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="مواقيت الصلاة في تونس - النسخة الشاملة", page_icon="🕌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .stButton>button { width: 100%; border-radius: 12px; background-color: #d32f2f; color: white; font-weight: bold; }
    .current-time-box { background-color: #f8f9fa; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #d32f2f; margin-bottom: 20px; }
    .countdown-section { background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); color: white; padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3); }
    .prayer-card { background: white; padding: 12px; border-radius: 12px; text-align: center; border: 1px solid #eee; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .prayer-time { font-size: 1.4rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 2. تحميل ومعالجة بيانات تونس (من الملف المرفوع)
@st.cache_data
def load_tunisia_data():
    # بيانات الولايات والمعتمديات والعمادات المستخرجة 
    data = """تونس	قرطاج	سيدي بوسعيد
تونس	المدينة	المدينة
تونس	باب البحر	بحيرة تونس
أريانة	سكرة	دار فضال
بنزرت	ماطر	ماطر المدينة
بنزرت	بنزرت الشمالية	الكورنيش
باجة	مجاز الباب	مجاز الباب المدينة
نابل	الحمامات	ياسمين الحمامات""" 
    # ملاحظة: الكود الفعلي سيقرأ كامل الملف المرفوع 'nouveau 2085.txt'
    # هنا محاكاة للهيكل التنظيمي 
    df = pd.read_csv(io.StringIO(data), sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'])
    return df

df_tunisia = load_tunisia_data()

st.title("🕌 مواقيت الصلاة في تونس")

# 3. نظام تحديد الموقع (GPS أو يدوي هرمي)
st.subheader("📍 تحديد الموقع")
lat, lon, final_address = None, None, ""

tab1, tab2 = st.tabs(["🌐 نظام تحديد الموقع العالمي (GPS)", "📝 اختيار يدوي (ولاية/معتمدية/عمادة)"])

with tab1:
    if st.button("تحديد موقعي الآن"):
        loc = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition(pos => {return [pos.coords.latitude, pos.coords.longitude]})', key='gps_loc')
        if loc:
            lat, lon = loc[0], loc[1]
            final_address = "موقعك الحالي عبر GPS"

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        state = st.selectbox("الولاية", ["اختر"] + sorted(df_tunisia['الولاية'].unique().tolist()))
    with col2:
        districts = df_tunisia[df_tunisia['الولاية'] == state]['المعتمدية'].unique().tolist() if state != "اختر" else []
        district = st.selectbox("المعتمدية", ["اختر"] + sorted(districts))
    with col3:
        villages = df_tunisia[(df_tunisia['الولاية'] == state) & (df_tunisia['المعتمدية'] == district)]['العمادة'].unique().tolist() if district != "اختر" else []
        village = st.selectbox("العمادة/الحي", ["اختر"] + sorted(villages))
    
    street = st.text_input("النهج / الشارع (اختياري):", placeholder="مثال: نهج الحبيب بورقيبة")

    if not lat and state != "اختر":
        with st.spinner('جاري جلب الإحداثيات...'):
            geolocator = Nominatim(user_agent="tunisia_prayer_app_v2")
            query = f"{street}, {village}, {district}, {state}, Tunisia"
            location = geolocator.geocode(query)
            if location:
                lat, lon = location.latitude, location.longitude
                final_address = location.address

# 4. الحسابات والعرض
if lat and lon:
    now = datetime.now()
    today = date.today()
    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    
    # حساب المواقيت
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
    times = calc.fetch_prayer_times()

    # التعديلات الشرعية المطلوبة
    def adjust_time(t_str, delta_min):
        return (datetime.strptime(t_str, "%H:%M") + timedelta(minutes=delta_min)).strftime("%H:%M")

    adj_times = {
        "Fajr": times["Fajr"], "Sunrise": times["Sunrise"],
        "Dhuhr": adjust_time(times["Dhuhr"], 7),  # +7 دقائق للظهر
        "Asr": times["Asr"],
        "Maghrib": adjust_time(times["Maghrib"], 2), # +2 دقائق للمغرب
        "Isha": times["Isha"]
    }

    # عرض الوقت الحالي والتاريخ الهجري
    st.markdown(f"""
        <div class="current-time-box">
            <div style="font-size: 0.9rem; color: #666;">{final_address}</div>
            <div style="font-size: 2.2rem; font-weight: bold; color: #d32f2f;">{now.strftime('%H:%M')}</div>
            <div style="font-size: 1rem;">{hijri.day} {hijri.month_name()} {hijri.year} هـ</div>
        </div>
    """, unsafe_allow_html=True)

    # حساب الصلاة القادمة والعداد
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
            <p style='margin:0; opacity: 0.9;'>المتبقي لصلاة {next_p_name}</p>
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
    st.warning("⚠️ الرجاء تفعيل GPS أو اختيار الموقع من القوائم لعرض المواقيت.")
