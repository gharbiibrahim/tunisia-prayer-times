import streamlit as st
import pandas as pd
from prayer_times_calculator import PrayerTimesCalculator
from datetime import date, datetime, timedelta
from hijri_converter import Gregorian

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="مواقيت الصلاة الرسمية بتونس", page_icon="🕌", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { direction: RTL; text-align: right; font-family: 'Cairo', sans-serif; }
    .big-time-box { text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 20px; border: 3px solid #d32f2f; margin-bottom: 20px; }
    .day-name { font-size: 3.5rem; font-weight: bold; color: #2c3e50; display: block; }
    .current-time { font-size: 5.5rem; font-weight: bold; color: #d32f2f; line-height: 1.1; }
    .date-container { font-size: 1.8rem; margin-top: 10px; color: #555; }
    .hijri-date { font-weight: bold; color: #b71c1c; }
    .gregorian-date { font-size: 1.4rem; color: #7f8c8d; }
    .prayer-card { background: white; padding: 12px; border-radius: 15px; text-align: center; border: 1px solid #eee; margin-bottom: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .prayer-time { font-size: 2rem; font-weight: bold; color: #d32f2f; }
    .dhikr-box { background-color: #fff3e0; padding: 15px; border-right: 5px solid #ff9800; border-radius: 10px; margin-top: 20px; font-size: 1.2rem; }
    .qibla-box { background-color: #e8f5e9; padding: 12px; border-radius: 10px; text-align: center; border: 1px solid #4caf50; margin-top: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- بيانات الإحداثيات الثابتة للولايات ---
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

# --- تحميل وتنظيف البيانات من الملف ---
@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv('nouveau 2085.txt', sep='\t', names=['الولاية', 'المعتمدية', 'العمادة'], engine='python', encoding='utf-8')
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except:
        return pd.DataFrame()

df_clean = load_and_clean_data()

# --- واجهة المستخدم ---
st.title("🕌 حقيبة المؤمن التونسي")

col1, col2, col3 = st.columns(3)
with col1:
    selected_state = st.selectbox("الولاية", ["اختر"] + sorted(df_clean['الولاية'].unique().tolist()) if not df_clean.empty else [])
with col2:
    districts = sorted(df_clean[df_clean['الولاية'] == selected_state]['المعتمدية'].unique()) if selected_state != "اختر" else []
    selected_district = st.selectbox("المعتمدية", ["اختر"] + districts)
with col3:
    villages = sorted(df_clean[(df_clean['الولاية'] == selected_state) & (df_clean['المعتمدية'] == selected_district)]['العمادة'].unique()) if selected_district != "اختر" else []
    selected_village = st.selectbox("العمادة", ["اختر"] + villages)

if selected_state != "اختر":
    now = datetime.now()
    lat, lon = TUNISIA_COORDS[selected_state]
    
    # حساب المواقيت بمعايير تونس (زاوية 18 وتعديلات الظهر والمغرب)
    calc = PrayerTimesCalculator(latitude=lat, longitude=lon, calculation_method="mwl", date=str(date.today()))
    times = calc.fetch_prayer_times()
    def adj(t, m): return (datetime.strptime(t, "%H:%M") + timedelta(minutes=m)).strftime("%H:%M")
    
    prayers = {
        "الفجر": times["Fajr"], "الشروق": times["Sunrise"],
        "الظهر": adj(times["Dhuhr"], 7), "العصر": times["Asr"],
        "المغرب": adj(times["Maghrib"], 2), "العشاء": adj(times["Isha"], 6)
    }

    # عرض الوقت واليوم
    days_ar = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
    hijri = Gregorian(now.year, now.month, now.day).to_hijri()
    
    st.markdown(f"""
        <div class="big-time-box">
            <span class="day-name">{days_ar[now.strftime('%A')]}</span>
            <span class="current-time">{now.strftime('%H:%M')}</span>
            <div class="date-container">
                <span class="hijri-date">{hijri.day} {hijri.month_name()} {hijri.year} هـ</span><br>
                <span class="gregorian-date">{now.strftime('%d/%m/%Y')} م</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # عرض جدول الصلوات
    cols = st.columns(3)
    for i, (name, val) in enumerate(prayers.items()):
        with cols[i % 3]:
            st.markdown(f"<div class='prayer-card'><b>{name}</b><div class='prayer-time'>{val}</div></div>", unsafe_allow_html=True)

    # القبلة والأذكار
    st.markdown(f"<div class='qibla-box'>🧭 اتجاه القبلة لولاية {selected_state}: {105 if selected_state in ['تونس','بنزرت','نابل'] else 100} درجة من الشمال</div>", unsafe_allow_html=True)
    
    is_morning = 4 <= now.hour < 12
    dhikr = "أصبحنا وأصبح الملك لله والحمد لله" if is_morning else "أمسينا وأمسى الملك لله والحمد لله"
    st.markdown(f"<div class='dhikr-box'><b>✨ {'أذكار الصباح' if is_morning else 'أذكار المساء'}:</b><br>{dhikr}</div>", unsafe_allow_html=True)

    # مشاركة واتساب
    share_text = f"مواقيت الصلاة في {selected_state} - {selected_village} لليوم:\n" + "\n".join([f"{k}: {v}" for k,v in prayers.items()])
    whatsapp_url = f"https://wa.me/?text={share_text.replace(' ', '%20').replace(':', '%3A')}"
    st.markdown(f"<a href='{whatsapp_url}' target='_blank'><button style='width:100%; border-radius:15px; background-color:#25D366; color:white; border:none; padding:15px; font-weight:bold; cursor:pointer;'>🟢 مشاركة المواقيت عبر واتساب</button></a>", unsafe_allow_html=True)

else:
    st.info("الرجاء تحديد الموقع من القوائم أعلاه لعرض المواقيت.")
