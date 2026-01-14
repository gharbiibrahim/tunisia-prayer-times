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
            # استخراج اسم الولاية من اسم الملف (مثلاً Bizerte)
            state_name = f.split("-")[-1].replace(".csv", "").strip()
            data_map[state_name] = f
    return data_map

@st.cache_data
def load_state_csv(file_path):
    try:
        # قراءة الملف بدون رؤوس أعمدة (header=None) لتجنب خطأ الأسماء
        df = pd.read_csv(file_path, header=None, encoding='utf-8')
        
        # اختيار الأعمدة حسب الترتيب في ملفاتك:
        # العمود 2: الولاية (بنزرت، تونس...)
        # العمود 4: المعتمدية (منزل بورقيبة، العالية...)
        # العمود 6: العمادة (حي الجلاء، الختمين...)
        df_filtered = df[[2, 4, 6]].copy()
        df_filtered.columns = ['الولاية', 'المعتمدية', 'العمادة']
        
        # تنظيف البيانات من المسافات
        for col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].astype(str).str.strip()
            
        return df_filtered
    except Exception as e:
        st.error(f"حدث خطأ في القراءة: {e}")
        return None

# --- الواجهة ---
st.title("🕌 مواقيت الصلاة بتونس")

available_files = find_data_files()

if not available_files:
    st.error("❌ لم يتم العثور على ملفات CSV. تأكد من وجود الملفات في نفس المجلد.")
else:
    selected_state = st.selectbox("اختر الولاية", ["اختر"] + list(available_files.keys()))

    if selected_state != "اختر":
        df_state = load_state_csv(available_files[selected_state])
        
        if df_state is not None:
            # استخراج المعتمديات الفريدة (سيظهر 14 فقط في بنزرت)
            districts = sorted(df_state['المعتمدية'].unique())
            selected_district = st.selectbox("اختر المعتمدية", ["اختر"] + districts)
            
            if selected_district != "اختر":
                # فلترة العمادات بناءً على المعتمدية المختارة
                villages = sorted(df_state[df_state['المعتمدية'] == selected_district]['العمادة'].unique())
                selected_village = st.selectbox("اختر العمادة", ["اختر"] + villages)
                
                if selected_village != "اختر":
                    # إحداثيات افتراضية
                    lat, lon = 36.80, 10.18 
                    
                    try:
                        calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
                        times = calc.fetch_prayer_times()
                        
                        st.success(f"الموقع: {selected_village} | {selected_district} | {selected_state}")
                        
                        # عرض المواقيت
                        t_cols = st.columns(5)
                        prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]
                        for i, (p_ar, p_en) in enumerate(prayers):
                            t_cols[i].metric(p_ar, times[p_en])
                    except:
                        st.error("خطأ في جلب المواقيت.")
