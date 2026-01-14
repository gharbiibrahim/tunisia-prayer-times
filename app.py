import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from hijri_converter import Gregorian
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌", layout="centered")

# 2. تنسيق الواجهة (RTL وتكبير الخطوط)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    
    .big-time-box {
        text-align: center;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 20px;
        border: 3px solid #d32f2f;
        margin-bottom: 25px;
    }
    .day-name { font-size: 3.5rem; font-weight: bold; color: #2c3e50; display: block; }
    .current-time { font-size: 5.5rem; font-weight: bold; color: #d32f2f; line-height: 1.1; }
    
    .date-container { font-size: 1.8rem; margin-top: 15px; color: #555; }
    .hijri-date { font-weight: bold; color: #b71c1c; }
    .gregorian-date { font-size: 1.5rem; color: #7f8c8d; }

    .prayer-card {
        background: white; padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid #eee; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .prayer-name { font-size: 1.3rem; font-weight: bold; }
    .prayer-time { font-size: 2rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 3. تحميل البيانات من الملف المرفوع
@st.cache_data
def load_full_data():
    try:
        df = pd.read_csv('nouveau 2085.txt', sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'], engine='python', encoding='utf-8')
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except:
        return pd.DataFrame(columns=['الولاية', 'المعتمدية', 'العمادة'])

df = load_full_data()

# 4. اختيار الموقع
st.title("🕌 مواقيت الصلاة في تونس")
col1, col2, col3 = st.columns(3)
with col1:
    state = st.selectbox("الولاية", ["اختر"] + sorted(df['الولاية'].unique().tolist()))
with col2:
    districts = df[df['الولاية'] == state]['المعتمدية'].unique().tolist() if state != "اختر" else []
    district = st.selectbox("المعتمدية", ["اختر"] + sorted(districts))
with col3:
    villages = df[(df['الولاية'] == state) & (df['المعتمدية'] == district)]['العمادة'].unique().tolist() if district != "اختر" else []
    village = st.selectbox("العمادة", ["اختر"] + sorted(villages))

# 5. معالجة البيانات
lat, lon = None, None
if village != "اختر":
    geolocator = Nominatim(user_agent="tunisia_prayer_final_v1")
    location = geolocator.geocode(f"{village}, {district}, {state}, Tunisia")
    if location: 
        lat, lon = location.latitude, location.longitude

if lat and lon:
    now = datetime.now()
    today = date.today()
    
    # تحويل اليوم للعربية
    days_ar = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
    day_name = days_ar[now.strftime('%A')]
    
    # التاريخ الهجري
    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    months_hijri = ["محرّم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    hijri_str = f"{hijri.day} {months_hijri[hijri.month-1]} {hijri.year} هـ"
    
    # عرض الواجهة (تم تكبير الأحجام بناءً على طلبك)
    st.markdown(f"""
        <div class="big-time-box">
            <span class="day-name">{day_name}</span>
            <span class="current-time">{now.strftime('%H:%M')}</span>
            <div class="date-container">
                <div class="hijri-date">{hijri_str}</div>
                <div class="gregorian-date">{today.strftime('%d / %m / %Y')} م</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # حساب المواقيت
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
    times = calc.fetch_prayer_times()
    
    def adjust(t, m): return (datetime.strptime(t, "%H:%M") + timedelta(minutes=m)).strftime("%H:%M")
    
    prayers = {
        "الفجر": times["Fajr"], "الشروق": times["Sunrise"],
        "الظهر": adjust(times["Dhuhr"], 7), "العصر": times["Asr"],
        "المغرب": adjust(times["Maghrib"], 2), "العشاء": times["Isha"]
    }

    # عرض جدول الصلوات
    cols = st.columns(3)
    for i, (name, time_val) in enumerate(prayers.items()):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="prayer-card">
                    <div class="prayer-name">{name}</div>
                    <div class="prayer-time">{time_val}</div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("الرجاء تحديد الموقع من القوائم أعلاه.")
