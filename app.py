import streamlit as st
import google.generativeai as genai
import pypdf
from pptx import Presentation

# Configuration de la page
st.set_page_config(page_title="صانع الخرائط الذهنية المرئية", page_icon="🧠", layout="wide")

st.title("🧠 صانع الخرائط الذهنية والمرئية (Mind Map Diagram)")
st.write("ارفع ملفك (PDF, TXT, PPTX) وسيقوم الذكاء الاصطناعي بتحويله إلى خطاطة مرئية بأشكال وأسهم.")

# Clé API dans la barre latérale
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

# Téléversement du fichier (PDF, TXT, PPTX)
uploaded_file = st.file_uploader("اختر ملفاً لرفعه", type=["pdf", "txt", "pptx"])

text_content = ""

if uploaded_file is not None:
    # Lecture des fichiers PDF
    if uploaded_file.name.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
            
    # Lecture des fichiers TXT
    elif uploaded_file.name.endswith(".txt"):
        text_content = uploaded_file.read().decode("utf-8")
        
    # Lecture des fichiers PowerPoint (.pptx)
    elif uploaded_file.name.endswith(".pptx"):
        prs = Presentation(uploaded_file)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text_content += paragraph.text + "\n"

    st.success("تم قراءة الملف بنجاح!")

    # Bouton de génération
    if st.button("🚀 أنشئ الخطاطة المرئية"):
        if not api_key:
            st.error("يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.8-flash")
                
                with st.spinner("جاري رسم وتصميم الخطاطة المرئية..."):
                    prompt = f"""
                    قم بتحليل النص التالي واستخراج الأفكار الرئيسية والفرعية، ثم قم بصياغتها على شكل كود Graphviz DOT فقط لرسم خطاطة ذهنية مرئية (Mind Map Diagram).

                    القواعد والشروط:
                    1. اكتب كود Graphviz DOT فقط ولا تكتب أي نص تفسيري قبله أو بعده.
                    2. ابدأ الكود بـ `digraph G {{` وانته بـ `}}`.
                    3. استخدم الاتجاه الأفقِي `rankdir=LR;`.
                    4. اجعل العقدة الرئيسية (العنوان) في صندوق ملون بارز.
                    5. اربط الأفكار الرئيسية والفرعية بأسهم وشكل أنيق.

                    النص المراد تحليله:
                    \n\n{text_content[:8000]}
                    """
                    
                    response = model.generate_content(prompt)
                    dot_code = response.text.strip()
                    
                    if "```" in dot_code:
                        lines = dot_code.split("\n")
                        dot_code = "\n".join([line for line in lines if not line.startswith("```")])
                    
                    st.subheader("📌 الخطاطة الذهنية المرئية:")
                    st.graphviz_chart(dot_code)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء رسم الخطاطة: {e}")
