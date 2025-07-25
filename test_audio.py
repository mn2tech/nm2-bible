import streamlit as st
import time

st.title("⏰ Custom Alarm Timer Test")

audio_files = [
    "silent-evening-calm-piano-335749.mp3",
    "single-church-bell-2-352062.mp3"
]

selected = st.selectbox("Choose an alarm sound:", audio_files)
duration_minutes = st.slider("Set timer duration (minutes)", 1, 10, 1)

if st.button("Start Timer"):
    timer_placeholder = st.empty()
    total_seconds = duration_minutes * 60
    for t in range(total_seconds, -1, -1):
        mins, secs = divmod(t, 60)
        timer_placeholder.markdown(f"<h1 style='text-align:center;'>{mins}:{secs:02d}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    timer_placeholder.markdown("<h1 style='text-align:center;'>⏰ Time's up!</h1>", unsafe_allow_html=True)
    st.audio(selected, format="audio/mp3")
    st.info("If the alarm does not play automatically, please click the play button above.")
    st.markdown(
        """
        <script>
        alert("⏰ Time's up!");
        </script>
        """,
        unsafe_allow_html=True
    )