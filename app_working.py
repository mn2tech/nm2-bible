import streamlit as st
from streamlit_chat import message
from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import requests
import feedparser
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import time
import json
from supabase_client import (
    login,
    login_with_google,
    logout,
    get_current_user,
    handle_oauth_callback,
    add_comment,
    get_comments,
    update_comment,
    delete_comment,
)


COMMENTS_FILE = "comments.json"

def load_comments():
    try:
        with open(COMMENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_comments(comments):
    with open(COMMENTS_FILE, "w") as f:
        json.dump(comments, f, indent=2)

# --- Load environment variables ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Streamlit Config ---
st.set_page_config(page_title="NM2 Bible Chat (Beta)", layout="centered")

# --- Custom Styling ---
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
    color: #594f4f;
    padding: 1em;
    margin-top: 1em;
    border-left: 6px solid #d9a400;
    font-style: italic;
    font-family: 'Playfair Display', serif;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.donation-cta {
    text-align: center;
    font-size: 0.95em;
    color: #666;
    margin-bottom: 1em;
}
.comment-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    padding: 1em 1.2em;
    margin-bottom: 1.2em;
    font-family: 'Inter', sans-serif;
}
.comment-meta {
    color: #7c7c7c;
    font-size: 0.98em;
    margin-bottom: 0.3em;
    font-family: 'Inter', sans-serif;
}
.comment-actions {
    margin-top: 0.5em;
}
body, .stApp {
    background-image: url('prayer.png');
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;
}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Authentication Sidebar ---
with st.sidebar:
    st.markdown("### 👤 User Login (Optional)")
    
    # Simple local authentication fallback
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    
    if st.session_state.logged_in_user:
        st.success(f"Welcome, {st.session_state.logged_in_user}")
        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.success("✅ Logged out successfully!")
            st.rerun()
    else:
        st.markdown("#### 📧 Simple Login")
        login_email = st.text_input("Email", key="login_email")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            if login_email.strip():
                st.session_state.logged_in_user = login_email.strip()
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Please enter an email")
        
        st.markdown("---")
        st.markdown("#### 🌐 Quick Guest Login")
        if st.button("🔗 Login as Guest", key="guest_login"):
            st.session_state.logged_in_user = "guest@example.com"
            st.success("✅ Logged in as guest!")
            st.rerun()
        
        st.info("💡 **Note**: Authentication is currently in simple mode. Any email will work for testing.")

# --- Login Status Indicator ---
if st.session_state.get("logged_in_user"):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.success(f"👋 Welcome back, **{st.session_state.logged_in_user}**! You are logged in.")
    with col2:
        if st.button("🚪 Logout", type="secondary", key="main_logout"):
            st.session_state.logged_in_user = None
            st.success("👋 You have been logged out!")
            st.rerun()
else:
    st.info("👋 Welcome! You can login in the sidebar for additional features.")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 Bible Chat (Beta)",
    "📰 Bible News",
    "📖 Bible Reading Room",
    "🙏 Prayer Room",         # ← Prayer hands emoji
    "📆 Daily Devotional",   # ← Calendar emoji
    "💬 Comments"
])

# --- Tab 1: Bible Chat Experience ---
with tab1:
    st.title("NM2 Bible Chat")
    st.markdown("Welcome, beloved seeker. This tool was built with prayer and purpose — to guide hearts, encourage reflection, and honor God's Word.")

    st.markdown("""
    <div class='donation-cta'>
    If this ministry blesses you, consider <a href='https://buy.stripe.com/28EfZg6hD1Lk0zsg7pdZ602' target='_blank'>supporting our mission</a>.  
    Your gift helps us serve more hearts through the Word.
    </div>
    """, unsafe_allow_html=True)

    verses = [
        {
            "verse": ""Trust in the Lord with all your heart and lean not on your own understanding." — Proverbs 3:5",
            "teaching": "Divine wisdom runs deeper than logic. Trust requires surrender — not silence, but strength."
        },
        {
            "verse": ""The Lord is my shepherd; I shall not want." — Psalm 23:1",
            "teaching": "God's care is constant. His presence provides even when provision seems absent."
        },
        {
            "verse": ""Let the peace of Christ rule in your hearts." — Colossians 3:15",
            "teaching": "Peace isn't passive — it's the holy authority of calm amidst chaos."
        }
    ]
    chosen = random.choice(verses)
    st.markdown(f"<div class='verse-box'>{chosen['verse']}</div>", unsafe_allow_html=True)
    with st.expander("📖 Teach me more"):
        st.markdown(chosen["teaching"])
    with st.expander("🙏 A short prayer"):
        st.markdown("""Lord, may Your Word take root in my heart today.  
        Guide me, teach me, and help me walk with grace.  
        Thank You for being near, even in silence. Amen.""")

    prompt = st.chat_input("What's on your heart today?")
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

    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=(msg["role"] == "user"), key=str(i))

