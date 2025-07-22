import streamlit as st
import sqlite3
import os
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
from textblob import TextBlob
from streamlit_js_eval import streamlit_js_eval
from PIL import Image

# --- Setup ---
st.set_page_config(layout="wide", page_title="NM2TECH Bible Chat", page_icon="✝️")
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Logo and Sidebar ---
with st.sidebar:
    logo = Image.open("nm2tech_logo.png")
    st.image(logo, width=40)
    st.title("NM2TECH Bible Chat")
    
    if st.button("+ New Chat"):
        st.session_state["messages"] = []

    st.divider()
    st.markdown("🔁 Daily Tokens Reset")
    if "tokens" in st.session_state:
        st.metric("Tokens Left", st.session_state["tokens"])
    st.divider()
    st.caption("Built with ❤️ by NM2TECH")

# --- DB Setup ---
conn = sqlite3.connect("tokens.db")
cursor = conn.cursor()
cursor.executescript("""
CREATE TABLE IF NOT EXISTS user_tokens (
    user_id TEXT PRIMARY KEY,
    tokens_left INTEGER,
    last_reset TEXT
);
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

# --- Token Functions ---
def reset_tokens(user_id):
    today = datetime.now().date().isoformat()
    cursor.execute("SELECT last_reset FROM user_tokens WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row or row[0] != today:
        cursor.execute("REPLACE INTO user_tokens (user_id, tokens_left, last_reset) VALUES (?, ?, ?)", (user_id, 1, today))
        conn.commit()

def get_tokens(user_id):
    cursor.execute("SELECT tokens_left FROM user_tokens WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def deduct_token(user_id):
    cursor.execute("UPDATE user_tokens SET tokens_left = tokens_left - 1 WHERE user_id=?", (user_id,))
    conn.commit()

def save_chat(user_id, role, msg):
    cursor.execute("INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)", (user_id, role, msg))
    conn.commit()

# --- User ID Setup ---
if "user_id" not in st.session_state:
    result = streamlit_js_eval(js_expressions="window.localStorage.getItem('user_id')")
    if result:
        st.session_state["user_id"] = result
    else:
        new_id = str(uuid.uuid4())
        streamlit_js_eval(js_expressions=f"window.localStorage.setItem('user_id', '{new_id}')")
        st.session_state["user_id"] = new_id

USER_ID = st.session_state["user_id"]
reset_tokens(USER_ID)
st.session_state["tokens"] = get_tokens(USER_ID)

# --- Chat UI ---
st.markdown("## ✝️ Bible Chat")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---
prompt = st.chat_input("Ask a Bible question or request a sermon...")

if prompt:
    if st.session_state["tokens"] <= 0:
        st.error("⚠️ Out of tokens. Come back tomorrow or donate to unlock more.")
        st.stop()

    corrected_prompt = str(TextBlob(prompt).correct())

    with st.chat_message("user"):
        st.markdown(corrected_prompt)
    st.session_state["messages"].append({"role": "user", "content": corrected_prompt})
    save_chat(USER_ID, "user", corrected_prompt)

    # --- AI Response ---
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                system_prompt = "You are a Bible-savvy assistant. Answer questions clearly or generate sermons if asked."
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": corrected_prompt}
                ]
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7
                )
                reply = response.choices[0].message.content.strip()
                st.markdown(reply)
                st.session_state["messages"].append({"role": "assistant", "content": reply})
                save_chat(USER_ID, "assistant", reply)
                deduct_token(USER_ID)
                st.session_state["tokens"] -= 1

                # --- If Sermon, allow download ---
                if "sermon" in corrected_prompt.lower() or "points on" in corrected_prompt.lower():
                    st.download_button(
                        label="📄 Download Sermon as PDF",
                        file_name=f"sermon_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        data=reply.encode("utf-8")
                    )
            except Exception as e:
                st.error("Error getting reply.")
                st.exception(e)
