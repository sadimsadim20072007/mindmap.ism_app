import streamlit as st
import google.generativeai as genai
import pypdf
import re

# ضبط إعدادات الصفحة
st.set_page_config(page_title="صانع الخرائط الذهنية الذكي", page_icon="🧠", layout="wide")

st.title("🧠 صانع الخرائط الذهنية الذكي عصام")
st.write("ارفع ملفك (PDF أو TXT) وسيقوم الذكاء الاصطناعي بتحليله وتحويله إلى خريطة ذهنية مرئية وملخصة.")

# إدخال مفتاح API في الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    st.markdown("[احصل على مفتاح مجاني من Google AI Studio](https://aistudio.google.com/)")

# رفع الملف
uploaded_file = st.file_uploader("اختر ملفاً لتحليله", type=["pdf", "txt"])

text_content = ""

if uploaded_file is not None:
    # قراءة الملف
    try:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text_content += (page.extract_text() or "") + "\n"
        elif uploaded_file.name.endswith(".txt"):
            text_content = uploaded_file.read().decode("utf-8")

        if not text_content.strip():
            st.warning("⚠️ لم يتم العثور على نص قابل للقراءة في الملف (قد يكون ملف PDF ممسوحاً ضوئياً كصور).")
        else:
            st.success(f"✅ تم قراءة الملف بنجاح! عدد الحروف التقريبي: {len(text_content):,}")

            # زر الإنشاء
            if st.button("🚀 أنشئ الخريطة الذهنية البصرية"):
                if not api_key:
                    st.error("يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-3.8-flash")

                        with st.spinner("جاري تحليل المحتوى وتصميم الخريطة الذهنية..."):
                            # طلب مخرجات Mermaid + ملخص شجري
                            prompt = f"""
                            أنت خبير في التلخيص وتصميم الخرائط الذهنية.
                            قم بقراءة النص التالي واستخراج الأفكار الرئيسية والفرعية بدقة وبشكل هرمي:

                            المطلوب منك:
                            1. توليد كود Mermaid لخريطة ذهنية (Mindmap) داخل كتلة كود ```mermaid.
                               - ابدأ بـ mindmap ثم الفكرة المركزية root((العنوان)) وتفرع منها.
                               - تجنب استخدام الرموز المعقدة أو الأقواس داخل النصوص حتى لا يتعطل كود Mermaid.
                            2. بعد كود الميرميد، اكتب شرحاً شجرياً منظماً بالنقاط والعناوين (Markdown Outline).

                            النص:
                            \"\"\"{text_content[:50000]}\"\"\"
                            """
                            
                            response = model.generate_content(prompt)
                            output = response.text

                            # فصل كود Mermaid عن بقية النص للعرض
                            mermaid_match = re.search(r"```mermaid([\s\S]*?)```", output)
                            
                            tab1, tab2, tab3 = st.tabs(["📊 الخريطة الذهنية (رسم)", "📝 المخطط التفصيلي", "📄 النص الكامل"])

                            with tab1:
                                if mermaid_match:
                                    mermaid_code = mermaid_match.group(1).strip()
                                    # عرض الرسم باستخدام مكون Mermaid المدمج في Streamlit
                                    st.markdown(f"```mermaid\n{mermaid_code}\n```")
                                else:
                                    st.info("لم نتمكن من استخراج كود الرسم تلقائياً، يمكنك مراجعة المخطط في التبويب التالي.")

                            with tab2:
                                # إزالة كود Mermaid لعرض الشرح فقط
                                clean_text = re.sub(r"```mermaid[\s\S]*?```", "", output).strip()
                                st.markdown(clean_text)

                            with tab3:
                                st.code(output, language="markdown")

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاتصال بـ Gemini: {e}")

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
