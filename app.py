import streamlit as st
from adhan import adhan
from adhan.methods import custom, ASAR_STANDARD
from datetime import date
from geopy.geocoders import Nominatim

# إعدادات واجهة تونسية
st.set_page_config(page_title="مواقيت الصلاة - تونس", page_icon="🕌")

# دالة الحساب (بزاوية 18 درجة لوزارة الشؤون الدينية)
def get_prayer_times(lat, lon):
    params = custom(fajr_angle=18, isha_angle=18, method_name="Tunisia")
    return adhan(
        day=date.today(),
        location=(lat, lon),
        parameters=params,
        timezone_offset=1,
        asasr_method=ASAR_STANDARD
    )

st.title("🇹🇳 مواقيت الصلاة في تونس")
st.write("حساب دقيق للمعتمديات والقرى بناءً على الموقع الجغرافي")

# خيار البحث عن أي مكان في تونس
place = st.text_input("ابحث عن مدينتك، معتمديتك، أو قريتك:", "تونس العاصمة")

geolocator = Nominatim(user_agent="tunisia_prayer_app_2026")
location = geolocator.geocode(place + ", Tunisia")

if location:
    st.success(f"📍 الموقع: {location.address}")
    times = get_prayer_times(location.latitude, location.longitude)
    
    # عرض الأوقات في مربعات جذابة
    cols = st.columns(3)
    prayers = [
        ("الفجر", "fajr"), ("الشروق", "shuruq"), ("الظهر", "zuhr"),
        ("العصر", "asr"), ("المغرب", "maghrib"), ("العشاء", "isha")
    ]
    
    for i, (name, key) in enumerate(prayers):
        with cols[i % 3]:
            st.info(f"**{name}**\n\n# {times[key].strftime('%H:%M')}")
else:
    st.warning("يرجى التأكد من كتابة اسم المكان بشكل صحيح (مثال: 'منزل تميم' أو 'رمادة')")

st.markdown("---")
st.caption("يعتمد هذا التطبيق على الحساب الفلكي لوزارة الشؤون الدينية التونسية.")
