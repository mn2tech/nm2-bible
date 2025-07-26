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
import time  # <-- Add this line

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
    chosen = random.choice(verses)
    st.markdown(f"<div class='verse-box'>{chosen['verse']}</div>", unsafe_allow_html=True)
    with st.expander("📖 Teach me more"):
        st.markdown(chosen["teaching"])
    with st.expander("🙏 A short prayer"):
        st.markdown("""Lord, may Your Word take root in my heart today.  
        Guide me, teach me, and help me walk with grace.  
        Thank You for being near, even in silence. Amen.""")

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
    # st.image("prayer.png", use_container_width=True)  # <-- Remove or comment out this line
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

    # Show music player for manual play before countdown
    if play_music and sound_file:
        st.audio(sound_file, format="audio/mp3")
        st.info("Click the play button above to start your prayer music.")

    # Option to play Lord's Prayer during prayer
    play_lords_prayer = st.checkbox("Play Lord's Prayer while praying", value=False)

    # Show Lord's Prayer audio player for manual play before countdown
    if play_lords_prayer:
        st.audio("audio_The_Lords_Prayer.mp3", format="audio/mp3")
        st.info("Click the play button above to listen to the Lord's Prayer during your prayer.")

    if st.button("Start Countdown"):
        import time

        st.markdown("""
        <style>
        .main, .block-container { padding: 0 !important; }
        header, footer, [data-testid="stSidebar"] { display: none !important; }
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
        }
        </style>
        """, unsafe_allow_html=True)

        gentle_message = (
            "<b>🔥 Come As You Are </b><br>"
            "Why set a timer to meet God? Because stillness rarely finds us on its own—we must choose it. In these few minutes, time won’t race past. It will settle. It will breathe.<br>"
            "Don’t ask. Just be. Let your heart rest in His presence.<br>"
            "It doesn’t matter what burdens you carry or what mistakes you made today—come as you are. God already knows. What He desires most is your presence."
        )

        countdown_placeholder = st.empty()
        for t in range(duration_seconds, -1, -1):
            mins, secs = divmod(t, 60)
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
        # Show "Complete" message only (no music at end)
        countdown_placeholder.markdown(
            f"""
            <div class='fullscreen-countdown'>
                <h1>🕊️ Complete</h1>
                <div class='gentle-message'>{gentle_message}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

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

    # --- Add the latest Our Daily Bread video ---
    st.subheader("Watch Today's Devotional")
    st.video("https://www.youtube.com/watch?v=Qw3R8b6qQ1A")  # Replace with the latest video URL if needed

# --- Tab 6: Comments and Feedback ---
with tab6:
    st.header("💬 Community Comments & Reflections")

    # Modern comment input area
    st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)

    if "comments" not in st.session_state:
        st.session_state.comments = []  # Each comment: {"name": ..., "text": ...}

    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None

    # --- Input fields for name and comment ---
    col_name, col_comment = st.columns([1, 3])
    with col_name:
        name = st.text_input("Your Name", key="comment_name")
    with col_comment:
        comment = st.text_area("Share your thoughts, prayers, or encouragement:", key="comment_input")

    if st.button("Post Comment"):
        if comment.strip():
            st.session_state.comments.append({"name": name.strip() or "Anonymous", "text": comment.strip()})
            st.success("Thank you for sharing!")
            st.rerun()

    st.markdown("#### Recent Comments:")

    for idx, c in enumerate(reversed(st.session_state.comments[-10:])):
        real_idx = len(st.session_state.comments) - 1 - idx  # Actual index in the list

        st.markdown("<div class='comment-card'>", unsafe_allow_html=True)
        if st.session_state.edit_index == real_idx:
            st.markdown("<div class='comment-meta'><b>Edit your comment</b></div>", unsafe_allow_html=True)
            new_name = st.text_input("Edit your name:", value=c["name"], key=f"edit_name_{real_idx}")
            new_text = st.text_area("Edit your comment:", value=c["text"], key=f"edit_{real_idx}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key=f"save_{real_idx}"):
                    st.session_state.comments[real_idx] = {"name": new_name, "text": new_text}
                    st.session_state.edit_index = None
                    st.success("Comment updated!")
                    st.rerun()
            with col2:
                if st.button("Cancel", key=f"cancel_{real_idx}"):
                    st.session_state.edit_index = None
                    st.rerun()
        else:
            st.markdown(f"<div class='comment-meta'><b>{c['name']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div>{c['text']}</div>", unsafe_allow_html=True)
            cols = st.columns([0.1, 0.9])
            with cols[0]:
                if st.button("✏️", key=f"edit_btn_{real_idx}"):
                    st.session_state.edit_index = real_idx
                    st.rerun()
            with cols[1]:
                st.code(c["text"], language="")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🙏 *Thank you for helping us grow and improve this ministry.*")

st.markdown("""
<div style='background-color:#e3e7ff; color:#2a2a6c; padding:0.8em 1em; border-radius:8px; border:1px solid #b3b8e0; margin-bottom:1.5em; text-align:center; font-weight:600; font-size:1.1em;'>
🚧 <span style='color:#d97706;'>NM2 Bible Assistant is in <b>BETA</b></span> — Features may change. Thank you for your feedback and prayers!
</div>
""", unsafe_allow_html=True)