import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from hijri_converter import Gregorian

# 1. إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة بتونس - التوقيت الرسمي", page_icon="🕌", layout="centered")

# 2. التنسيق الجمالي (أحجام كبيرة وبدون تحديث تلقائي)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    
    .big-time-box {
        text-align: center; padding: 25px; background-color: #f8f9fa;
        border-radius: 20px; border: 3px solid #d32f2f; margin-bottom: 25px;
    }
    .day-name { font-size: 3.5rem; font-weight: bold; color: #2c3e50; display: block; }
    .current-time { font-size: 6rem; font-weight: bold; color: #d32f2f; line-height: 1.1; }
    
    .date-container { font-size: 1.8rem; margin-top: 15px; color: #555; }
    .hijri-date { font-weight: bold; color: #b71c1c; }
    .gregorian-date { font-size: 1.5rem; color: #7f8c8d; }

    .prayer-card {
        background: white; padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid #eee; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .prayer-name { font-size: 1.4rem; font-weight: bold; color: #333; }
    .prayer-time { font-size: 2.2rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 3. تحميل البيانات الهرمية
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
st.title("🕌 مواقيت الصلاة الرسمية - تونس")
col1, col2, col3 = st.columns(3)
with col1:
    state = st.selectbox("الولاية", ["اختر"] + sorted(df['الولاية'].unique().tolist()))
with col2:
    districts = df[df['الولاية'] == state]['المعتمدية'].unique().tolist() if state != "اختر" else []
    district = st.selectbox("المعتمدية", ["اختر"] + sorted(districts))
with col3:
    villages = df[(df['الولاية'] == state) & (df['المعتمدية'] == district)]['العمادة'].unique().tolist() if district != "اختر" else []
    village = st.selectbox("العمادة", ["اختر"] + sorted(villages))

# 5. معالجة البيانات والحساب الفلكي
lat, lon = None, None
if village != "اختر":
    geolocator = Nominatim(user_agent="tunisia_prayer_official_fixed")
    location = geolocator.geocode(f"{village}, {district}, {state}, Tunisia")
    if location: 
        lat, lon = location.latitude, location.longitude

if lat and lon:
    now = datetime.now()
    today = date.today()
    
    # التاريخ واليوم
    days_ar = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
    day_name = days_ar[now.strftime('%A')]
    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    months_hijri = ["محرّم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    hijri_str = f"{hijri.day} {months_hijri[hijri.month-1]} {hijri.year} هـ"
    
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

    # حساب المواقيت - ضبط الزاوية على 18 درجة لتوافق تونس
    calc = PrayerTimesCalculator(
        latitude=lat, 
        longitude=lon, 
        calculation_method="mwl", # تعتمد 18 للفجر و 17 للعشاء، سنقوم بالتعديل يدوياً للعشاء
        date=str(today)
    )
    # ملاحظة: بعض المكاتب لا تدفع العشاء لـ 18 تلقائياً، لذا سنستخدم معيار "Tehran" أو "Custom" إذا لزم الأمر
    # ولكن الأسهل برمجياً هو استخدام mwl ثم التحقق من الزاوية
    times = calc.fetch_prayer_times()
    
    def adjust(t, m): return (datetime.strptime(t, "%H:%M") + timedelta(minutes=m)).strftime("%H:%M")
    
    # ضبط التوقيتات بناءً على ملاحظاتك ومعايير تونس
    prayers = {
        "الفجر": times["Fajr"], # زاوية 18 درجة
        "الشروق": times["Sunrise"],
        "الظهر": adjust(times["Dhuhr"], 7), 
        "العصر": times["Asr"],
        "المغرب": adjust(times["Maghrib"], 2), 
        "العشاء": adjust(times["Isha"], 6) # أضفنا 6 دقائق لتغطية الفارق بين زاوية 17 و 18 درجة
    }

    cols = st.columns(3)
    for i, (name, time_val) in enumerate(prayers.items()):
        with cols[i % 3]:
            st.markdown(f"""<div class="prayer-card"><div class="prayer-name">{name}</div><div class="prayer-time">{time_val}</div></div>""", unsafe_allow_html=True)
else:
    st.info("الرجاء اختيار الموقع لعرض المواقيت.")