# --- Tab 2: Bible News with Embedded Images ---
with tab2:
    st.subheader("📰 Global Bible News & Updates")
    feed_urls = [
        "https://harbingersdaily.com/feed/",
        "https://livinghisword.org/feed/",
        "https://www.crosswalk.com/rss/feeds/headlines.xml"
    ]

    def fetch_feed_items(url, max_items=3):
        feed = feedparser.parse(url)
        return feed.entries[:max_items]

    for url in feed_urls:
        items = fetch_feed_items(url)
        for item in items:
            title = item.title
            link = item.link
            summary_html = item.summary if "summary" in item else ""
            soup = BeautifulSoup(summary_html, "html.parser")

            # --- Extract image if available ---
            img_tag = soup.find("img")
            img_url = img_tag["src"] if img_tag and img_tag.get("src") else None
            summary_text = soup.get_text()[:200] + "..." if summary_html else ""

            # --- News Card ---
            st.markdown("""
            <div style='padding:1em; margin-bottom:1.5em; background-color:#fff; border:1px solid #eee; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
            """, unsafe_allow_html=True)

            if img_url:
                st.image(img_url, use_container_width=True)

            st.markdown(f"**{title}**", unsafe_allow_html=True)
            st.markdown(summary_text)
            st.markdown(f"<a href='{link}' target='_blank'>Read more →</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🙏 *Let every headline remind us to pray and act with hope.*")
    st.link_button("Give with Grace", url="https://buy.stripe.com/28EfZg6hD1Lk0zsg7pdZ602")

    # --- Tab 3: Christian Media ---
with tab3:
    st.subheader("📖 Bible Reading Room")
    st.markdown("""
    <div class='donation-cta'>
    A quiet place to linger with Scripture — read, reflect, and let the Word dwell richly.
    </div>
    """, unsafe_allow_html=True)

    # --- Full Book-Chapter Map ---
    book_chapters = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
        "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
        "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
        "Ezra": 10, "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150,
        "Proverbs": 31, "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66,
        "Jeremiah": 52, "Lamentations": 5, "Ezekiel": 48, "Daniel": 12,
        "Hosea": 14, "Joel": 3, "Amos": 9, "Obadiah": 1, "Jonah": 4, "Micah": 7,
        "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3, "Haggai": 2, "Zechariah": 14,
        "Malachi": 4, "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21,
        "Acts": 28, "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13,
        "Galatians": 6, "Ephesians": 6, "Philippians": 4, "Colossians": 4,
        "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4,
        "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5,
        "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
    }

    # --- Select Book and Chapter ---
    book = st.selectbox("Choose a Book", list(book_chapters.keys()))
    chapter = st.number_input("Choose Chapter", min_value=1, max_value=book_chapters[book], value=1)

    # --- Display Selected Book and Chapter ---
    st.markdown(f"### {book} {int(chapter)}")

    # Fetch and display full Bible text using Bible API with typing effect
    api_url = f"https://bible-api.com/{book}%20{int(chapter)}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        verses = data.get("verses", [])
        all_verses = "<br>".join(
            f"<b>{verse['verse']}.</b> {verse['text']}" for verse in verses
        )
        st.markdown(
            f"<div class='verse-box'>{all_verses}</div>",
            unsafe_allow_html=True
        )
        st.success("All verses displayed.")
    else:
        st.info("Unable to fetch Bible text. Please check your internet connection or try another book/chapter.")

