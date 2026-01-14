import streamlit as st
import pandas as pd
import os
import glob
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from hijri_converter import Gregorian

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌", layout="centered")

# دالة ذكية لجلب الولايات من أسماء الملفات التي رفعتها
def get_states_from_files():
    # البحث عن الملفات التي تبدأ بـ tun_admgz_2022.xls
    files = glob.glob("tun_admgz_2022.xls - *.csv")
    states = []
    for f in files:
        # استخراج اسم الولاية من اسم الملف
        state_name = f.split("- ")[1].replace(".csv", "").strip()
        states.append(state_name)
    return sorted(states)

# دالة تحميل البيانات من ملف الـ CSV
@st.cache_data
def load_data(state):
    file_path = f"tun_admgz_2022.xls - {state}.csv"
    try:
        # ملفاتك لا تحتوي على صف عناوين (Header)، لذا نحدد الأعمدة يدوياً
        # العمود 2: الولاية، العمود 4: المعتمدية، العمود 6: العمادة
        df = pd.read_csv(file_path, header=None, encoding='utf-8')
        df_selected = df[[2, 4, 6]].copy()
        df_selected.columns = ['الولاية', 'المعتمدية', 'العمادة']
        # تنظيف البيانات من المسافات
        for col in df_selected.columns:
            df_selected[col] = df_selected[col].astype(str).str.strip()
        return df_selected
    except Exception as e:
        return pd.DataFrame(columns=['الولاية', 'المعتمدية', 'العمادة'])

# --- الواجهة ---
st.title("🕌 مواقيت الصلاة بتونس")
st.write("بيانات رسمية مستخرجة من السجل الإداري 2022")

available_states = get_states_from_files()

if not available_states:
    st.error("لم يتم العثور على ملفات البيانات. تأكد من وجود ملفات CSV في مجلد التطبيق.")
else:
    # 1. اختيار الولاية
    selected_state = st.selectbox("اختر الولاية", ["اختر"] + available_states)

    if selected_state != "اختر":
        df = load_data(selected_state)
        
        # 2. اختيار المعتمدية (ستظهر 14 فقط في بنزرت لأننا نستخدم unique)
        districts = sorted(df['المعتمدية'].unique())
        selected_district = st.selectbox("اختر المعتمدية", ["اختر"] + districts)
        
        if selected_district != "اختر":
            # 3. اختيار العمادة
            villages = sorted(df[df['المعتمدية'] == selected_district]['العمادة'].unique())
            selected_village = st.selectbox("اختر العمادة", ["اختر"] + villages)
            
            if selected_village != "اختر":
                # --- حساب المواقيت ---
                # إحداثيات تقريبية (يمكن تطويرها لاحقاً لتكون أكثر دقة لكل معتمدية)
                COORDS = {
                    "Tunis": (36.80, 10.18), "Bizerte": (37.27, 9.87), "Sousse": (35.82, 10.63),
                    "Sfax": (34.74, 10.76), "Kairouan": (35.67, 10.09), "Béja": (36.73, 9.18),
                    "Jendouba": (36.50, 8.78), "Nabeul": (36.45, 10.73) # أضف بقية الولايات هنا
                }
                
                # استخدام اسم الولاية بالإنجليزية للبحث في القاموس
                # إذا لم توجد، نستخدم إحداثيات العاصمة كافتراضي
                lat, lon = COORDS.get(selected_state, (36.80, 10.18))
                
                try:
                    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
                    times = calc.fetch_prayer_times()
                    
                    # عرض النتائج
                    st.success(f"الموقع: {selected_village} | {selected_district} | {selected_state}")
                    
                    cols = st.columns(5)
                    prayers = [("الفجر", "Fajr"), ("الظهر", "Dhuhr"), ("العصر", "Asr"), ("المغرب", "Maghrib"), ("العشاء", "Isha")]
                    
                    for i, (name, key) in enumerate(prayers):
                        cols[i].metric(name, times[key])
                except:
                    st.warning("تعذر الاتصال بخدمة المواقيت، يرجى المحاولة لاحقاً.")
