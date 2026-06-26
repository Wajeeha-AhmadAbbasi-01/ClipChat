# app.py - Complete working app
import streamlit as st
import os
import time
from rag import RAGProcessor

st.set_page_config(
    page_title="ClipChat - YouTube Q&A",
    page_icon="🎥",
    layout="wide"
)

st.markdown("""
    <style>
    .stTextInput > div > div > input { font-size: 16px; }
    .stTextArea > div > div > textarea { font-size: 16px; }
    .answer-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #ff4b4b;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-box.success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-box.error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .status-box.info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎥 ClipChat")
st.markdown("Ask questions about any YouTube video using AI!")

with st.sidebar:
    st.header("⚙️ Settings")
    
    language = st.selectbox(
        "🌐 Video Language",
        options=['en', 'es', 'fr', 'de', 'hi', 'ja', 'zh', 'ar'],
        format_func=lambda x: {
            'en': '🇬🇧 English',
            'es': '🇪🇸 Spanish',
            'fr': '🇫🇷 French',
            'de': '🇩🇪 German',
            'hi': '🇮🇳 Hindi',
            'ja': '🇯🇵 Japanese',
            'zh': '🇨🇳 Chinese',
            'ar': '🇸🇦 Arabic'
        }[x]
    )
    
    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown("""
    1. Enter a YouTube URL
    2. Click "Process Video"
    3. Ask questions
    4. Get AI answers
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = 0
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    st.metric("Videos Processed", st.session_state.processed_videos)
    st.metric("Questions Asked", st.session_state.questions_asked)

def get_api_key():
    try:
        api_key = st.secrets.get("HUGGINGFACE_API_KEY")
        if api_key:
            return api_key
    except:
        pass
    return os.getenv("HUGGINGFACE_API_KEY")

hf_token = get_api_key()

if not hf_token:
    st.error("""
    ⚠️ **HUGGINGFACE_API_KEY not found!**
    
    Please add your HuggingFace API key:
    1. Go to app settings in Streamlit Cloud
    2. Click on "Secrets"
    3. Add `HUGGINGFACE_API_KEY = "your_key_here"`
    """)
    st.stop()

@st.cache_resource
def get_processor():
    return RAGProcessor(hf_token)

try:
    processor = get_processor()
except Exception as e:
    st.error(f"⚠️ Error initializing processor: {str(e)}")
    st.stop()

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📹 Video Input")
    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://youtube.com/watch?v=...",
        help="Enter the full YouTube video URL"
    )
    
    process_button = st.button(
        "🔄 Process Video",
        type="primary",
        use_container_width=True,
        disabled=not video_url
    )
    
    if video_url and "youtube.com/watch" in video_url:
        try:
            video_id = video_url.split("v=")[1].split("&")[0]
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
            st.caption(f"Video ID: {video_id}")
        except:
            pass

with col2:
    st.subheader("💬 Question & Answer")
    question = st.text_area(
        "Ask a question about the video",
        placeholder="What is this video about?",
        height=80
    )
    
    ask_button = st.button(
        "❓ Ask Question",
        type="primary",
        use_container_width=True,
        disabled=not question or not st.session_state.get('processed', False)
    )

if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_url' not in st.session_state:
    st.session_state.video_url = None
if 'answer' not in st.session_state:
    st.session_state.answer = None
if 'status' not in st.session_state:
    st.session_state.status = None
if 'status_type' not in st.session_state:
    st.session_state.status_type = None

if process_button:
    if not video_url:
        st.session_state.status = "Please enter a YouTube URL"
        st.session_state.status_type = "error"
    else:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(msg, percent):
                status_text.text(msg)
                progress_bar.progress(percent / 100)
            
            with st.spinner("Processing video..."):
                processor.process_video(video_url, language, update_progress)
            
            st.session_state.processed = True
            st.session_state.video_url = video_url
            st.session_state.processed_videos += 1
            st.session_state.status = "✅ Video processed successfully!"
            st.session_state.status_type = "success"
            
            progress_bar.empty()
            status_text.empty()
            st.rerun()
            
        except Exception as e:
            st.session_state.status = f"❌ Error: {str(e)}"
            st.session_state.status_type = "error"

if ask_button and st.session_state.processed:
    try:
        with st.spinner("🤔 Thinking..."):
            answer = processor.query_video(
                st.session_state.video_url,
                question,
                language
            )
        
        st.session_state.answer = answer
        st.session_state.questions_asked += 1
        st.session_state.status = "✅ Answer generated!"
        st.session_state.status_type = "success"
        st.rerun()
        
    except Exception as e:
        st.session_state.status = f"❌ Error: {str(e)}"
        st.session_state.status_type = "error"

if st.session_state.status:
    st.markdown(f"""
    <div class="status-box {st.session_state.status_type}">
        {st.session_state.status}
    </div>
    """, unsafe_allow_html=True)

if st.session_state.answer:
    st.markdown("---")
    st.subheader("📝 Answer")
    st.markdown(f"""
    <div class="answer-box">
        <strong>Q:</strong> {question}<br><br>
        <strong>A:</strong> {st.session_state.answer}
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Answer",
        data=st.session_state.answer,
        file_name="vidrag_answer.txt",
        mime="text/plain"
    )

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, and HuggingFace")
