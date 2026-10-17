import streamlit as st
import google.generativeai as genai
import pypdf
from pptx import Presentation
from PIL import Image
from pdf2docx import Converter
import os

# إعدادات الصفحة
st.set_page_config(page_title="صانع الخرائط الذهنية ومحول الملفات", page_icon="🧠", layout="wide")

st.title("🧠 صانع الخرائط الذهنية وتحويل PDF إلى Word")
st.write("ارفع ملفك لإنشاء خطاطة ذهنية مرئية أو لتحويل ملفات PDF إلى مستندات Word قابلة للتعديل.")

# مفتاح API
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

# رفع الملفات والصور
uploaded_file = st.file_uploader("اختر ملفاً أو صورة لرفعها", type=["pdf", "txt", "pptx", "png", "jpg", "jpeg"])

text_content = ""
image_input = None

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    
    # قراءة ومعالجة ملفات PDF
    if file_ext == "pdf":
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
            
        # قسم تحويل PDF إلى Word
        st.markdown("---")
        st.subheader("📄 تحويل ملف PDF إلى Word (.docx)")
        if st.button("🔄 تحويل هذا الملف إلى Word"):
            with st.spinner("جاري تحويل الملف... قد يستغرق ذلك بضع ثوانٍ"):
                try:
                    temp_pdf = "temp_input.pdf"
                    temp_docx = "converted_output.docx"
                    
                    with open(temp_pdf, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    cv = Converter(temp_pdf)
                    cv.convert(temp_docx, start=0, end=None)
                    cv.close()
                    
                    with open(temp_docx, "rb") as f:
                        docx_data = f.read()
                        
                    st.success("تم تحويل الملف بنجاح!")
                    
                    filename_base = uploaded_file.name.rsplit('.', 1)[0]
                    st.download_button(
                        label="📥 تحميل مستند Word (.docx)",
                        data=docx_data,
                        file_name=f"{filename_base}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
                    if os.path.exists(temp_docx):
                        os.remove(temp_docx)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التحويل: {e}")
        st.markdown("---")

    # قراءة ملفات TXT
    elif file_ext == "txt":
        text_content = uploaded_file.read().decode("utf-8")
        
    # قراءة ملفات PPTX
    elif file_ext == "pptx":
        prs = Presentation(uploaded_file)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text_content += paragraph.text + "\n"
                        
    # قراءة الصور
    elif file_ext in ["png", "jpg", "jpeg"]:
        image_input = Image.open(uploaded_file)
        st.image(image_input, caption="الصورة المرفوعة", width=400)

    st.success("تم قراءة الملف بنجاح!")

    # زر إنشاء الخطاطة المرئية
    if st.button("🚀 أنشئ الخطاطة المرئية"):
        if not api_key:
            st.error("يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                # استخدام النموذج المحدد gemini-3.8-flash
                model = genai.GenerativeModel("gemini-3.8-flash")
                
                with st.spinner("جاري تصميم الخطاطة..."):
                    prompt = """
                    قم بتحليل المحتوى واستخراج خطاطة ذهنية تتبع بالظبط الهيكلة التالية:

                    1. **العقدة الرئيسية (الموضوع / العنوان)**
                    2. **الفروع الرئيسية الأربعة الإلزامية:**
                       - **الأهداف والمعلومات العامة**
                       - **المراحل والأنشطة الزمنية** (افتتاح الحصة، أنشطة القراءة، أنشطة الكتابة، الاختتام)
                       - **الوسائل والدعامات التربوية**
                       - **التقويم والواجبات المنزلية**

                    قم بصياغة النتيجة كـ كود Graphviz DOT فقط (دون أي نص خارجي)، ابدأ بـ `digraph G {` وانته بـ `}`.
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
                    
                    st.subheader("📌 الخطاطة الذهنية المرئية:")
                    st.graphviz_chart(dot_code)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء رسم الخطاطة: {e}")
