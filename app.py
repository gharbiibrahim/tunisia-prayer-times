import streamlit as st
import pandas as pd
import glob
import os
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌")

def find_data_files():
    files = glob.glob("*.csv")
    data_map = {}
    for f in files:
        if "tun_admgz_2022" in f:
            state_name = f.split("-")[-1].replace(".csv", "").strip()
            data_map[state_name] = f
    return data_map

@st.cache_data
def load_state_csv(file_path):
    try:
        # قراءة الملف مع السماح لـ pandas بالتعرف على العناوين تلقائياً
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # اختيار الأعمدة بناءً على أسمائها الموجودة في ملفاتك
        # الملفات تحتوي على: [الإقليم، المحافظة، المعتمدية، العمادة...]
        needed_columns = {
            'المحافظة': 'الولاية',
            'المعتمدية': 'المعتمدية',
            'العمادة': 'العمادة'
        }
        
        # التأكد من وجود الأعمدة المطلوبة وتغيير أسمائها لسهولة التعامل
        df_filtered = df[list(needed_columns.keys())].copy()
        df_filtered.rename(columns=needed_columns, inplace=True)
        
        # تنظيف البيانات من أي مسافات زائدة
        for col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].astype(str).str.strip()
            
        return df_filtered
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
        return None

# --- الواجهة ---
st.title("🕌 مواقيت الصلاة بتونس")

available_files = find_data_files()

if not available_files:
    st.error("لم يتم العثور على ملفات البيانات بنسق CSV.")
else:
    selected_state = st.selectbox("اختر الولاية", ["اختر"] + list(available_files.keys()))

    if selected_state != "اختر":
        df_state = load_state_csv(available_files[selected_state])
        
        if df_state is not None:
            # هنا سيظهر 14 معتمدية فقط لولاية بنزرت بشكل دقيق
            districts = sorted(df_state['المعتمدية'].unique())
            selected_district = st.selectbox("اختر المعتمدية", ["اختر"] + districts)
            
            if selected_district != "اختر":
                villages = sorted(df_state[df_state['المعتمدية'] == selected_district]['العمادة'].unique())
                selected_village = st.selectbox("اختر العمادة", ["اختر"] + villages)
                
                if selected_village != "اختر":
                    # إحداثيات افتراضية - يمكنك ربطها بملف إحداثيات لاحقاً
                    lat, lon = 36.80, 10.18 
                    
                    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
                    times = calc.fetch_prayer_times()
                    
                    st.success(f"الموقع المختار: {selected_village}، {selected_district}، {selected_state}")
                    
                    # عرض المواقيت
                    t_cols = st.columns(5)
                    prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]
                    for i, (p_ar, p_en) in enumerate(prayers):
                        t_cols[i].metric(p_ar, times[p_en])
