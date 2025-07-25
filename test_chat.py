import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load .env variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="NM2 Bible Chat", layout="centered")

st.title("NM2 Bible Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Display Box
chat_html = """
<style>
#chat-box {
    display: flex;
    flex-direction: column;
    max-height: 400px;
    overflow-y: auto;
    margin: 1rem 0;
    padding: 1rem;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.chat-message {
    margin: 0.5rem 0;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    max-width: 80%;
    word-wrap: break-word;
}
.user {
    background-color: #e1f5fe;
    align-self: flex-end;
}
.assistant {
    background-color: #ede7f6;
    align-self: flex-start;
}
</style>
<div id="chat-box">
"""

for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "assistant"
    chat_html += f"<div class='chat-message {role}'>{msg['content']}</div>"

chat_html += """
</div>
<script>
setTimeout(() => {
    const chatBox = window.parent.document.querySelector("#chat-box");
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
}, 100);
</script>
"""

components.html(chat_html, height=400)

# Input
prompt = st.chat_input("What’s on your heart today?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("💬 Thinking..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.7,
            )
            assistant_text = response.choices[0].message.content
        except Exception as e:
            assistant_text = "⚠️ Something went wrong: " + str(e)

    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
