import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime
import time
from ummalqura.hijri_date import HijriDate # مكتبة التاريخ الهجري

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌", layout="wide")

# --- تحسينات CSS للواجهة العربية الإبداعية ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Amiri:wght@700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
        background-color: #f4f7f6;
    }

    /* شريط الوقت والتاريخ */
    .date-container {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* تحسين القوائم المنسدلة */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px;
        border: 1px solid #2e7d32;
    }

    /* بطاقات الصلاة الملونة */
    .prayer-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        border-right: 6px solid #d4af37;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: 0.3s;
    }
    .prayer-card:hover {
        transform: scale(1.05);
        background-color: #fffdf5;
    }
    .prayer-name { font-family: 'Amiri', serif; font-size: 1.4rem; color: #1b5e20; }
    .prayer-time { font-size: 1.8rem; font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'], encoding='utf-8')
        return df
    except:
        return None

# --- عرض الوقت والتاريخ (التاتش الإبداعي) ---
today = date.today()
now = datetime.now().strftime("%H:%M:%S")
hijri = HijriDate.get_hijri_date(today) # تحويل التاريخ لميلادي

st.markdown(f"""
    <div class="date-container">
        <h2 style="margin:0; font-family: 'Amiri';">📅 اليوم: {today.strftime('%A')}</h2>
        <div style="font-size: 1.2rem; margin-top: 10px;">
            <span>🗓️ ميلادي: {today.strftime('%d / %m / %Y')}</span> | 
            <span>🌙 هجري: {hijri}</span> | 
            <span>⏰ الوقت الآن: {now}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = load_data()

if df is not None:
    # --- تحسين عرض خيارات المنطقة ---
    with st.expander("🔍 تخصيص الموقع الجغرافي", expanded=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            states = sorted(df['الولاية'].unique())
            sel_state = st.selectbox("📌 اختر الولاية", ["-- اختر ولايتك --"] + states)

        with c2:
            if sel_state != "-- اختر ولايتك --":
                districts = sorted(df[df['الولاية'] == sel_state]['المعتمدية'].unique())
                sel_district = st.selectbox("🏢 اختر المعتمدية", ["-- اختر المعتمدية --"] + districts)
            else:
                st.selectbox("🏢 المعتمدية", ["قم باختيار الولاية أولاً"], disabled=True)

        with c3:
            if sel_state != "-- اختر ولايتك --" and 'sel_district' in locals() and sel_district != "-- اختر المعتمدية --":
                villages = sorted(df[(df['الولاية'] == sel_state) & (df['المعتمدية'] == sel_district)]['العمادة'].unique())
                sel_village = st.selectbox("🏡 اختر العمادة", ["-- اختر العمادة --"] + villages)
            else:
                st.selectbox("🏡 العمادة", ["قم باختيار المعتمدية أولاً"], disabled=True)

    # --- عرض المواقيت ---
    if 'sel_village' in locals() and sel_village != "-- اختر العمادة --":
        st.markdown(f"<h3 style='text-align: center; color: #2e7d32;'>🕌 مواقيت الصلاة في {sel_village}</h3>", unsafe_allow_html=True)
        
        # حساب المواقيت (إحداثيات تونس العاصمة كمثال، يمكن ربطها بقاعدة بيانات أدق)
        calc = PrayerTimesCalculator(latitude=36.8, longitude=10.1, calculation_method="mwl", date=str(today))
        times = calc.fetch_prayer_times()

        cols = st.columns(5)
        prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]
        
        for i, (name, key) in enumerate(prayers):
            with cols[i]:
                st.markdown(f"""
                    <div class="prayer-card">
                        <div class="prayer-name">{name}</div>
                        <div class="prayer-time">{times[key]}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.info("💡 ملاحظة: يتم حساب المواقيت بناءً على رابطة العالم الإسلامي وتوقيت تونس المحلي.")

# إضافة خاصية التحديث التلقائي للوقت (اختياري)
if st.button('تحديث الوقت الآن 🔄'):
    st.rerun()
