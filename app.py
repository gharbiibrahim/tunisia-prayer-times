import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌", layout="wide")

# --- CSS مخصص لدعم RTL وتجميل الواجهة ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Amiri:wght@700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    
    /* تصميم الهيدر (التاريخ والوقت) */
    .header-box {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* تصميم بطاقات المواقيت */
    .prayer-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border-right: 8px solid #d4af37;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin: 5px;
    }
    .prayer-name { font-family: 'Amiri', serif; font-size: 1.4rem; color: #1b5e20; }
    .prayer-time { font-size: 1.9rem; font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- عرض التاريخ والوقت الحالي ---
today = date.today()
hijri = HijriDate.get_hijri_date(today)
current_time = datetime.now().strftime("%I:%M %p")

st.markdown(f"""
    <div class="header-box">
        <h1 style='font-family: Amiri; margin:0;'>🕌 مواقيت الصلاة في تونس</h1>
        <div style='font-size: 1.3rem; margin-top: 10px;'>
            {today.strftime('%A')} : {today.strftime('%d / %m / %Y')} م | {hijri} هـ
        </div>
        <div style='font-size: 1.5rem; font-weight: bold; margin-top: 5px;'>⌚ الوقت الآن: {current_time}</div>
    </div>
    """, unsafe_allow_html=True)

# --- تحميل البيانات وتحسين الفلاتر ---
@st.cache_data
def load_data():
    try:
        # قراءة الملف مع تجاهل المسافات الزائدة
        df = pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'])
        return df
    except:
        return None

df = load_data()

if df is not None:
    st.markdown("### 📍 اختر منطقتك بدقة")
    
    # تحسين طريقة العرض في 3 أعمدة
    c1, c2, c3 = st.columns(3)
    
    with c1:
        states = sorted(df['الولاية'].unique())
        sel_state = st.selectbox("📌 الولاية", ["-- اختر الولاية --"] + states)

    with c2:
        if sel_state != "-- اختر الولاية --":
            districts = sorted(df[df['الولاية'] == sel_state]['المعتمدية'].unique())
            sel_district = st.selectbox("🏢 المعتمدية", ["-- اختر المعتمدية --"] + districts)
        else:
            st.selectbox("🏢 المعتمدية", ["يرجى تحديد الولاية"], disabled=True)

    with c3:
        if sel_state != "-- اختر الولاية --" and 'sel_district' in locals() and sel_district != "-- اختر المعتمدية --":
            villages = sorted(df[(df['الولاية'] == sel_state) & (df['المعتمدية'] == sel_district)]['العمادة'].unique())
            sel_village = st.selectbox("🏡 العمادة/القرية", ["-- اختر العمادة --"] + villages)
        else:
            st.selectbox("🏡 العمادة", ["يرجى تحديد المعتمدية"], disabled=True)

    # --- حساب وعرض المواقيت ---
    if 'sel_village' in locals() and sel_village != "-- اختر العمادة --":
        st.divider()
        st.markdown(f"<h3 style='text-align: center;'>🕋 مواقيت الصلاة لجهة: {sel_village}</h3>", unsafe_allow_html=True)
        
        # ملاحظة: الإحداثيات هنا تقريبية، يمكن تحسينها بجلب إحداثيات كل معتمدية
        calc = PrayerTimesCalculator(latitude=36.8, longitude=10.1, calculation_method="mwl", date=str(today))
        times = calc.fetch_prayer_times()

        p_cols = st.columns(5)
        prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]
        
        for i, (ar_name, en_key) in enumerate(prayers):
            with p_cols[i]:
                st.markdown(f"""
                    <div class="prayer-card">
                        <div class="prayer-name">{ar_name}</div>
                        <div class="prayer-time">{times[en_key]}</div>
                    </div>
                """, unsafe_allow_html=True)
