import streamlit as st
import google.generativeai as genai
import pypdf

# ضبط إعدادات الصفحة
st.set_page_config(page_title="صانع الخرائط الذهنية المرئية", page_icon="🧠", layout="wide")

st.title("🧠 صانع الخرائط الذهنية والمرئية (Mind Map Diagram)")
st.write("ارفع ملفك (PDF أو TXT) وسيقوم الذكاء الاصطناعي بتحويله إلى خطاطة مرئية بأشكال وأسهم.")

# إدخال مفتاح API في القائمة الجانبية
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

# رفع الملف
uploaded_file = st.file_uploader("اختر ملفاً لرفعه", type=["pdf", "txt"])

text_content = ""

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
    elif uploaded_file.name.endswith(".txt"):
        text_content = uploaded_file.read().decode("utf-8")

    st.success("تم قراءة الملف بنجاح!")

    # زر إنشاء الخطاطة المرئية
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
                    
                    # تنظيف الكود من أي علامات تنسيق زائدة
                    if "```" in dot_code:
                        lines = dot_code.split("\n")
                        dot_code = "\n".join([line for line in lines if not line.startswith("```")])
                    
                    st.subheader("📌 الخطاطة الذهنية المرئية:")
                    
                    # عرض الخطاطة الرسمية كشكل بياني أشكال وأسهم
                    st.graphviz_chart(dot_code)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء رسم الخطاطة: {e}")
