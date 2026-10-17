import streamlit as st
import google.generativeai as genai
import pypdf

# Configuration de la page
st.set_page_config(page_title="Générateur de Cartes Mentales Structurées", page_icon="🧠", layout="centered")

st.title("🧠   صانع الخرائط الذهنية الهيكلية عصام")
st.write("ارفع ملفك (PDF أو TXT) وسيقوم الذكاء الاصطناعي بتحليله وتنظيمه وفق هيكلة منظمة ومقسمة.")

# Clé API dans la barre latérale
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

# Téléversement du fichier
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

    # Bouton de génération
    if st.button("🚀 أنشئ الخريطة الذهنية الهيكلية"):
        if not api_key:
            st.error("يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.8-flash")
                
                # Prompt structuré selon le modèle de fiche
                prompt = f"""
                قم بتحليل النص التالي واستخراج خريطة ذهنية هيكلية ومقسمة بوضوح إلى الفئات الرئيسية التالية:
                
                1. 🎯 **الأهداف والمعلومات العامة (Objectifs & Infos)**
                2. ⏱️ **المراحل والأنشطة الزمنية (Phases Chronologiques)**
                3. 🛠️ **الوسائل والدعامات المستعملة (Supports & Outils)**
                4. 📝 **التقويم والواجبات المنزلية (Évaluation & Devoirs)**

                صغ النتيجة على شكل شجرة خريطة ذهنية مقسمة باستعمال العناوين، النقاط والرموز التعبيرية (Markdown).

                النص:
                \n\n{text_content[:8000]}
                """
                
                st.subheader("📌 الخريطة الذهنية الهيكلية:")
                
                # Affichage en streaming
                response = model.generate_content(prompt, stream=True)
                st.write_stream(chunk.text for chunk in response)
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
