import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from hijri_converter import Gregorian
import math

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="مواقيت الصلاة الرسمية بتونس", page_icon="🕌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .big-time-box { text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 20px; border: 3px solid #d32f2f; margin-bottom: 20px; }
    .day-name { font-size: 3rem; font-weight: bold; color: #2c3e50; }
    .current-time { font-size: 5rem; font-weight: bold; color: #d32f2f; line-height: 1; }
    .prayer-card { background: white; padding: 12px; border-radius: 15px; text-align: center; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .prayer-time { font-size: 1.8rem; font-weight: bold; color: #d32f2f; }
    .dhikr-box { background-color: #fff3e0; padding: 20px; border-right: 5px solid #ff9800; border-radius: 10px; margin-top: 20px; font-size: 1.2rem; }
    .qibla-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #4caf50; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. بيانات الموقع (تونس)
TUNISIA_COORDS = {
    "تونس": (36.8065, 10.1815), "بنزرت": (37.2744, 9.8739), "أريانة": (36.8665, 10.1647),
    "بن عروس": (36.7531, 10.2222), "منوبة": (36.8078, 10.0863), "نابل": (36.4561, 10.7376),
    "زغوان": (36.4029, 10.1429), "باجة": (36.7256, 9.1906), "جندوبة": (36.5011, 8.7802),
    "الكاف": (36.1822, 8.7148), "سليانة": (36.0840, 9.3708), "سوسة": (35.8256, 10.6084),
    "المنستير": (35.7780, 10.8262), "المهدية": (35.5047, 11.0622), "القيروان": (35.6781, 10.0963),
    "سيدي بوزيد": (35.0382, 9.4849), "القصرين": (35.1676, 8.8365), "صفاقس": (34.7400, 10.7600),
    "قفصة": (34.4250, 8.7842), "توزر": (33.9197, 8.1335), "قبلي": (33.7050, 8.9714),
    "قابس": (33.8815, 10.0982), "مدنين": (33.3550, 10.4922), "تطاوين": (32.9297, 10.4518)
}

# 3. تحميل البيانات الهرمية من ملفك
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('nouveau 2085.txt', sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'], engine='python', encoding='utf-8')
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except: return pd.DataFrame()

df = load_data()

# 4. واجهة الاختيار
st.title("🕌 حقيبة المؤمن التونسي")
col_s, col_d, col_v = st.columns(3)
with col_s: state = st.selectbox("الولاية", ["اختر"] + sorted(df['الولاية'].unique().tolist()))
with col_d: district = st.selectbox("المعتمدية", sorted(df[df['الولاية']==state]['المعتمدية'].unique()) if state != "اختر" else [])
with col_v: village = st.selectbox("العمادة", sorted(df[(df['الولاية']==state) & (df['المعتمدية']==district)]['العمادة'].unique()) if district else [])

if state != "اختر":
    now = datetime.now()
    lat, lon = TUNISIA_COORDS[state]
    
    # حساب المواقيت (زاوية 18 وتعديلات تونس)
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
    times = calc.fetch_prayer_times()
    def adj(t, m): return (datetime.strptime(t, "%H:%M") + timedelta(minutes=m)).strftime("%H:%M")
    
    prayers = {"الفجر": times["Fajr"], "الشروق": times["Sunrise"], "الظهر": adj(times["Dhuhr"], 7), 
               "العصر": times["Asr"], "المغرب": adj(times["Maghrib"], 2), "العشاء": adj(times["Isha"], 6)}

    # عرض الوقت والتاريخ
    day_ar = {"Monday":"الاثنين","Tuesday":"الثلاثاء","Wednesday":"الأربعاء","Thursday":"الخميس","Friday":"الجمعة","Saturday":"السبت","Sunday":"الأحد"}[now.strftime('%A')]
    hijri = Gregorian(now.year, now.month, now.day).to_hijri()
    
    st.markdown(f"""
        <div class="big-time-box">
            <div class="day-name">{day_ar}</div>
            <div class="current-time">{now.strftime('%H:%M')}</div>
            <div style="font-size:1.5rem;">{hijri.day} {hijri.month_name()} {hijri.year} هـ | {now.strftime('%d/%m/%Y')} م</div>
        </div>
    """, unsafe_allow_html=True)

    # عرض المواقيت
    cols = st.columns(3)
    for i, (name, val) in enumerate(prayers.items()):
        with cols[i%3]: st.markdown(f"<div class='prayer-card'><b>{name}</b><div class='prayer-time'>{val}</div></div>", unsafe_allow_html=True)

    # ميزة 1: اتجاه القبلة (حساب فلكي تقريبي لتونس)
    # زاوية القبلة من تونس تقريباً 100-110 درجة من الشمال
    st.markdown(f"""
        <div class="qibla-box">
            <b>🧭 اتجاه القبلة لولاية {state}:</b> {105 if state in ["تونس","بنزرت"] else 100} درجة من اتجاه الشمال
        </div>
    """, unsafe_allow_html=True)

    # ميزة 2: أذكار متغيرة
    is_morning = 5 <= now.hour < 12
    dhikr = "أصبحنا وأصبح الملك لله والحمد لله" if is_morning else "أمسينا وأمسى الملك لله والحمد لله"
    dhikr_title = "أذكار الصباح" if is_morning else "أذكار المساء"
    st.markdown(f"""<div class="dhikr-box"><b>✨ {dhikr_title}:</b><br>{dhikr}... (اللهم بك أصبحنا وبك أمسينا)</div>""", unsafe_allow_html=True)

    # ميزة 3: مشاركة المواقيت
    share_text = f"مواقيت الصلاة في {state} ({village}) ليوم {day_ar}:\n" + "\n".join([f"{k}: {v}" for k,v in prayers.items()])
    st.download_button("📤 نسخ ومشاركة المواقيت", share_text, file_name="prayers.txt")
    
    # رابط واتساب مباشر
    whatsapp_url = f"https://wa.me/?text={share_text.replace(' ', '%20').replace(':', '%3A')}"
    st.markdown(f"""<a href="{whatsapp_url}" target="_blank"><button style="width:100%; border-radius:10px; background-color:#25D366; color:white; border:none; padding:10px; cursor:pointer;">🟢 مشاركة عبر واتساب</button></a>""", unsafe_allow_html=True)

else:
    st.info("الرجاء اختيار الموقع من القوائم أعلاه.")
