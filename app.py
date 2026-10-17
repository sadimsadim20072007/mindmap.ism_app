import streamlit as st
import google.generativeai as genai
from pptx import Presentation
import json
import datetime
import os

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="المدرسة الرائدة - المذكرة اليومية الذكية",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تطبيق تنسيقات CSS احترافية
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #f4f7f9;
    }

    /* الشريط العلوي */
    .top-toolbar {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* شارة التنبيه */
    .auto-badge {
        background-color: #e6f4ea;
        color: #137333;
        border: 1px solid #ceead6;
        padding: 8px 16px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* بطاقات المواد الملونة */
    .subject-card {
        border-radius: 10px;
        padding: 12px;
        color: #1a1a1a;
        height: 100%;
    }

    .card-fr { background-color: #f5edf7; border: 2px solid #8e44ad; }
    .card-ar { background-color: #eaf5ea; border: 2px solid #27ae60; }
    .card-math { background-color: #eaf2f8; border: 2px solid #2980b9; }

    .card-fr .sec-header { background-color: #8e44ad; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .card-ar .sec-header { background-color: #27ae60; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }
    .card-math .sec-header { background-color: #2980b9; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; }

    .meta-bar { background: rgba(0,0,0,0.05); padding: 5px 10px; border-radius: 5px; font-size: 0.85rem; margin-bottom: 10px; font-weight: 600; }
    .time-badge { float: left; background: rgba(255,255,255,0.8); color: #333; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; }
    
    .stButton>button { border-radius: 8px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# الشريط الجانبي لإعداد مفتاح API
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    api_key = st.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")
    model_name = st.selectbox("النموذج المستخدم:", ["gemini-3.8-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
    st.markdown("---")
    st.info("💡 تحليلات المذكرة اليومية لمؤسسات الريادة.")

# 1. شريط العرض العلوي مع اللوجو والترويسة الرسمية
st.markdown('<div class="top-toolbar">', unsafe_allow_html=True)

header_col1, header_col2 = st.columns([1, 4])

with header_col1:
    # عرض شعار الوزارة من المجلد عند رفعه إلى GitHub
    if os.path.exists("logo.png"):
        st.image("logo.png", width=170)
    elif os.path.exists("logo_ministère.jpg"):
        st.image("logo_ministère.jpg", width=170)
    else:
        st.markdown("🏛️ **شعار الوزارة**")

with header_col2:
    st.markdown("### المملكة المغربية - وزارة التربية الوطنية والتعليم الأولي والرياضة")
    st.markdown("#### 🏫 المدرسة الرائدة | المذكرة اليومية الذكية")

st.markdown("---")

# أدوات التحكم ورفع الملفات
row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns([2.5, 1.8, 2, 1.2, 1.2])

with row1_col1:
    uploaded_files = st.file_uploader("💻 إدراج العروض التقديمية (PPTX)", type=["pptx", "pdf"], accept_multiple_files=True, label_visibility="collapsed")

with row1_col2:
    selected_date = st.date_input("📅 اختيار التاريخ", datetime.date.today(), label_visibility="collapsed")

with row1_col3:
    generate_btn = st.button("🪄 توليد المذكرة تلقائياً", type="primary", use_container_width=True)

with row1_col4:
    st.button("📚 مكتبتي", use_container_width=True)

with row1_col5:
    st.button("💾 حفظ", use_container_width=True)

st.markdown('<div class="auto-badge">✅ تم إدراج شعار الوزارة الرسمي وإعداد التنسيق التلقائي</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# استخراج النص من العروض
all_slides_text = ""
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pptx"):
            prs = Presentation(uploaded_file)
            all_slides_text += f"\n--- ملف: {uploaded_file.name} ---\n"
            for i, slide in enumerate(prs.slides):
                all_slides_text += f"شريحة {i+1}:\n"
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            all_slides_text += paragraph.text + "\n"

# زر التوليد
if generate_btn:
    if not api_key:
        st.error("يرجى إدخال مفتاح Gemini API في القائمة الجانبية أولاً.")
    elif not uploaded_files:
        st.warning("يرجى إدراج ملفات العروض التقديمية (PPTX) أولاً.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            with st.spinner("جاري استخراج البيانات وتنسيق المذكرة اليومية للأعمدة الثلاثة..."):
                prompt = f"""
                أنت خبير تربوي متخصص في إعداد مذكرات "المدرسة الرائدة" (فترة دعم تعلمات الأساس).
                قم بتحليل محتوى العروض التقديمية واستخراج المذكرة اليومية بالضبط لـ 3 مواد:
                
                تاريخ اليوم: {selected_date.strftime('%Y-%m-%d')}

                استخرج البيانات واسترجعها في صيغة JSON حصرية بالهيكل التالي:
                {{
                  "francais": {{
                    "level": "Niv: 5",
                    "palier": "Pal: 1",
                    "sequence": "Séa: 3",
                    "objectifs": "الأهداف التعليمية للمادة...",
                    "step1_title": "1. Rituel d'ouverture",
                    "step1_duration": "10 min",
                    "step1_desc": "أنشطة الافتتاح والتهيئة...",
                    "step2_title": "2. Activité principale / Vocabulaire",
                    "step2_duration": "30 min",
                    "step2_desc": "الأنشطة والتمارين الرئيسية...",
                    "step3_title": "3. Evaluation & Clôture",
                    "step3_duration": "15 min",
                    "step3_desc": "أنشطة التقويم والختام..."
                  }},
                  "arabic": {{
                    "level": "المستوى: 5",
                    "labna": "اللبنة: التمكن",
                    "hissa": "الحصة: 1",
                    "objectifs": "الأهداف التربوية المحددة...",
                    "step1_title": "1. افتتاح الحصة",
                    "step1_duration": "15 د",
                    "step1_desc": "أنشطة التهيئة وقراءة اللوحة...",
                    "step2_title": "2. أنشطة قرائية",
                    "step2_duration": "30 د",
                    "step2_desc": "قراءة النصوص والكلمات والتطبيقات...",
                    "step3_title": "3. أنشطة كتابية وتقويم",
                    "step3_duration": "15 د",
                    "step3_desc": "النقل والإنتاج والتقويم..."
                  }},
                  "math": {{
                    "level": "المستوى: 5",
                    "labna": "اللبنة: الأعداد الصحيحة",
                    "hissa": "الحصة: 1",
                    "objectifs": "أهداف درس الرياضيات...",
                    "step1_title": "1. الحساب الذهني والافتتاح",
                    "step1_duration": "15 د",
                    "step1_desc": "أنشطة الحساب الذهني السريع...",
                    "step2_title": "2. النشاط الرئيسي",
                    "step2_duration": "30 د",
                    "step2_desc": "بناء المفهوم وحل المسائل...",
                    "step3_title": "3. تقويم ودعم",
                    "step3_duration": "15 د",
                    "step3_desc": "أنشطة التقويم الفردي والدعم..."
                  }}
                }}

                اكتب كود JSON فقط دون أي نصوص إضافية.
                نص الشرائح للتحليل:
                {all_slides_text[:10000]}
                """
                
                response = model.generate_content(prompt)
                res_text = response.text.strip()
                
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                elif "```" in res_text:
                    res_text = res_text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(res_text)
                
                # عرض شريط المذكرة اليومية مع اللوجو
                st.markdown(f"""
                <div style="background: #ffffff; border: 2px solid #dcdfe3; border-radius: 12px; padding: 15px; margin-top: 15px;">
                    <div style="background: #0d233a; color: #ffffff; padding: 12px 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 1.1rem; margin-bottom: 15px;">
                        <div>🏫 المملكة المغربية - وزارة التربية الوطنية والتعليم الأولي والرياضة | المذكرة اليومية - المدرسة الرائدة</div>
                        <div>📅 التاريخ: {selected_date.strftime('%Y-%m-%d')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_fr, col_ar, col_ma = st.columns(3)
                
                # عمود Français
                with col_fr:
                    fr = data.get("francais", {})
                    st.markdown(f"""
                    <div class="subject-card card-fr">
                        <div class="sec-header">Français</div>
                        <div class="meta-bar">{fr.get('level', '')} | {fr.get('palier', '')} | {fr.get('sequence', '')}</div>
                        <div style="font-weight:bold; color:#8e44ad;">🎯 Objectifs:</div>
                        <p style="font-size:0.9rem;">{fr.get('objectifs', '')}</p>
                        <hr style="border-color:#8e44ad;">
                        <div>
                            <strong>{fr.get('step1_title', '')}</strong>
                            <span class="time-badge">{fr.get('step1_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{fr.get('step1_desc', '')}</p>
                        </div>
                        <hr style="border-color:#8e44ad;">
                        <div>
                            <strong>{fr.get('step2_title', '')}</strong>
                            <span class="time-badge">{fr.get('step2_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{fr.get('step2_desc', '')}</p>
                        </div>
                        <hr style="border-color:#8e44ad;">
                        <div>
                            <strong>{fr.get('step3_title', '')}</strong>
                            <span class="time-badge">{fr.get('step3_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{fr.get('step3_desc', '')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # عمود اللغة العربية
                with col_ar:
                    ar = data.get("arabic", {})
                    st.markdown(f"""
                    <div class="subject-card card-ar">
                        <div class="sec-header">اللغة العربية</div>
                        <div class="meta-bar">{ar.get('level', '')} | {ar.get('labna', '')} | {ar.get('hissa', '')}</div>
                        <div style="font-weight:bold; color:#27ae60;">🎯 الأهداف:</div>
                        <p style="font-size:0.9rem;">{ar.get('objectifs', '')}</p>
                        <hr style="border-color:#27ae60;">
                        <div>
                            <strong>{ar.get('step1_title', '')}</strong>
                            <span class="time-badge">{ar.get('step1_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{ar.get('step1_desc', '')}</p>
                        </div>
                        <hr style="border-color:#27ae60;">
                        <div>
                            <strong>{ar.get('step2_title', '')}</strong>
                            <span class="time-badge">{ar.get('step2_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{ar.get('step2_desc', '')}</p>
                        </div>
                        <hr style="border-color:#27ae60;">
                        <div>
                            <strong>{ar.get('step3_title', '')}</strong>
                            <span class="time-badge">{ar.get('step3_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{ar.get('step3_desc', '')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # عمود الرياضيات
                with col_ma:
                    ma = data.get("math", {})
                    st.markdown(f"""
                    <div class="subject-card card-math">
                        <div class="sec-header">الرياضيات</div>
                        <div class="meta-bar">{ma.get('level', '')} | {ma.get('labna', '')} | {ma.get('hissa', '')}</div>
                        <div style="font-weight:bold; color:#2980b9;">🎯 الأهداف:</div>
                        <p style="font-size:0.9rem;">{ma.get('objectifs', '')}</p>
                        <hr style="border-color:#2980b9;">
                        <div>
                            <strong>{ma.get('step1_title', '')}</strong>
                            <span class="time-badge">{ma.get('step1_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{ma.get('step1_desc', '')}</p>
                        </div>
                        <hr style="border-color:#2980b9;">
                        <div>
                            <strong>{ma.get('step2_title', '')}</strong>
                            <span class="time-badge">{ma.get('step2_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{ma.get('step2_desc', '')}</p>
                        </div>
                        <hr style="border-color:#2980b9;">
                        <div>
                            <strong>{ma.get('step3_title', '')}</strong>
                            <span class="time-badge">{ma.get('step3_duration', '')}</span>
                            <p style="font-size:0.85rem; margin-top:5px;">{ma.get('step3_desc', '')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة العروض: {e}")
