import streamlit as st
from adhan import adhan
from adhan.methods import custom, ASAR_STANDARD
from datetime import date, datetime
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="توقيت الصلاة بتونس", layout="centered")

# دالة حساب الأوقات
def get_times(lat, lon):
    tunisia_params = custom(fajr_angle=18, isha_angle=18, method_name="Tunisia")
    return adhan(
        day=date.today(),
        location=(lat, lon),
        parameters=tunisia_params,
        timezone_offset=1,
        asasr_method=ASAR_STANDARD
    )

# واجهة التطبيق
st.title("🌙 أوقات الصلاة في الجمهورية التونسية")
st.write(f"اليوم: {date.today().strftime('%Y-%m-%d')}")

# قائمة الولايات (أمثلة للإحداثيات)
states = {
    "تونس العاصمة": (36.8065, 10.1815),
    "بنزرت (ماطر)": (37.0400, 9.6650),
    "صفاقس": (34.7400, 10.7600),
    "سوسة": (35.8256, 10.6084),
    "قابس": (33.8815, 10.0982),
    "تطاوين": (32.9297, 10.4518)
}

selected_state = st.selectbox("اختر الولاية أو أقرب مدينة كبيرة:", list(states.keys()))
coords = states[selected_state]

# حساب الأوقات
p_times = get_times(coords[0], coords[1])

# عرض النتائج بشكل جميل
st.markdown("---")
cols = st.columns(3)
display_order = [
    ("الفجر", "fajr"), ("الشروق", "shuruq"), ("الظهر", "zuhr"),
    ("العصر", "asr"), ("المغرب", "maghrib"), ("العشاء", "isha")
]

for i, (name, key) in enumerate(display_order):
    with cols[i % 3]:
        st.metric(label=name, value=p_times[key].strftime("%H:%M"))

st.markdown("---")
st.caption("تم ضبط الحسابات وفقاً لزاوية 18 درجة (وزارة الشؤون الدينية التونسية).")