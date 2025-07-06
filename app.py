import streamlit as st
import requests
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
from openai import OpenAI

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    language = st.selectbox("🌐 Choose Language", ["English", "Hindi", "Spanish", "French"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NM2TECH AI Bible Assistant", page_icon="💻", layout="centered")

logo = Image.open("nm2tech_logo.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, use_container_width=False)
    #st.image("nm2tech_logo.png", width=200)
    st.markdown("""
        <h1 style='color:#003f63;'>💻 NM2TECH AI Bible Assistant</h1>
        <p style='font-size:18px;'>Explore scripture or ask Bible-related questions using AI eg: "Interesting facts about bible"</p>
    """, unsafe_allow_html=True)

# 📜 Section 1: Verse Lookup with Version Selection
st.subheader("📜 Verse Lookup")

# 🔽 Version Selector Dropdown
version = st.selectbox(
    "Choose Bible Version:",
    ["KJV", "ASV", "WEB"],  # Bible-API supported versions
    index=0
)

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
You are a wise and compassionate AI Bible assistant. Answer all responses in {language}. 
You help users understand the Bible’s meaning, structure, authors, historical context, and spiritual themes in simple and encouraging language.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ] 
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        st.markdown("### 📘 Answer")
        st.write(response.choices[0].message.content.strip())

        # 🚦 Your Streamlit app content ends here

st.markdown("""
<hr style="margin-top: 2em; margin-bottom: 0.5em">
<small>
📌 <strong>Disclaimer:</strong> This assistant uses AI and public scripture APIs. It may not reflect every theological tradition. Cross-check for doctrinal study.
</small>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    color: #ffffff;
}

.stTextInput > div > input,
.stSelectbox > div[data-baseweb="select"],
.stTextArea textarea {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border-radius: 6px;
    border: 1px solid #444444;
}

.stButton > button {
    background-color: #007acc;
    color: white;
    font-size: 16px;
    padding: 12px 28px;
    border: none;
    border-radius: 6px;
}

.stButton > button:hover {
    background-color: #005fa3;
}

hr {
    border-top: 1px solid #444444;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    color: #1f1f1f;
    padding: 0px;
    margin: 0px;
}

h1 {
    color: #002b5b;
    font-size: 28px;
}

p {
    color: #444444;
}

.stTextInput > div > input,
.stTextArea textarea,
.stSelectbox > div[data-baseweb="select"] {
    background-color: #f9f9f9;
    color: #1f1f1f;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 15px;
}

div.stButton > button {
    background-color: #0077cc;
    color: #ffffff;
    font-size: 16px;
    border-radius: 8px;
    padding: 12px 28px;
    border: none;
    transition: background-color 0.3s ease;
}

div.stButton > button:hover {
    background-color: #005fa3;
}

.stRadio > div {
    color: #002b5b;
    font-weight: 500;
}

hr {
    border-top: 1px solid #ccc;
    margin-top: 2em;
    margin-bottom: 1em;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
---
<sub><center>Powered by <strong>Word Ministries of India</strong></center></sub>
""", unsafe_allow_html=True)

# 🔻 Then add your footer and style block at the bottom
st.markdown("""
---
<center><sub>NM2TECH LLC • Technology simplified.</sub></center>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Your CSS here... (as you've written it) */
    </style>
""", unsafe_allow_html=True)