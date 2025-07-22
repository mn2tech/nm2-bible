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

# Stripe donation links
def launch_checkout(tier):
    links = {
        "supporter": "https://buy.stripe.com/28EfZg6hD1Lk0zsg7pdZ602",
        "sustainer": "https://buy.stripe.com/00w14m5dz4Xw1Dw8EXdZ601",
        "patron":    "https://buy.stripe.com/7sYeVcdK50Hgbe63kDdZ600"
    }
    selected_link = links.get(tier)
    if selected_link:
        st.markdown(f"[🎁 Donate and Unlock Tokens]({selected_link}?success=true&tier={tier})", unsafe_allow_html=True)

# Persistent user ID using localStorage
if "user_id" not in st.session_state:
    result = streamlit_js_eval(js_expressions="window.localStorage.getItem('user_id')")
    if result:
        st.session_state["user_id"] = result
    else:
        new_id = str(uuid.uuid4())
        streamlit_js_eval(js_expressions=f"window.localStorage.setItem('user_id', '{new_id}')")
        st.session_state["user_id"] = new_id

USER_ID = st.session_state["user_id"]

# Token system
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
        cursor.execute("INSERT INTO user_tokens (user_id, tokens_left, last_reset) VALUES (?, ?, ?)", (user_id, MAX_FREE_TOKENS, today))
        conn.commit()
    elif row[1] != today:
        cursor.execute("UPDATE user_tokens SET tokens_left=?, last_reset=? WHERE user_id=?", (MAX_FREE_TOKENS, today, user_id))
        conn.commit()

reset_tokens_if_needed(USER_ID)

def get_tokens(user_id):
    cursor.execute("SELECT tokens_left FROM user_tokens WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def deduct_tokens(user_id, amount):
    cursor.execute("UPDATE user_tokens SET tokens_left = tokens_left - ? WHERE user_id=?", (amount, user_id))
    conn.commit()

# Stripe redirect token addition
query_params = st.query_params
if "success" in query_params and not st.session_state.get("donation_added", False):
    tier = query_params.get("tier", "supporter")
    tier = tier.lower()
    tokens_reward = {"supporter": 50, "sustainer": 150, "patron": 300}.get(tier, 0)
    if tokens_reward:
        cursor.execute("SELECT tokens_left FROM user_tokens WHERE user_id=?", (USER_ID,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE user_tokens SET tokens_left = tokens_left + ? WHERE user_id=?", (tokens_reward, USER_ID))
        else:
            today = datetime.now().date().isoformat()
            cursor.execute("INSERT INTO user_tokens (user_id, tokens_left, last_reset) VALUES (?, ?, ?)", (USER_ID, tokens_reward, today))
        conn.commit()
        st.session_state.donation_added = True
        st.success(f"🎉 Thank you! {tokens_reward} tokens have been added.")

# Manual credit fallback (optional)
if USER_ID == "PASTE-YOUR-TEST-ID-HERE" and not st.session_state.get("manually_credited", False):
    cursor.execute("UPDATE user_tokens SET tokens_left = tokens_left + 50 WHERE user_id=?", (USER_ID,))
    conn.commit()
    st.session_state.manually_credited = True
    st.success("✅ Tokens manually credited. Thank you!")

user_tokens = get_tokens(USER_ID)
st.sidebar.metric("📘 Daily Questions Left", user_tokens)

# Load environment and OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Logo
logo = Image.open("nm2tech_logo.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, use_container_width=False)

st.set_page_config(page_title="NM2TECH AI Bible Assistant", page_icon="💻", layout="centered")
st.markdown("### 📖 Bible Study & Sermon Preparation")
st.markdown("Ask about meaning, context, or theological themes.")

user_question = st.text_input("Ask about scripture meaning, theme, or context:")
qa_lang = st.selectbox("🌍 Response Language:", ["English", "Hindi", "Telugu"], key="qa_lang")

# If out of tokens, prompt payment
if user_tokens < TOKEN_COST:
    st.error("📌 You've reached your daily free questions.")
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
    with st.spinner("Reflecting..."):
        deduct_tokens(USER_ID, TOKEN_COST)
        system_prompt = f"You are a wise AI Bible assistant. Reply faithfully in {qa_lang}."
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
            answer = response.choices[0].message.content.strip()
            st.write("### 📘 Answer")
            st.write(answer)
        except Exception as e:
            st.error("⚠️ Something went wrong.")
            st.exception(e)