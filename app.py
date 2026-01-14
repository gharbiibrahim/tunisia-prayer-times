import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from hijri_converter import Gregorian

# 1. إعدادات الصفحة والتصميم (Style)
st.set_page_config(page_title="مواقيت الصلاة في تونس - الأسماء الرسمية", page_icon="🕌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .main-card { text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 15px; border-right: 8px solid #d32f2f; margin-bottom: 20px; }
    .time-now { font-size: 5rem; font-weight: bold; color: #d32f2f; }
    .prayer-row { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px; }
    .prayer-box { background: white; padding: 15px; border-radius: 10px; text-align: center; width: 130px; border: 1px solid #ddd; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .p-name { font-weight: bold; color: #333; font-size: 1.1rem; }
    .p-time { font-size: 1.6rem; color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. وظيفة تحميل وتصحيح الأسماء
@st.cache_data
def load_official_data():
    try:
        # قراءة البيانات مع معالجة المسافات والترميز لضمان مطابقة الملفات المرفوعة
        df = pd.read_csv('nouveau 2085.txt', sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'], engine='python', encoding='utf-8')
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip() # تنظيف الفراغات تماماً
        return df
    except Exception as e:
        st.error(f"حدث خطأ في قراءة ملف الأسماء: {e}")
        return pd.DataFrame()

df_data = load_official_data()

# إحداثيات الولايات (المرجع الجغرافي)
COORDS = {
    "تونس": (36.8065, 10.1815), "بنزرت": (37.2744, 9.8739), "أريانة": (36.8665, 10.1647),
    "بن عروس": (36.7531, 10.2222), "منوبة": (36.8078, 10.0863), "نابل": (36.4561, 10.7376),
    "زغوان": (36.4029, 10.1429), "باجة": (36.7256, 9.1906), "جندوبة": (36.5011, 8.7802),
    "الكاف": (36.1822, 8.7148), "سليانة": (36.0840, 9.3708), "سوسة": (35.8256, 10.6084),
    "المنستير": (35.7780, 10.8262), "المهدية": (35.5047, 11.0622), "القيروان": (35.6781, 10.0963),
    "سيدي بوزيد": (35.0382, 9.4849), "القصرين": (35.1676, 8.8365), "صفاقس": (34.7400, 10.7600),
    "قفصة": (34.4250, 8.7842), "توزر": (33.9197, 8.1335), "قبلي": (33.7050, 8.9714),
    "قابس": (33.8815, 10.0982), "مدنين": (33.3550, 10.4922), "تطاوين": (32.9297, 10.4518)
}

# 3. واجهة اختيار الموقع (الهرمية)
st.title("🕌 مواقيت الصلاة بتونس")

col_state, col_dist, col_vill = st.columns(3)

with col_state:
    states = sorted(df_data['الولاية'].unique().tolist()) if not df_data.empty else []
    selected_state = st.selectbox("الولاية", ["اختر الولاية"] + states)

with col_dist:
    districts = sorted(df_data[df_data['الولاية'] == selected_state]['المعتمدية'].unique().tolist()) if selected_state != "اختر الولاية" else []
    selected_district = st.selectbox("المعتمدية", ["اختر المعتمدية"] + districts)

with col_vill:
    villages = sorted(df_data[(df_data['الولاية'] == selected_state) & (df_data['المعتمدية'] == selected_district)]['العمادة'].unique().tolist()) if selected_district != "اختر المعتمدية" else []
    selected_village = st.selectbox("العمادة", ["اختر العمادة"] + villages)

# 4. الحساب والعرض
if selected_state in COORDS and selected_village != "اختر العمادة":
    lat, lon = COORDS[selected_state]
    today = date.today()
    now = datetime.now()
    
    # حساب المواقيت (زاوية 18 + التعديلات التونسية)
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(today))
    times = calc.fetch_prayer_times()
    
    def adjust(t, mins): return (datetime.strptime(t, "%H:%M") + timedelta(minutes=mins)).strftime("%H:%M")

    prayer_schedule = {
        "الفجر": times["Fajr"],
        "الشروق": times["Sunrise"],
        "الظهر": adjust(times["Dhuhr"], 7),
        "العصر": times["Asr"],
        "المغرب": adjust(times["Maghrib"], 2),
        "العشاء": adjust(times["Isha"], 6)
    }

    # التاريخ الهجري
    h = Gregorian(today.year, today.month, today.day).to_hijri()
    
    # العرض الرئيسي
    st.markdown(f"""
        <div class="main-card">
            <h3>{selected_state} - {selected_district} - {selected_village}</h3>
            <div class="time-now">{now.strftime('%H:%M')}</div>
            <p>{today.strftime('%d / %m / %Y')} م | {h.day} {h.month_name()} {h.year} هـ</p>
        </div>
    """, unsafe_allow_html=True)

    # عرض كروت الصلوات
    st.markdown('<div class="prayer-row">', unsafe_allow_html=True)
    cols = st.columns(6)
    for i, (name, val) in enumerate(prayer_schedule.items()):
        with cols[i]:
            st.markdown(f"""
                <div class="prayer-box">
                    <div class="p-name">{name}</div>
                    <div class="p-time">{val}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # مشاركة واتساب
    share_msg = f"مواقيت الصلاة لليوم في {selected_village}:\n" + "\n".join([f"{k}: {v}" for k, v in prayer_schedule.items()])
    wa_link = f"https://wa.me/?text={share_msg.replace(' ', '%20').replace(':', '%3A')}"
    st.markdown(f'<br><a href="{wa_link}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold;">🟢 مشاركة التوقيت عبر واتساب</button></a>', unsafe_allow_html=True)
else:
    st.info("الرجاء اختيار الولاية ثم المعتمدية والعمادة للحصول على المواقيت الصحيحة.")
