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
}
.verse-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    font-style: italic;
    font-size: 1.1rem;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}
.donation-cta {
    background: #fff8e1;
    border-left: 4px solid #ffb74d;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    font-style: italic;
}
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
.comment-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.comment-meta {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 Bible Chat (Beta)",
    "🙏 Prayer Room",
    "📰 Bible News",
    "📖 Bible Reading Room",
    "📆 Daily Devotional",
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
            "verse": "\"Trust in the Lord with all your heart and lean not on your own understanding.\" — Proverbs 3:5",
            "teaching": "Divine wisdom runs deeper than logic. Trust requires surrender — not silence, but strength."
        },
        {
            "verse": "\"The Lord is my shepherd; I shall not want.\" — Psalm 23:1",
            "teaching": "God's care is constant. His presence provides even when provision seems absent."
        },
        {
            "verse": "\"Let the peace of Christ rule in your hearts.\" — Colossians 3:15",
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

# --- Tab 2: Prayer Room (IMPROVED VERSION) ---
with tab2:
    st.header("⏰ Prayer Timer")
    
    # Layout: Dropdown and button on same horizontal line
    col1, col2 = st.columns([3, 2])
    
    with col1:
        duration_minutes = st.selectbox("Prayer Duration", [1, 2, 5, 10, 15, 20, 30], index=2)
        duration_seconds = duration_minutes * 60
        
    with col2:
        # Align button with dropdown by adding vertical spacing
        st.write("")  # This creates space to align with selectbox
        start_timer = st.button("🕰️ Start Prayer Timer", use_container_width=True, type="primary")
    
    # Checkboxes on a separate row below
    checkbox_col1, checkbox_col2 = st.columns(2)
    with checkbox_col1:
        play_music = st.checkbox("🎵 Play Background Music", value=True)
    with checkbox_col2:
        play_lords_prayer = st.checkbox("🙏 Play Lord's Prayer", value=False)
    
    # Instructions
    st.info("🎵 **Music will automatically stop when the timer ends!** Click the button above to start your prayer time.")
    
    # Initialize session state for music control
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
            
            # Gentle messages that change during prayer
            gentle_messages = [
                "Be still and know that I am God...",
                "Rest in His presence...",
                "Let His peace fill your heart...",
                "You are loved beyond measure...",
                "Cast all your anxieties on Him...",
                "He who keeps you will not slumber..."
            ]
            
            # Change message every 30 seconds
            message_index = (duration_seconds - t) // 30 % len(gentle_messages)
            gentle_message = gentle_messages[message_index]
            
            # Update countdown
            countdown_placeholder.markdown(
                f"""
                <div class='fullscreen-countdown'>
                    <h1>{mins}:{secs:02d}</h1>
                    <div class='gentle-message'>{gentle_message}</div>
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
                <div class='gentle-message'>
                    <strong>Prayer time complete. Peace be with you.</strong><br><br>
                    "May the Lord bless you and keep you;<br>
                    may the Lord make his face shine on you<br>
                    and be gracious to you;<br>
                    may the Lord turn his face toward you<br>
                    and give you peace."<br>
                    <em>- Numbers 6:24-26</em><br><br>
                    <strong>🔇 Music has stopped automatically.</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # JavaScript to force stop any remaining audio - ENHANCED VERSION
        st.components.v1.html("""
        <script>
        console.log("🛑 Starting comprehensive audio shutdown sequence...");
        
        // STEP 1: Aggressive audio stopping
        function destroyAllAudio() {
            const audioElements = document.querySelectorAll('audio');
            console.log(`Found ${audioElements.length} audio elements to stop`);
            
            audioElements.forEach((audio, index) => {
                console.log(`Stopping audio element ${index}:`, audio.src);
                
                // Multiple stopping methods for reliability
                try {
                    audio.pause();
                    audio.currentTime = 0;
                    audio.volume = 0;
                    audio.muted = true;
                    audio.loop = false;
                    audio.autoplay = false;
                    audio.src = ''; // Clear the source
                    audio.load(); // Force reload with empty source
                } catch(e) {
                    console.log(`Error stopping audio ${index}:`, e);
                }
            });
            
            // Also try to find audio in iframes (Streamlit audio components)
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach((iframe, index) => {
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    const iframeAudio = iframeDoc.querySelectorAll('audio');
                    iframeAudio.forEach(audio => {
                        audio.pause();
                        audio.currentTime = 0;
                        audio.volume = 0;
                        audio.muted = true;
                    });
                } catch(e) {
                    console.log(`Cannot access iframe ${index} (cross-origin):`, e);
                }
            });
            
            console.log("Audio stopping sequence completed");
        }
        
        // Execute immediately
        destroyAllAudio();
        
        // Repeat after 500ms to catch any delayed audio
        setTimeout(() => {
            console.log("🔄 Secondary audio stop...");
            destroyAllAudio();
        }, 500);
        
        // Final cleanup after 1 second
        setTimeout(() => {
            console.log("🔄 Final audio cleanup...");
            destroyAllAudio();
            
            // Remove audio elements entirely
            document.querySelectorAll('audio').forEach(audio => {
                try {
                    audio.remove();
                } catch(e) {}
            });
            
            console.log("✅ All audio shutdown complete!");
        }, 1000);
        </script>
        """, height=0)
        
        # Extended pause to ensure complete audio silence before Amen
        time.sleep(4)
        
        st.components.v1.html("""
        <script>
        console.log("🗣️ Speaking Amen blessing after extended silence...");
        
        if ('speechSynthesis' in window) {
            // Ensure no existing speech
            speechSynthesis.cancel();
            
            // Wait a moment for speech synthesis to be ready
            setTimeout(() => {
                const utterance = new SpeechSynthesisUtterance('May the peace of Christ be with you. Amen and Amen.');
                utterance.rate = 0.8;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                utterance.onstart = () => console.log("✅ Amen blessing started after silence");
                utterance.onend = () => console.log("✅ Amen blessing completed");
                utterance.onerror = (e) => {
                    console.log("❌ Speech error:", e.error);
                    alert("🙏 May the peace of Christ be with you. Amen and Amen.");
                };
                
                // Find a good English voice
                const voices = speechSynthesis.getVoices();
                const preferredVoice = voices.find(v => 
                    v.lang.startsWith('en') && (
                        v.name.includes('Microsoft') || 
                        v.name.includes('Google') ||
                        v.name.includes('Natural')
                    )
                ) || voices.find(v => v.lang.startsWith('en'));
                
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                    console.log("Using voice:", preferredVoice.name);
                }
                
                speechSynthesis.speak(utterance);
                console.log("🗣️ Amen blessing spoken after guaranteed silence");
            }, 1000);  // Extra 1-second delay for speech readiness
            
        } else {
            console.log("❌ Speech synthesis not supported");
            alert("🙏 May the peace of Christ be with you. Amen and Amen.");
        }
        </script>
        """, height=0)
        
        # Wait for Amen blessing to complete, then refresh
        time.sleep(7)
        st.rerun()

# --- Tab 3: Bible News with Embedded Images ---
with tab3:
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
            summary = BeautifulSoup(item.summary, 'html.parser').get_text() if item.summary else "No summary available."
            summary_text = summary[:200] + "..." if len(summary) > 200 else summary
            
            st.markdown("<div style='border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; background-color: #fafafa;'>", unsafe_allow_html=True)
            st.markdown(f"**{title}**", unsafe_allow_html=True)
            st.markdown(summary_text)
            st.markdown(f"<a href='{link}' target='_blank'>Read more →</a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🙏 *Let every headline remind us to pray and act with hope.*")
    st.link_button("Give with Grace", url="https://buy.stripe.com/28EfZg6hD1Lk0zsg7pdZ602")

# --- Tab 4: Bible Reading Room ---
with tab4:
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

    # Fetch and display full Bible text using Bible API
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
    else:
        st.info("Unable to fetch Bible text. Please check your internet connection or try another book/chapter.")

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
    from supabase_utils import add_comment, get_comments, update_comment, delete_comment

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
            comment_id = add_comment(name.strip() or "Anonymous", comment.strip())
            if comment_id:
                st.session_state.my_comment_ids.append(comment_id)
                st.success(f"✅ Thank you for sharing! (Comment ID: {comment_id})")
                st.info(f"🔍 Debug: Your comment IDs: {st.session_state.my_comment_ids}")
            else:
                st.error("❌ Failed to save comment. Please try again.")
            st.rerun()

    st.markdown("#### ✨ Recent Comments")
    comments = get_comments()
    
    # Debug info
    if st.session_state.my_comment_ids:
        st.info(f"🔍 Your comment IDs this session: {st.session_state.my_comment_ids}")

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