with tab4:
    st.header("🙏 Prayer Room")

    sound_map = {
        "Calm Music": "silent-evening-calm-piano-335749.mp3",  # Renamed from Gentle Bell to Calm Music
        "Worship Music": "silent-evening-calm-piano-335749.mp3"
    }
    sound_choice = st.selectbox("🔔 Choose Prayer Music", list(sound_map.keys()), index=1)  # Worship Music is default
    sound_file = sound_map.get(sound_choice)

    duration_minutes = st.slider("Set Prayer Time (minutes)", 1, 60, 5)
    duration_seconds = duration_minutes * 60

    # Option to play music during prayer
    play_music = st.checkbox("Play music while praying", value=False)
    
    # Option to play Lord's Prayer during prayer
    play_lords_prayer = st.checkbox("Play Lord's Prayer while praying", value=False)

    # Show current music selection for preview
    if play_music and sound_file:
        st.audio(sound_file, format="audio/mp3")
        st.info("👆 This music will play during your prayer time.")

    # Show Lord's Prayer audio player for preview
    if play_lords_prayer:
        st.audio("audio_The_Lords_Prayer.mp3", format="audio/mp3")
        st.info("👆 The Lord's Prayer will play during your prayer time.")

    # Create two buttons - one regular, one with music
    col1, col2 = st.columns(2)
    
    with col1:
        start_countdown = st.button("🕐 Start Silent Countdown", use_container_width=True)
        
    with col2:
        if play_music or play_lords_prayer:
            start_with_music = st.button("🎵 Start Prayer with Music", use_container_width=True, type="primary")
        else:
            start_with_music = False

    if start_countdown or start_with_music:
        import time
        
        # Store timer start time in session state
        if 'timer_start_time' not in st.session_state:
            st.session_state.timer_start_time = time.time()
            st.session_state.timer_duration = duration_seconds

        st.markdown("""
        <style>
        .main, .block-container { padding: 0 !important; }
        header, footer { display: none !important; }
        .fullscreen-countdown {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #f9f7f6;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 9999;
        }
        .fullscreen-countdown h1 {
            font-size: 10vw;
            color: #4caf50;
            text-align: center;
            margin: 0;
        }
        .gentle-message {
            font-size: 1.6rem;
            color: #594f4f;
            margin-top: 2vw;
            text-align: center;
            max-width: 700px;
            font-family: 'Playfair Display', serif;
            font-style: italic;
            padding-bottom: 80px; /* Add space at bottom to avoid overlap with icons */
        }
        /* Make Streamlit action buttons smaller and less intrusive */
        .stActionButton > button {
            width: 30px !important;
            height: 30px !important;
            font-size: 12px !important;
            padding: 2px !important;
        }
        div[data-testid="stToolbar"] {
            transform: scale(0.6);
            transform-origin: bottom right;
        }
        </style>
        """, unsafe_allow_html=True)

        gentle_message = (
            "<b>🔥 Come As You Are </b><br>"
            "Why set a timer to meet God? Because stillness rarely finds us on its own—we must choose it. In these few minutes, time won't race past. It will settle. It will breathe.<br>"
            "Don't ask. Just be. Let your heart rest in His presence.<br>"
            "It doesn't matter what burdens you carry or what mistakes you made today—come as you are. God already knows. What He desires most is your presence."
        )

        countdown_placeholder = st.empty()
        music_placeholder = st.empty()
        
        for t in range(duration_seconds, -1, -1):
            mins, secs = divmod(t, 60)
            
            # Update main countdown
            countdown_placeholder.markdown(
                f"""
                <div class='fullscreen-countdown'>
                    <h1>{mins}:{secs:02d}</h1>
                    <div class='gentle-message'>{gentle_message}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Update music player with live timer
            if start_with_music:
                music_html = '<div style="position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 10px; z-index: 1000;">'
                
                if play_music and sound_file:
                    if t > 0:
                        music_html += f'<p style="color: white; margin: 0 0 10px 0; font-size: 14px;">🎵 Prayer Music (stops in {mins}:{secs:02d})</p>'
                    else:
                        music_html += '<p style="color: #ffaa00; margin: 0 0 10px 0; font-size: 14px;">🎵 Prayer Music - STOPPED</p>'
                    music_html += f'''
                    <audio controls loop id="prayer-music" style="width: 280px;">
                        <source src="{sound_file}" type="audio/mpeg">
                    </audio><br>
                    '''
                
                if play_lords_prayer:
                    if t > 0:
                        music_html += f'<p style="color: white; margin: 10px 0 5px 0; font-size: 14px;">🙏 Lord\'s Prayer (stops in {mins}:{secs:02d})</p>'
                    else:
                        music_html += '<p style="color: #ffaa00; margin: 10px 0 5px 0; font-size: 14px;">🙏 Lord\'s Prayer - STOPPED</p>'
                    music_html += '''
                    <audio controls loop id="lords-prayer" style="width: 280px;">
                        <source src="audio_The_Lords_Prayer.mp3" type="audio/mpeg">
                    </audio>
                    '''
                
                if t > 0:
                    music_html += '<p style="color: #ccc; margin: 10px 0 0 0; font-size: 12px;">👆 Click PLAY to start music</p>'
                else:
                    music_html += '<p style="color: #ffaa00; margin: 10px 0 0 0; font-size: 12px;">🔔 Prayer time complete - music stopped</p>'
                    music_html += '''
                    <script>
                    const allAudio = document.querySelectorAll('audio');
                    allAudio.forEach(audio => {
                        if (!audio.paused) {
                            audio.pause();
                            console.log('Music stopped - prayer time complete');
                        }
                    });
                    </script>
                    '''
                
                music_html += '</div>'
                music_placeholder.markdown(music_html, unsafe_allow_html=True)
            
            time.sleep(1)
            
        # Clear timer session state when complete
        if 'timer_start_time' in st.session_state:
            del st.session_state.timer_start_time
        if 'timer_duration' in st.session_state:
            del st.session_state.timer_duration
            
        # Show "Complete" message with Chorus of Amens
        completion_message = (
            "<b>🕊️ Prayer Complete</b><br><br>"
            "<b>🎵 Chorus of Amens 🎵</b><br>"
            "Amen! Amen! Amen!<br>"
            "May Your will be done, Lord.<br>"
            "In Jesus' name, Amen.<br><br>"
            "Thank You, Father, for this sacred time together.<br>"
            "Your presence has filled this moment with peace."
        )
        
        countdown_placeholder.markdown(
            f"""
            <div class='fullscreen-countdown'>
                <h1>🕊️ Complete</h1>
                <div class='gentle-message'>{completion_message}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Use Streamlit components to trigger audio
        st.components.v1.html("""
        <script>
        function playAmens() {
            if ('speechSynthesis' in window) {
                // Clear any existing speech
                speechSynthesis.cancel();
                
                // Create the utterance
                const utterance = new SpeechSynthesisUtterance('Amen! Amen! Amen! May Your will be done, Lord. In Jesus name, Amen.');
                utterance.rate = 0.7;
                utterance.pitch = 1.0;
                utterance.volume = 0.8;
                
                // Get available voices and try to find a nice one
                const voices = speechSynthesis.getVoices();
                console.log('Available voices:', voices.map(v => v.name));
                
                // Try to find a suitable voice
                const preferredVoice = voices.find(voice => 
                    voice.name.includes('Female') || 
                    voice.name.includes('Samantha') || 
                    voice.name.includes('Karen') ||
                    voice.name.includes('Zira') ||
                    voice.lang.includes('en')
                );
                
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                    console.log('Using voice:', preferredVoice.name);
                }
                
                // Speak the amens
                speechSynthesis.speak(utterance);
                
                utterance.onend = function() {
                    console.log('Chorus of Amens completed');
                };
                
                utterance.onerror = function(event) {
                    console.error('Speech synthesis error:', event.error);
                };
            } else {
                console.log('Speech synthesis not supported');
            }
        }

        // Load voices and play after a short delay
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = function() {
                setTimeout(playAmens, 1000);
            };
        } else {
            setTimeout(playAmens, 1000);
        }
        </script>
        """, height=0)

# --- Tab 5: Daily Devotional ---
with tab5:
    st.header("Daily Devotional (Our Daily Bread)")

    feed_url = "https://odb.org/feed/"
    feed = feedparser.parse(feed_url)

    if feed.entries:
        for entry in feed.entries[:3]:  # Show the latest 3 devotionals
            st.subheader(entry.title)
            st.markdown(f"_{entry.published}_")
            st.markdown(entry.summary, unsafe_allow_html=True)
            st.markdown(f"[Read more]({entry.link})")
            st.markdown("---")
    else:
        st.info("Unable to fetch devotionals. Please try again later.")

# --- Tab 6: Comments and Feedback ---
with tab6:
    st.header("💬 Community Comments & Reflections")

    # Session state tracking
    if "my_comment_ids" not in st.session_state:
        st.session_state.my_comment_ids = []
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None
    if "delete_id" not in st.session_state:
        st.session_state.delete_id = None

    # --- Input form ---
    col_name, col_comment = st.columns([1, 3])
    with col_name:
        name = st.text_input("Your Name", key="supabase_name")
    with col_comment:
        comment = st.text_area("Share your thoughts, prayers, or encouragement:", key="supabase_input")

    if st.button("Post Comment"):
        if comment.strip():
            # Simple local comment storage for now
            if "local_comments" not in st.session_state:
                st.session_state.local_comments = []
            
            new_comment = {
                "id": len(st.session_state.local_comments) + 1,
                "name": name.strip() or "Anonymous",
                "text": comment.strip(),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "user": st.session_state.get("logged_in_user", "anonymous")
            }
            st.session_state.local_comments.insert(0, new_comment)  # Add to beginning
            st.session_state.my_comment_ids.append(new_comment["id"])
            st.success("✅ Thank you for sharing!")
            st.rerun()

    st.markdown("#### ✨ Recent Comments")
    
    # Use local comments if available, otherwise try Supabase
    try:
        if "local_comments" in st.session_state and st.session_state.local_comments:
            comments = st.session_state.local_comments
        else:
            # Try to get from Supabase, but fall back gracefully
            comments_response = get_comments()
            comments = comments_response.data if comments_response and hasattr(comments_response, 'data') else []
    except:
        # If Supabase fails, use local storage
        comments = st.session_state.get("local_comments", [])

    for c in comments:
        is_mine = c["id"] in st.session_state.my_comment_ids
        st.markdown("<div class='comment-card'>", unsafe_allow_html=True)

        if st.session_state.edit_id == c["id"]:
            st.markdown(f"<div class='comment-meta'><b>Editing as {c['name']}</b></div>", unsafe_allow_html=True)
            new_text = st.text_area("Edit your comment:", value=c["text"], key=f"edit_text_{c['id']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", key=f"save_{c['id']}"):
                    update_comment(c["id"], new_text)
                    st.session_state.edit_id = None
                    st.success("✏️ Comment updated!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", key=f"cancel_{c['id']}"):
                    st.session_state.edit_id = None
                    st.rerun()
        else:
            st.markdown(f"<div class='comment-meta'><b>{c['name']}</b> • {c['created_at']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div>{c['text']}</div>", unsafe_allow_html=True)

            # --- Action buttons (Edit, Share, Delete) ---
            cols = st.columns([0.2, 0.2, 0.2, 0.4])
            with cols[0]:
                if is_mine and st.button("✏️ Edit", key=f"edit_{c['id']}"):
                    st.session_state.edit_id = c["id"]
            with cols[1]:
                if st.button("🔗 Share", key=f"share_{c['id']}"):
                    st.code(c["text"], language="")
                    st.toast("Copied to clipboard!")
            with cols[2]:
                if is_mine and st.button("🗑️ Delete", key=f"delete_{c['id']}"):
                    st.session_state.delete_id = c["id"]

        st.markdown("</div>", unsafe_allow_html=True)

    # Handle deferred delete outside loop
    if st.session_state.delete_id is not None:
        delete_comment(st.session_state.delete_id)
        st.success("🗑️ Comment deleted!")
        st.session_state.delete_id = None
        st.rerun()

    st.markdown("---")
    st.markdown("🙏 *Thank you for helping us grow and improve this ministry.*")


st.markdown("""
<div style='background-color:#e3e7ff; color:#2a2a6c; padding:0.8em 1em; border-radius:8px; border:1px solid #b3b8e0; margin-bottom:1.5em; text-align:center; font-weight:600; font-size:1.1em;'>
🚧 <span style='color:#d97706;'>NM2 Bible Assistant is in <b>BETA</b></span> — Features may change. Thank you for your feedback and prayers!
</div>
""", unsafe_allow_html=True)
