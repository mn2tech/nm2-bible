import streamlit as st
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🖼️ Load and Display Logo at the Top Center
logo = Image.open("nm2tech_logo.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, use_column_width=False)

# 🌐 Page Configuration
st.set_page_config(page_title="NM2TECH AI Bible Assistant", page_icon="💻", layout="centered")

# 🎯 Language Selector
language = st.selectbox("🌍 Choose Language:", ["English", "Hindi", "Spanish", "French"])

# 🧠 Page Header
st.markdown("""
    <h1 style='text-align:center; color:#003f63;'>💻 NM2TECH AI Bible Assistant</h1>
    <p style='text-align:center; font-size:18px;'>Explore scripture or ask Bible-related questions using AI. Try: "Interesting facts about the Bible"</p>
""", unsafe_allow_html=True)

# 📜 Section 1: Verse Lookup
st.subheader("📜 Verse Lookup")

version = st.selectbox("Choose Bible Version:", ["KJV", "ASV", "WEB"])
verse_input = st.text_input("Enter a Bible reference (e.g. John 3:16, Psalm 23):")

if verse_input:
    with st.spinner("Searching for scripture..."):
        api_url = f"https://bible-api.com/{verse_input}?translation={version.lower()}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            st.markdown(f"### ✝️ {data['reference']} ({version})")
            st.write(data['text'])
        else:
            st.error("⚠️ Verse not found. Try formatting like 'John 3:16'.")

st.divider()

# 🧠 Section 2: GPT-Powered Q&A
st.subheader("🤖 Ask a Bible Question")
user_question = st.text_input("Ask about meaning, context, or interpretation:")

if user_question:
    with st.spinner("Reflecting thoughtfully..."):
        system_prompt = f"""
You are a wise and compassionate AI Bible assistant. Respond clearly and faithfully in {language}.
You help users understand the Bible’s meaning, structure, authors, historical context, and spiritual themes.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )

            original_answer = response.choices[0].message.content.strip()

            # 🌍 Translate if needed
            translated_answer = original_answer
            if language != "English":
                translation_prompt = f"Translate this to {language}:\n\n{original_answer}"
                translation_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": translation_prompt}],
                    temperature=0.3
                )
                translated_answer = translation_response.choices[0].message.content.strip()

            st.markdown("### 📘 Answer")
            st.write(translated_answer)

        except Exception as e:
            st.error("⚠️ Something went wrong. Please try again.")
            st.exception(e)

# 📌 Disclaimer
st.markdown("""
<hr style="margin-top: 2em; margin-bottom: 0.5em">
<small>
📌 <strong>Disclaimer:</strong> This assistant uses AI and public scripture APIs. It may not reflect every theological tradition. Cross-check for doctrinal study.
</small>
""", unsafe_allow_html=True)

# 👣 Footer
st.markdown("""<hr><center><sub>Powered by <strong>Word Ministries of India</strong></sub></center>""", unsafe_allow_html=True)
st.markdown("""<center><sub>NM2TECH LLC • Technology simplified.</sub></center>""", unsafe_allow_html=True)