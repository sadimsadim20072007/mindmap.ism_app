import streamlit as st
import google.generativeai as genai
import pypdf
from pptx import Presentation
from PIL import Image
from pdf2docx import Converter
import os
import datetime

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="صانع المذكرات والخرائط الذهنية",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق تنسيقات CSS احترافية تطابق التصميم المرفق
st.markdown("""
<style>
    @import url('[suspicious link removed]');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* الهيدر العلوي الأنيق الداكن */
    .hero-header {
        background: linear-gradient(135deg, #0d233a 0%, #17375e 100%);
        color: #ffffff;
        padding: 2.5rem 1.5rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        margin-top: -3rem;
        margin-left: -3rem;
        margin-right: -3rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 1.2rem;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        display: inline-block;
        padding: 0.5rem 1.2rem;
        border-radius: 30px;
        font-size: 0.95rem;
        backdrop-filter: blur(5px);
    }

    /* أزرار مخصصة */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
    }
    
    /* شارة التنبيه والوضع */
    .status-pill {
        background-color: #e6f4ea;
        color: #137333;
        padding: 0.6rem 1.2rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid #ceead6;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 1. الهيدر الداكن الرئيسي (Hero Header)
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🧠 المذكرة اليومية والخرائط الذهنية الذكية</div>
    <div class="hero-subtitle">التوليد التلقائي الشامل وفق مقاربة التدريس والتأطير التربوي المناسب</div>
    <div class="hero-badge">📅 انقر لاختيار التاريخ، ثم ارفع ملفاتك ليتم التوليد والتنسيق تلقائياً</div>
</div>
""", unsafe_allow_html=True)

# القائمة الجانبية لإعداد مفتاح API والخيارات
with st.sidebar:
    st.header("⚙️ الإعدادات العامة")
    api_key = st.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")
    selected_model = st.selectbox("نموذج الذكاء الاصطناعي:", ["gemini-3.8-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
    st.markdown("---")
    [lien suspect supprimé]("💡 يتم استخدام النموذج المحدد لتوليد الخرائط والمذكرات وفق الهيكلة التربوية.")

# حاوية الإدخال والتحكم الرئيسية
col_file, col_date = st.columns([2, 1])

with col_date:
    selected_date = [lien suspect supprimé]_input("📅 اختيار التاريخ", [lien suspect supprimé]())

with col_file:
    uploaded_file = st.file_uploader("📂 إدراج العروض أو المستندات (PDF, PPTX, TXT, PNG, JPG)", type=["pdf", "txt", "pptx", "png", "jpg", "jpeg"])

text_content = ""
image_input = None

if uploaded_file is not None:
    file_ext = [lien suspect supprimé].split(".")[-1].lower()
    
    # قراءة الملف حسب نوعه
    if file_ext == "pdf":
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
    elif file_ext == "txt":
        text_content = [lien suspect supprimé]().decode("utf-8")
    elif file_ext == "pptx":
        prs = Presentation(uploaded_file)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text_content += paragraph.text + "\n"
    elif file_ext in ["png", "jpg", "jpeg"]:
        image_input = [lien suspect supprimé](uploaded_file)

    st.markdown(f"""
    <div class="status-pill">
        ✅ تم تحميل الملف <b>{[lien suspect supprimé]}</b> بنجاح وسيكون التنسيق عمودياً تلقائياً (Portrait).
    </div>
    """, unsafe_allow_html=True)

    # شريط الأزرار الرئيسية المنسق
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        generate_btn = st.button("🪄 توليد المذكرة والخطاطة تلقائياً", type="primary", use_container_width=True)
    with c2:
        convert_btn = st.button("🔄 تحويل PDF إلى Word", use_container_width=True)
    with c3:
        st.caption(f"تاريخ الحصة: {selected_date.strftime('%Y-%m-%d')}")

    # قسم تحويل PDF إلى Word
    if convert_btn:
        if file_ext != "pdf":
            st.warning("يرجى رفع ملف بصيغة PDF للتمكن من تحويله إلى Word.")
        else:
            with st.spinner("جاري التحويل إلى Word..."):
                try:
                    temp_pdf = "temp_input.pdf"
                    temp_docx = "converted_output.docx"
                    
                    with open(temp_pdf, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    cv = Converter(temp_pdf)
                    cv.convert(temp_docx, start=0, end=None)
                    cv.close()
                    
                    with open(temp_docx, "rb") as f:
                        docx_data = [lien suspect supprimé]()
                        
                    st.success("تم التحويل بنجاح!")
                    filename_base = [lien suspect supprimé].rsplit('.', 1)[0]
                    [lien suspect supprimé]_button(
                        label="📥 تحميل مستند Word (.docx)",
                        data=docx_data,
                        file_name=f"{filename_base}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    
                    if os.path.exists(temp_pdf): os.remove(temp_pdf)
                    if os.path.exists(temp_docx): os.remove(temp_docx)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التحويل: {e}")

    # قسم توليد الخريطة والمذكرة
    if generate_btn:
        if not api_key:
            st.error("يرجى إدخال مفتاح Gemini API في القائمة الجانبية أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                
                with st.spinner("جاري تحليل المحتوى وتوليد الخطاطة والمذكرة بالكامل..."):
                    prompt = f"""
                    تاريخ الحصة: {selected_date.strftime('%Y-%m-%d')}
                    قم بتحليل المحتوى المرفق واستخراج خطاطة ومذكرة ذهنية شاملة تتبع بالظبط الهيكلة التالية:

                    1. **العقدة الرئيسية (الموضوع / العنوان)**
                    2. **الفروع الرئيسية الأربعة الإلزامية:**
                       - **الأهداف والمعلومات العامة**
                       - **المراحل والأنشطة الزمنية** (افتتاح الحصة، أنشطة القراءة، أنشطة الكتابة، الاختتام)
                       - **الوسائل والدعامات التربوية**
                       - **التقويم والواجبات المنزلية**

                    قم بصياغة النتيجة كـ كود Graphviz DOT فقط (دون أي نص خارجي)، ابدأ بـ `digraph G {{` وانته بـ `}}`.
                    استخدم الاتجاه الأفقي `rankdir=LR;` وأشكال مستطيلات ملونة لكل فرع.
                    """
                    
                    if image_input:
                        response = model.generate_content([prompt, image_input])
                    else:
                        response = model.generate_content(f"{prompt}\n\nالنص المراد تحليله:\n{text_content[:8000]}")
                    
                    dot_code = response.text.strip()
                    
                    if "```" in dot_code:
                        lines = dot_code.split("\n")
                        dot_code = "\n".join([line for line in lines if not line.startswith("```")])
                    
                    st.markdown("### 📌 المذكرة والخطاطة الذهنية المستخرجة:")
                    st.graphviz_chart(dot_code)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء الرسم والتوليد: {e}")
