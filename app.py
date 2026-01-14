import streamlit as st
import pandas as pd
import os
import glob
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌")

# دالة للبحث عن الملفات بأي صيغة مشابهة لملفاتك
def find_data_files():
    # يبحث عن أي ملف CSV يحتوي على كلمة "tun_admgz" أو ينتهي بـ .csv
    files = glob.glob("*.csv")
    data_map = {}
    for f in files:
        if "tun_admgz_2022" in f:
            # استخراج اسم الولاية بعد علامة الـ "-"
            try:
                state_name = f.split("-")[-1].replace(".csv", "").strip()
                data_map[state_name] = f
            except:
                continue
    return data_map

# دالة تحميل البيانات
@st.cache_data
def load_state_csv(file_path):
    try:
        # قراءة الملف مع تحديد الترميز الصحيح
        df = pd.read_csv(file_path, header=None, encoding='utf-8')
        # تحديد الأعمدة: 2 للمحافظة، 4 للمعتمدية، 6 للعمادة
        df = df[[2, 4, 6]]
        df.columns = ['الولاية', 'المعتمدية', 'العمادة']
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return None

# --- الواجهة الرسومية ---
st.title("🕌 نظام مواقيت الصلاة الدقيق")

available_files = find_data_files()

if not available_files:
    st.error("❌ لم يتم العثور على الملفات. تأكد أن الملفات (مثل tun_admgz_2022.xls - Bizerte.csv) موجودة في نفس مجلد ملف app.py")
else:
    # 1. اختيار الولاية
    selected_state_name = st.selectbox("اختر الولاية", ["اختر"] + list(available_files.keys()))

    if selected_state_name != "اختر":
        file_path = available_files[selected_state_name]
        df_state = load_state_csv(file_path)
        
        if df_state is not None:
            # 2. اختيار المعتمدية (هنا ستظهر 14 معتمدية فقط لبنزرت)
            districts = sorted(df_state['المعتمدية'].unique())
            selected_district = st.selectbox("اختر المعتمدية", ["اختر"] + districts)
            
            if selected_district != "اختر":
                # 3. اختيار العمادة
                villages = sorted(df_state[df_state['المعتمدية'] == selected_district]['العمادة'].unique())
                selected_village = st.selectbox("اختر العمادة", ["اختر"] + villages)
                
                if selected_village != "اختر":
                    # إحداثيات افتراضية (يمكنك ربطها بجدول إحداثيات لاحقاً)
                    lat, lon = 37.27, 9.87 # إحداثيات بنزرت كمثال
                    
                    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
                    times = calc.fetch_prayer_times()
                    
                    st.success(f"الموقع: {selected_state_name} > {selected_district} > {selected_village}")
                    
                    # عرض المواقيت في مربعات
                    cols = st.columns(5)
                    cols[0].metric("الفجر", times['Fajr'])
                    cols[1].metric("الظهر", times['Dhuhr'])
                    cols[2].metric("العصر", times['Asr'])
                    cols[3].metric("المغرب", times['Maghrib'])
                    cols[4].metric("العشاء", times['Isha'])
