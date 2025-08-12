import streamlit as st
import time
import base64
import feedparser
from supabase_client import get_comments, add_comment, update_comment, delete_comment, login, logout, get_current_user, login_with_google, handle_oauth_callback

# Set page configuration
st.set_page_config(
    page_title="Bible Assistant & Prayer Timer",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .fullscreen-countdown {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        color: white;
        text-align: center;
    }
    .fullscreen-countdown h1 {
        font-size: 8rem;
        margin: 0;
        font-weight: 300;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .gentle-message {
        font-size: 1.5rem;
        margin-top: 2rem;
        max-width: 600px;
        line-height: 1.6;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🙏 Bible Assistant & Prayer Timer")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Home", "📖 Bible Q&A", "💭 Meditation Generator", "⏰ Prayer Timer", "📚 Daily Devotional", "💬 Community"])

# Tab 4: Prayer Timer with SIMPLIFIED music control
with tab4:
    st.header("⏰ Prayer Timer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration_minutes = st.selectbox("Prayer Duration", [1, 2, 5, 10, 15, 20, 30], index=2)
        duration_seconds = duration_minutes * 60
        
        play_music = st.checkbox("🎵 Play Background Music", value=True)
        play_lords_prayer = st.checkbox("🙏 Play Lord's Prayer", value=False)
        
    with col2:
        start_timer = st.button("🕰️ Start Prayer Timer", use_container_width=True, type="primary")
    
    # Instructions
    st.info("🎵 **Music will automatically stop when the timer ends!** Click the button above to start your prayer time.")
    
    # Initialize session state
    if 'music_should_play' not in st.session_state:
        st.session_state.music_should_play = False
    
    if start_timer:
        st.session_state.music_should_play = True
        
        # Display initial message
        st.markdown(
            "<b>🔥 Come As You Are </b><br>"
            "Why set a timer to meet God? Because stillness rarely finds us on its own—we must choose it. In these few minutes, time won't race past. It will settle. It will breathe.<br>"
            "Don't ask. Just be. Let your heart rest in His presence.<br>"
            "It doesn't matter what burdens you carry or what mistakes you made today—come as you are. God already knows. What He desires most is your presence."
        )
        
        # Show music players (ONLY when supposed to play)
        if st.session_state.music_should_play:
            if play_music:
                try:
                    with open("silent-evening-calm-piano-335749.mp3", "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=True)
                    st.info("🎵 Prayer music is playing...")
                except:
                    st.warning("Background music file not found")
            
            if play_lords_prayer:
                try:
                    st.audio("audio_The_Lords_Prayer.mp3", format="audio/mp3", autoplay=True, loop=True)
                    st.info("🙏 Lord's Prayer is playing...")
                except:
                    st.warning("Lord's Prayer audio file not found")
        
        # Countdown timer
        countdown_placeholder = st.empty()
        
        # Timer loop
        for t in range(duration_seconds, -1, -1):
            mins, secs = divmod(t, 60)
            
            # Update countdown
            countdown_placeholder.markdown(
                f"""
                <div class='fullscreen-countdown'>
                    <h1>{mins}:{secs:02d}</h1>
                    <div class='gentle-message'>Be still and know that I am God... {mins}:{secs:02d} remaining</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            time.sleep(1)
        
        # STOP MUSIC BY SETTING SESSION STATE
        st.session_state.music_should_play = False
        
        # Show completion message
        countdown_placeholder.markdown(
            """
            <div class='fullscreen-countdown'>
                <h1>🙏</h1>
                <div class='gentle-message'>Prayer time complete. Music has stopped automatically.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # JavaScript to force stop any remaining audio
        st.components.v1.html("""
        <script>
        // Stop all audio elements
        document.querySelectorAll('audio').forEach(audio => {
            audio.pause();
            audio.currentTime = 0;
            audio.volume = 0;
        });
        console.log("All audio stopped");
        </script>
        """, height=0)
        
        time.sleep(3)
        st.rerun()

# Other tabs remain the same...
with tab1:
    st.header("🏠 Welcome")
    st.write("Welcome to your personal Bible Assistant and Prayer Timer!")

with tab2:
    st.header("📖 Bible Q&A")
    st.write("Ask questions about the Bible here.")

with tab3:
    st.header("💭 Meditation Generator")
    st.write("Generate personalized meditations here.")

with tab5:
    st.header("📚 Daily Devotional")
    st.write("Read daily devotionals here.")

with tab6:
    st.header("💬 Community")
    st.write("Connect with the community here.")
