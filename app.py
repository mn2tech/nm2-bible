import streamlit as st
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import sqlite3
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
import uuid

# 🌟 Stripe donation links
def launch_checkout(tier):
    links = {
        "supporter": "https://buy.stripe.com/test_28E3cu0Xr5rC5dT3gfds401",
        "sustainer": "https://buy.stripe.com/test_6oUfZg7lP6vGgWB043ds402",
        "patron":    "https://buy.stripe.com/test_aFacN46hLbQ0ayd4kjds403"
    }
    selected_link = links.get(tier)
    if selected_link:
        st.markdown(f"🎁 [Click here to donate and unlock more tokens]({selected_link})", unsafe_allow_html=True)

# 🌐 Persistent User ID
if "user_id" not in st.session_state:
    result = streamlit_js_eval(js_expressions="window.localStorage.getItem('user_id')")
    if result:
        st.session_state["user_id"] = result
    else:
        new_id = str(uuid.uuid4())
        streamlit_js_eval(js_expressions=f"window.localStorage.setItem('user_id', '{new_id}')")
        st.session_state["user_id"] = new_id

USER_ID = st.session_state["user_id"]

# 📘 Token Setup
MAX_FREE_TOKENS = 1
TOKEN_COST = 1
conn = sqlite3.connect("tokens.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_tokens (
    user_id TEXT PRIMARY KEY,
    tokens_left INTEGER,
    last_reset TEXT
)
""")
conn.commit()

def reset_tokens_if_needed(user_id):
    today = datetime.now().date().isoformat()
    cursor.execute("SELECT tokens_left, last_reset FROM user_tokens WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        # First-time user — create entry
        cursor.execute("INSERT INTO user_tokens (user_id, tokens_left, last_reset) VALUES (?, ?, ?)",
                       (user_id, MAX_FREE_TOKENS, today))
        conn.commit()
    elif row[1] != today:
        # Only reset if last reset ≠ today
        cursor.execute("UPDATE user_tokens SET tokens_left=?, last_reset=? WHERE user_id=?",
                       (MAX_FREE_TOKENS, today, user_id))
        conn.commit()

def get_tokens(user_id):
    cursor.execute("SELECT tokens_left FROM user_tokens WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def deduct_tokens(user_id, amount):
    cursor.execute("UPDATE user_tokens SET tokens_left = tokens_left - ? WHERE user_id=?", (amount, user_id))
    conn.commit()

user_tokens = get_tokens(USER_ID)
st.sidebar.metric("📘 Daily Questions Left", user_tokens)

# 🧠 API & Setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🖼️ Logo
logo = Image.open("nm2tech_logo.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, use_container_width=False)

# 🌐 Page Config
st.set_page_config(page_title="NM2TECH AI Bible Assistant", page_icon="💻", layout="centered")

# 🧠 Header
st.markdown("""
<h1 style='text-align:center; color:#003f63;'>💻 NM2TECH AI Bible Assistant</h1>
<p style='text-align:center; font-size:18px;'>Explore scripture or ask Bible-related questions using AI. Try: "Interesting facts about the Bible"</p>
""", unsafe_allow_html=True)

# 📜 Verse Lookup
st.subheader("📜 Verse Lookup")
version = st.selectbox("Choose Bible Version:", ["KJV", "ASV", "WEB"])
verse_input = st.text_input("Enter a Bible reference (e.g. John 3:16, Psalm 23):")
col1, col2, col3 = st.columns([3, 1.2, 0.2])
with col2:
    verse_lang = st.selectbox("🌍 Lang", ["English", "Hindi", "Telugu"], key="verse_lang")

if verse_input:
    with st.spinner("Searching for scripture..."):
        api_url = f"https://bible-api.com/{verse_input}?translation={version.lower()}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            st.markdown(f"### ✝️ {data['reference']} ({version})")
            original_verse = data['text']
            translated_verse = original_verse
            if verse_lang != "English":
                try:
                    translation_prompt = f"Translate this Bible verse into {verse_lang}:\n\n{original_verse}"
                    translation_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": translation_prompt}],
                        temperature=0.3
                    )
                    translated_verse = translation_response.choices[0].message.content.strip()
                except Exception as e:
                    st.warning("⚠️ Translation failed. Showing verse in English.")
                    st.exception(e)
            st.markdown("**📝 English:**")
            st.write(original_verse)
            if verse_lang != "English":
                st.markdown(f"**🌐 {verse_lang}:**")
                st.write(translated_verse)
        else:
            st.error("⚠️ Verse not found. Try formatting like 'John 3:16'.")

st.divider()

# 🤖 GPT-Powered Q&A
st.subheader("📘 Bible Study & Sermon Preparation")
st.markdown("_Ask about meaning, context, interpretation, or theological themes to prepare your message._ eg: Type 'Sermon on joy'")
user_question = st.text_input("Ask about meaning, context, or interpretation:")
col1, col2, col3 = st.columns([3, 1.2, 0.2])
with col2:
    qa_lang = st.selectbox("🌍 Select Answer Language:", ["English", "Hindi", "Telugu"], key="qa_lang")

# 💳 Show donation options if tokens exhausted
if user_tokens < TOKEN_COST:
    st.error("📌 You've reached your daily free questions.")

    st.markdown("### 💝 Support the AI Bible Assistant")
    st.markdown("Choose a donation tier to continue your spiritual exploration:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💖 Supporter $1.99 (+50)"):
            launch_checkout("supporter")
    with col2:
        if st.button("🌟 Sustainer $4.99 (+150)"):
            launch_checkout("sustainer")
    with col3:
        if st.button("👑 Patron $8.99 (+300)"):
            launch_checkout("patron")
    st.stop()

if user_question:
    with st.spinner("Reflecting thoughtfully..."):
        deduct_tokens(USER_ID, TOKEN_COST)
        system_prompt = f"""
You are a wise and compassionate AI Bible assistant. Respond clearly and faithfully in {qa_lang}.
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
            translated_answer = original_answer
            if qa_lang != "English":
                translation_prompt = f"Translate this to {qa_lang}:\n\n{original_answer}"
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

# 📌 Disclaimer & Footer
st.markdown("""
<hr style="margin-top: 2em; margin-bottom: 0.5em">
<small>
📌 <strong>Disclaimer:</strong> This assistant uses AI and public scripture APIs. It may not reflect every theological tradition. Cross-check for doctrinal study.
</small>
""", unsafe_allow_html=True)
st.markdown("""<hr><center><sub>Powered by <strong>Word Ministries of India</strong></sub></center>""", unsafe_allow_html=True)
st.markdown("""<center><sub>NM2TECH LLC • Technology simplified.</sub></center>""", unsafe_allow_html=True)