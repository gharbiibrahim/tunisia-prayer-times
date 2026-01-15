import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مواقيت الصلاة بتونس", page_icon="🕌", layout="centered")

@st.cache_data
def load_data_from_text():
    try:
        # قراءة الملف 2085.txt مع تحديد المفصل كـ Tab (\t)
        # الملف يحتوي على 3 أعمدة: الولاية، المعتمدية، العمادة
        df = pd.read_csv("2085.txt", sep='\t', header=None, names=['الولاية', 'المعتمدية', 'العمادة'], encoding='utf-8')
        
        # تنظيف البيانات من المسافات الزائدة
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except FileNotFoundError:
        st.error("❌ لم يتم العثور على الملف '2085.txt' في مجلد التطبيق.")
        return None
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
        return None

# --- واجهة المستخدم ---
st.title("🕌 مواقيت الصلاة بتونس")
st.write("بيانات مستخرجة من ملف 2085 المحلي")

df = load_data_from_text()

if df is not None:
    # 1. اختيار الولاية
    states = sorted(df['الولاية'].unique())
    selected_state = st.selectbox("اختر الولاية", ["اختر ولاية"] + states)

    if selected_state != "اختر ولاية":
        # 2. اختيار المعتمدية (تصفية بناءً على الولاية)
        mask_state = df['الولاية'] == selected_state
        districts = sorted(df[mask_state]['المعتمدية'].unique())
        selected_district = st.selectbox("اختر المعتمدية", ["اختر معتمدية"] + districts)
        
        if selected_district != "اختر معتمدية":
            # 3. اختيار العمادة (تصفية بناءً على المعتمدية)
            mask_district = (df['الولاية'] == selected_state) & (df['المعتمدية'] == selected_district)
            villages = sorted(df[mask_district]['العمادة'].unique())
            selected_village = st.selectbox("اختر العمادة", ["اختر عمادة"] + villages)
            
            if selected_village != "اختر عمادة":
                # --- حساب المواقيت ---
                # إحداثيات افتراضية للمركز (يمكنك توسيعها لاحقاً)
                lat, lon = 36.80, 10.18 
                
                try:
                    calc = PrayerTimesCalculator(
                        latitude=lat, 
                        longitude=lon, 
                        calculation_method="mwl", 
                        date=str(date.today())
                    )
                    times = calc.fetch_prayer_times()
                    
                    st.divider()
                    st.success(f"📍 {selected_village}، {selected_district}، {selected_state}")
                    
                    # عرض المواقيت في أعمدة
                    cols = st.columns(5)
                    prayers = [
                        ("الفجر", "Fajr"), ("الظهر", "Dhuhr"), 
                        ("العصر", "Asr"), ("المغرب", "Maghrib"), 
                        ("العشاء", "Isha")
                    ]
                    
                    for i, (ar_name, en_key) in enumerate(prayers):
                        cols[i].metric(ar_name, times[en_key])
                        
                except Exception:
                    st.error("حدث خطأ في جلب مواقيت الصلاة.")
