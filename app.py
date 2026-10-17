import streamlit as st
import google.generativeai as genai
import pypdf

# ضبط عنوان وتصميم الصفحة
st.set_page_config(page_title="صانع الخرائط الذهنية", page_icon="🧠", layout="centered")

st.title("🧠 صانع الخرائط الذهنية الذكي")
st.write("ارفع ملفك (PDF أو TXT) وسيقوم الذكاء الاصطناعي بتحليله وتحويله إلى خريطة ذهنية مقسمة ومبسطة.")

# إدخال مفتاح API الخاص بـ Gemini في القائمة الجانبية
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

# رفع الملف
uploaded_file = st.file_uploader("اختر ملفاً لرفعه", type=["pdf", "txt"])

text_content = ""

if uploaded_file is not None:
    # قراءة محتوى الملف المرفوع
    if uploaded_file.name.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
    elif uploaded_file.name.endswith(".txt"):
        text_content = uploaded_file.read().decode("utf-8")

    st.success("تم قراءة الملف بنجاح! جاهز للتجميع.")

    # زر إنشاء الخريطة الذهنية
    if st.button("🚀 أنشئ الخريطة الذهنية"):
        if not api_key:
            st.error("يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                # استخدام نموذج gemini-2.0-flash الأحدث والأسرع
                model = genai.GenerativeModel("gemini-2.0-flash")
                
                prompt = f"""
                قم باستخراج الأفكار الرئيسية والفرعية للنص التالي بشكل مركز ومبسط، وصغها على شكل خريطة ذهنية هرمية واضحة ومنظمة باستخدام النقاط والعناوين (Markdown):
                \n\n{text_content[:8000]}
                """
                
                st.subheader("📌 الخريطة الذهنية المستخرجة:")
                
                # توليد النص وبثه مباشرة على الشاشة فور حدوثه (Streaming)
                response = model.generate_content(prompt, stream=True)
                st.write_stream(chunk.text for chunk in response)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
