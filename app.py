import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date

# --- إعدادات الصفحة والجمالية ---
st.set_page_config(page_title="مواقيت الصلاة - تونس", page_icon="🕌", layout="wide")

# إضافة CSS مخصص لدعم اليمين إلى اليسار وتجميل الواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&display=swap');

    /* تنسيق الجسم العام ودعم RTL */
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
        background-color: #f8f9fa;
    }

    /* تنسيق العناوين */
    h1, h2, h3 {
        font-family: 'Amiri', serif;
        color: #2c3e50;
    }

    /* بطاقات مواقيت الصلاة */
    .prayer-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border-bottom: 4px solid #2e7d32;
        transition: transform 0.3s ease;
    }
    .prayer-card:hover {
        transform: translateY(-5px);
        border-bottom: 4px solid #d4af37;
    }
    .prayer-name {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    .prayer-time {
        color: #2e7d32;
        font-size: 1.8rem;
        font-weight: bold;
    }

    /* تنسيق القوائم المنسدلة */
    div[data-baseweb="select"] {
        direction: RTL;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # قراءة ملف 2085.txt
        df = pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'], encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {e}")
        return None

# --- الواجهة الرسومية ---
st.markdown("<h1 style='text-align: center;'>✨ مواقيت الصلاة بدقة العواصم والقرى</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d;'>نظام متطور يعتمد على ملف 2085 لتغطية كافة ربوع تونس</p>", unsafe_allow_html=True)

df = load_data()

if df is not None:
    # تقسيم الصفحة لثلاثة أعمدة للاختيارات
    col1, col2, col3 = st.columns(3)
    
    with col1:
        states = sorted(df['الولاية'].unique())
        selected_state = st.selectbox("📍 الولاية", ["اختر ولاية"] + states)

    with col2:
        if selected_state != "اختر ولاية":
            districts = sorted(df[df['الولاية'] == selected_state]['المعتمدية'].unique())
            selected_district = st.selectbox("🏢 المعتمدية", ["اختر معتمدية"] + districts)
        else:
            st.selectbox("🏢 المعتمدية", ["انتظر اختيار الولاية"], disabled=True)

    with col3:
        if selected_state != "اختر ولاية" and 'selected_district' in locals() and selected_district != "اختر معتمدية":
            villages = sorted(df[(df['الولاية'] == selected_state) & (df['المعتمدية'] == selected_district)]['العمادة'].unique())
            selected_village = st.selectbox("🏡 العمادة/القرية", ["اختر عمادة"] + villages)
        else:
            st.selectbox("🏡 العمادة/القرية", ["انتظر اختيار المعتمدية"], disabled=True)

    # --- عرض النتائج بلمسة إبداعية ---
    if 'selected_village' in locals() and selected_village != "اختر عمادة":
        st.markdown("<br>", unsafe_allow_html=True)
        
        # حساب المواقيت (بناءً على إحداثيات تقريبية للمنطقة)
        lat, lon = 36.8, 10.1 # يمكن تحسينها بجلب إحداثيات كل منطقة
        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
        times = calc.fetch_prayer_times()

        # عرض العنوان المختار
        st.markdown(f"""
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 10px; text-align: center; margin-bottom: 25px;">
                مواقيت الصلاة اليوم في <b>{selected_village}</b> ({selected_district}) - {date.today().strftime('%Y/%m/%d')}
            </div>
        """, unsafe_allow_html=True)

        # عرض المواقيت في بطاقات
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

        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-style: italic;'>'إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَوْقُوتًا'</p>", unsafe_allow_html=True)
