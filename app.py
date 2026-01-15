import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌", layout="wide")

# --- CSS لدعم اليمين إلى اليسار والجمالية ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Amiri:wght@700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .info-box {
        background: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border-right: 5px solid #d4af37;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .prayer-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border-bottom: 5px solid #d4af37;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .prayer-time { font-size: 1.8rem; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- عرض التاريخ والوقت ---
today = date.today()
hijri = HijriDate.get_hijri_date(today)
current_time = datetime.now().strftime("%H:%M")

st.markdown(f"""
    <div class="main-header">
        <h1 style='font-family: Amiri; margin:0;'>🕌 مواقيت الصلاة بتونس</h1>
        <p style='font-size: 1.2rem; opacity: 0.9;'>
            {today.strftime('%A')} : {today.strftime('%d / %m / %Y')} م | {hijri} هـ
        </p>
        <h2 style='margin:0;'>⏰ الوقت الآن: {current_time}</h2>
    </div>
    """, unsafe_allow_html=True)

# --- تحميل البيانات ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'])
    except:
        st.error("⚠️ ملف 2085.txt غير موجود في المجلد")
        return None

df = load_data()

if df is not None:
    # --- تحسين عرض الخيارات ---
    st.markdown("### 📍 تحديد الموقع")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        state = st.selectbox("اختر الولاية", ["-- الكل --"] + sorted(df['الولاية'].unique().tolist()))
    
    with col2:
        if state != "-- الكل --":
            district = st.selectbox("اختر المعتمدية", sorted(df[df['الولاية'] == state]['المعتمدية'].unique().tolist()))
        else:
            st.selectbox("المعتمدية", ["اختر الولاية أولاً"], disabled=True)
            
    with col3:
        if state != "-- الكل --":
            village = st.selectbox("اختر العمادة", sorted(df[(df['الولاية'] == state) & (df['المعتمدية'] == district)]['العمادة'].unique().tolist()))
        else:
            st.selectbox("العمادة", ["اختر المعتمدية أولاً"], disabled=True)

    # --- عرض المواقيت ---
    if state != "-- الكل --":
        st.divider()
        # هنا يتم استدعاء الحاسبة (ملاحظة: الإحداثيات تحتاج لربط دقيق، سنستخدم العاصمة كافتراضي حالياً)
        calc = PrayerTimesCalculator(latitude=36.8, longitude=10.1, calculation_method="mwl", date=str(today))
        times = calc.fetch_prayer_times()
        
        st.markdown(f"#### 🕋 مواقيت الصلاة في: {village}، {district}")
        
        p_cols = st.columns(5)
        prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]
        
        for i, (ar, en) in enumerate(prayers):
            with p_cols[i]:
                st.markdown(f"""
                    <div class="prayer-card">
                        <div style='color: #666;'>{ar}</div>
                        <div class="prayer-time">{times[en]}</div>
                    </div>
                """, unsafe_allow_html=True)
