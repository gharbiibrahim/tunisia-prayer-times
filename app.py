import streamlit as st
import pandas as pd
import glob
import os
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from hijri_converter import Gregorian

# --- إعدادات الواجهة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس - دقة الإكسيل", page_icon="🕌")

# دالة لجلب قائمة الولايات المتاحة من أسماء الملفات
def get_available_states():
    files = glob.glob("tun_admgz_2022.xls - *.csv")
    states = [f.split("- ")[1].replace(".csv", "").strip() for f in files]
    return sorted(states)

# دالة لتحميل بيانات ولاية معينة من ملف الـ CSV الخاص بها
def load_state_data(state_name):
    file_path = f"tun_admgz_2022.xls - {state_name}.csv"
    if os.path.exists(file_path):
        # قراءة الملف - الأعمدة في ملفاتك هي: الإقليم، المحافظة، المعتمدية، العمادة...
        df = pd.read_csv(file_path, header=None)
        # حسب هيكلة ملفاتك: العمود 2 هو الولاية، العمود 4 هو المعتمدية، العمود 6 هو العمادة
        df_cleaned = df[[2, 4, 6]].copy()
        df_cleaned.columns = ['الولاية', 'المعتمدية', 'العمادة']
        return df_cleaned
    return pd.DataFrame()

# --- واجهة المستخدم ---
st.title("🕌 مواقيت الصلاة حسب السجل الرسمي")

states = get_available_states()
selected_state = st.selectbox("اختر الولاية", ["اختر"] + states)

if selected_state != "اختر":
    df_state = load_state_data(selected_state)
    
    # استخراج المعتمديات (ستظهر 14 فقط لبنزرت كما طلبت)
    districts = sorted(df_state['المعتمدية'].unique())
    selected_district = st.selectbox("اختر المعتمدية", ["اختر"] + districts)
    
    if selected_district != "اختر":
        # استخراج العمادات التابعة للمعتمدية المختارة
        villages = sorted(df_state[df_state['المعتمدية'] == selected_district]['العمادة'].unique())
        selected_village = st.selectbox("اختر العمادة", ["اختر"] + villages)
        
        if selected_village != "اختر":
            # إحداثيات الولايات (يمكنك توسيعها لتشمل إحداثيات أدق للمعتمديات)
            COORDS = {
                "بنزرت": (37.2744, 9.8739), "تونس": (36.8065, 10.1815), # ... بقية الإحداثيات
            }
            
            lat, lon = COORDS.get(selected_state, (36.8065, 10.1815))
            
            # حساب المواقيت
            calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
            times = calc.fetch_prayer_times()
            
            # عرض النتائج بتنسيق جذاب
            st.success(f"الموقع المعتمد: {selected_village}، {selected_district}، {selected_state}")
            
            # (هنا تضع مصفوفة عرض المواقيت كما في الكود السابق)
            st.write(f"فجر: {times['Fajr']} | ظهر: {times['Dhuhr']} | عصر: {times['Asr']} | مغرب: {times['Maghrib']} | عشاء: {times['Isha']}")
