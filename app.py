import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from hijri_converter import Gregorian
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="مواقيت الصلاة الرسمية بتونس", page_icon="🕌", layout="centered")

# 2. إحداثيات الولايات التونسية (ثابتة لضمان عمل التطبيق دائماً)
TUNISIA_COORDS = {
    "تونس": (36.8065, 10.1815), "بنزرت": (37.2744, 9.8739), "أريانة": (36.8665, 10.1647),
    "بن عروس": (36.7531, 10.2222), "منوبة": (36.8078, 10.0863), "نابل": (36.4561, 10.7376),
    "زغوان": (36.4029, 10.1429), "باجة": (36.7256, 9.1906), "جندوبة": (36.5011, 8.7802),
    "الكاف": (36.1822, 8.7148), "سليانة": (36.0840, 9.3708), "سوسة": (35.8256, 10.6084),
    "المنستير": (35.7780, 10.8262), "المهدية": (35.5047, 11.0622), "القيروان": (35.6781, 10.0963),
    "سيدي بوزيد": (35.0382, 9.4849), "القصرين": (35.1676, 8.8365), "صفاقس": (34.7400, 10.7600),
    "قفصة": (34.4250, 8.7842), "توزر": (33.9197, 8.1335), "قبلي": (33.7050, 8.9714),
    "قابس": (33.8815, 10.0982), "مدنين": (33.3550, 10.4922), "تطاوين": (32.9297, 10.4518)
}

# 3. التنسيق الجمالي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .big-time-box { text-align: center; padding: 25px; background-color: #f8f9fa; border-radius: 20px; border: 3px solid #d32f2f; margin-bottom: 25px; }
    .day-name { font-size: 3.5rem; font-weight: bold; color: #2c3e50; display: block; }
    .current-time { font-size: 6rem; font-weight: bold; color: #d32f2f; line-height: 1.1; }
    .date-container { font-size: 1.8rem; margin-top: 15px; color: #555; }
    .hijri-date { font-weight: bold; color: #b71c1c; }
    .gregorian-date { font-size: 1.5rem; color: #7f8c8d; }
    .prayer-card { background: white; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .prayer-name { font-size: 1.4rem; font-weight: bold; }
    .prayer-time { font-size: 2.2rem; font-weight: bold; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 4. تحميل البيانات من ملفك
@st.cache_data
def load_full_data():
    try:
        df = pd.read_csv('nouveau 2085.txt', sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'], engine='python', encoding='utf-8')
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception:
        return pd.DataFrame(columns=['الولاية', 'المعتمدية', 'العمادة'])

df = load_full_data()

# 5. اختيار الموقع
st.title("🕌 مواقيت الصلاة بتونس")
col1, col2, col3 = st.columns(3)
with col1:
    state = st.selectbox("الولاية", ["اختر"] + sorted(df['الولاية'].unique().tolist()))
with col2:
    districts = df[df['الولاية'] == state]['المعتمدية'].unique().tolist() if state != "اختر" else []
    district = st.selectbox("المعتمدية", ["اختر"] + sorted(districts))
with col3:
    villages = df[(df['الولاية'] == state) & (df['المعتمدية'] == district)]['العمادة'].unique().tolist() if district != "اختر" else []
    village = st.selectbox("العمادة", ["اختر"] + sorted(villages))

# تحديد الإحداثيات من القاموس الداخلي (بدون Geopy لتفادي الخطأ)
lat, lon = None, None
if state in TUNISIA_COORDS:
    lat, lon = TUNISIA_COORDS[state]

if lat and lon and state != "اختر":
    now = datetime.now()
    today = date.today()
    
    # تحويل اليوم والتاريخ
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

    # الحساب (زاوية 18 درجة)
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
    times = calc.fetch_prayer_times()
    
    def adjust(t, m): return (datetime.strptime(t, "%H:%M") + timedelta(minutes=m)).strftime("%H:%M")
    
    # المعايير الرسمية (7 دقائق للظهر، 2 للمغرب، و6 دقائق إضافية للعشاء لمطابقة زاوية 18)
    prayers = {
        "الفجر": times["Fajr"],
        "الشروق": times["Sunrise"],
        "الظهر": adjust(times["Dhuhr"], 7),
        "العصر": times["Asr"],
        "المغرب": adjust(times["Maghrib"], 2),
        "العشاء": adjust(times["Isha"], 6)
    }

    cols = st.columns(3)
    for i, (name, time_val) in enumerate(prayers.items()):
        with cols[i % 3]:
            st.markdown(f"""<div class="prayer-card"><div class="prayer-name">{name}</div><div class="prayer-time">{time_val}</div></div>""", unsafe_allow_html=True)
else:
    st.info("الرجاء اختيار الولاية لعرض المواقيت.")
