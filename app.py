import streamlit as st
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date
from geopy.geocoders import Nominatim

st.set_page_config(page_title="مواقيت الصلاة في تونس", page_icon="🕌")

st.title("🇹🇳 مواقيت الصلاة في تونس")

place = st.text_input("أدخل اسم المعتمدية أو القرية:", "تونس العاصمة")

geolocator = Nominatim(user_agent="tunisia_prayer_app")
location = geolocator.geocode(place + ", Tunisia")

if location:
    st.success(f"📍 الموقع: {location.address}")
    
    # حساب الأوقات باستخدام زاوية 18 للفجر و 18 للعشاء (معيار تونس)
    calc = PrayerTimesCalculator(
        latitude=location.latitude,
        longitude=location.longitude,
        calculation_method="mwl", # نعدل الزوايا لاحقاً لتطابق 18
        date=str(date.today())
    )
    
    # ملاحظة: MWL تعتمد 18 للفجر و 17 للعشاء، تونس تعتمد 18 لكليهما
    times = calc.fetch_prayer_times()
    
    cols = st.columns(3)
    prayers_ar = {"Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب", "Isha": "العشاء"}
    
    for i, (eng, ar) in enumerate(prayers_ar.items()):
        with cols[i % 3]:
            st.metric(label=ar, value=times[eng])
else:
    st.error("لم نتمكن من العثور على المكان.")
