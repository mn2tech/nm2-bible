import streamlit as st
from streamlit_chat import message
from openai import OpenAI
from dotenv import load_dotenv
import os
import random

# --- Load environment variables ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Streamlit Config ---
st.set_page_config(page_title="NM2 Bible Chat", layout="centered")

# --- Inject Custom Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f9f7f6;
    color: #333;
}

h1 {
    font-family: 'Playfair Display', serif;
    color: #594f4f;
    text-align: center;
}

.stMarkdown p {
    font-size: 1.05rem;
    line-height: 1.6;
}

div[data-testid="stChatMessage"] {
    border-radius: 10px;
    padding: 0.75em;
    background-color: #fff;
    border: 1px solid #eee;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

a {
    color: #0055a4;
    text-decoration: none;
}

a:hover {
    color: #d9a400;
    text-decoration: underline;
}

.verse-box {
    background-color: #fff6e6;
    color: #594f4f;  /* Ensures visibility in light mode */
    padding: 1em;
    margin-top: 1em;
    border-left: 6px solid #d9a400;
    font-style: italic;
    font-family: 'Playfair Display', serif;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

/* 🌙 Dark mode override */
@media (prefers-color-scheme: dark) {
    .verse-box {
        background-color: #2f2f2f;
        color: #f9f7f6;  /* Light text for dark background */
        border-left: 6px solid #d9a400;
        box-shadow: none;
    }
}

.donation-cta {
    text-align: center;
    font-size: 0.95em;
    color: #666;
    margin-bottom: 1em;
}
</style>
""", unsafe_allow_html=True)

# --- Session state setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- App Header ---
st.title("NM2 Bible Chat")
st.markdown("""
Welcome, beloved seeker.  
This tool was built with prayer and purpose — to guide hearts, encourage reflection, and honor God's Word.
""")

# --- Donation Banner ---
st.markdown("""
<div class='donation-cta'>
If this ministry blesses you, consider <a href='https://buy.stripe.com/28EfZg6hD1Lk0zsg7pdZ602' target='_blank'>supporting our mission</a>.  
Your gift helps us serve more hearts through the Word.
</div>
""", unsafe_allow_html=True)

# --- Verse of the Day + Teaching + Prayer ---
verses_with_teaching = [
    {
        "verse": "“Trust in the Lord with all your heart and lean not on your own understanding.” — Proverbs 3:5",
        "teaching": "Divine wisdom runs deeper than logic. Trust requires surrender — not silence, but strength."
    },
    {
        "verse": "“The Lord is my shepherd; I shall not want.” — Psalm 23:1",
        "teaching": "God’s care is constant. His presence provides even when provision seems absent."
    },
    {
        "verse": "“Let the peace of Christ rule in your hearts.” — Colossians 3:15",
        "teaching": "Peace isn't passive — it's the holy authority of calm amidst chaos."
    }
]
chosen = random.choice(verses_with_teaching)
st.markdown(f"<div class='verse-box'>{chosen['verse']}</div>", unsafe_allow_html=True)
with st.expander("📖 Teach me more"):
    st.markdown(chosen["teaching"])
with st.expander("🙏 A short prayer"):
    st.markdown("""
    Lord, may Your Word take root in my heart today.  
    Guide me, teach me, and help me walk with grace.  
    Thank You for being near, even in silence. Amen.
    """)

# --- Chat Input ---
prompt = st.chat_input("What’s on your heart today?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.spinner("📖 Listening for heavenly wisdom..."):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history,
            temperature=0.7,
        )
        response = completion.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Message History ---
with st.container():
    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=(msg["role"] == "user"), key=str(i))

# --- Footer ---
st.markdown("""
<div style='text-align: center; font-size: 0.8em; color: gray;'>
    Designed by <a href="https://nm2tech.com" target="_blank">NM2TECH</a> • 
    Powered by <a href="https://wordministriesofindia.org" target="_blank">Word Ministries of India Inc.</a><br>
    <em>To God be the glory. Your questions are a sacred offering — thank you for sharing.</em>
</div>
""", unsafe_allow_html=True)