import streamlit as st
import os
import time
from rag import RAGProcessor

st.set_page_config(
    page_title="ClipChat - YouTube Q&A",
    page_icon="🎥",
    layout="wide"
)

# Clean, responsive CSS adapting to both Light and Dark themes
st.markdown("""
    <style>
    /* Reset & Spacing */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Title Section */
    .title-container {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1.5rem;
    }
    .title-container h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(45deg, #4A90D9, #28a745);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .title-container p {
        color: var(--text-color);
        opacity: 0.8;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Elegant Modern Cards */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Setup explicit text colors for system elements to adapt perfectly */
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Customizing Streamlit Native Form Elements seamlessly */
    .stTextInput > div > div {
        border-radius: 10px !important;
    }
    .stTextArea > div > div {
        border-radius: 10px !important;
    }
    
    /* Buttons Customization styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        font-size: 0.95rem !important;
    }
    
    /* Step Item Customizations */
    .step-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.5rem 0;
        font-size: 0.95rem;
    }
    .step-num {
        background: #4A90D9;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
    
    /* Answer Display Box Styling */
    .answer-container {
        background: rgba(74, 144, 217, 0.05);
        border-radius: 16px;
        padding: 1.8rem;
        border: 1px solid rgba(74, 144, 217, 0.2);
        margin-top: 1.5rem;
    }
    .answer-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #4A90D9;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.8rem;
    }
    .answer-question {
        background: rgba(128, 128, 128, 0.1);
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border-left: 4px solid #4A90D9;
        margin-bottom: 1.2rem;
        font-weight: 500;
    }
    .answer-text {
        line-height: 1.7;
        font-size: 1.05rem;
    }
    
    /* Footer section alignment */
    .footer {
        text-align: center;
        opacity: 0.5;
        font-size: 0.85rem;
        padding: 2rem 0 1rem 0;
    }
    
    .video-id-text {
        opacity: 0.6;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ===== TITLE =====
st.markdown("""
<div class="title-container">
    <h1>🎥 ClipChat</h1>
    <p>Ask questions about any YouTube video using AI</p>
</div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    language = st.selectbox(
        "🌐 Video Language",
        options=['en', 'es', 'fr', 'de', 'hi', 'ja', 'zh', 'ar'],
        format_func=lambda x: {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'hi': 'Hindi',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }[x]
    )
    
    st.markdown("---")
    
    st.markdown("### 📖 How it Works")
    st.markdown("""
    <div class="step-item">
        <span class="step-num">1</span>
        <span>Enter YouTube URL</span>
    </div>
    <div class="step-item">
        <span class="step-num">2</span>
        <span>Click "Process Video"</span>
    </div>
    <div class="step-item">
        <span class="step-num">3</span>
        <span>Ask a question</span>
    </div>
    <div class="step-item">
        <span class="step-num">4</span>
        <span>Get AI answer</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Stats")
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = 0
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("🎬 Videos", st.session_state.processed_videos)
    with c2:
        st.metric("💬 Questions", st.session_state.questions_asked)

# ===== API KEY =====
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
    1. Go to app settings
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

# ===== SESSION STATE =====
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

# ===== MAIN LAYOUT =====
col1, col2 = st.columns([2, 3], gap="medium")

# LEFT COLUMN
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📹 Video Input</div>', unsafe_allow_html=True)
    
    video_url = st.text_input(
        "YouTube URL",
        placeholder="https://youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
    
    process_clicked = st.button(
        "🔄 Process Video",
        type="primary",
        disabled=not video_url
    )
    
    # Thumbnail
    if video_url:
        try:
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            elif "shorts" in video_url:
                video_id = video_url.split("/shorts/")[1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            
            st.image(
                f"http://img.youtube.com/vi/{video_id}/0.jpg",
                use_container_width=True
            )
            st.markdown(f'<div class="video-id-text">📌 Video ID: {video_id}</div>', unsafe_allow_html=True)
        except:
            pass
            
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💬 Question & Answer</div>', unsafe_allow_html=True)
    
    question = st.text_area(
        "Ask a question",
        placeholder="e.g., What is this video about?",
        height=100,
        label_visibility="collapsed"
    )
    
    ask_clicked = st.button(
        "❓ Ask Question",
        type="secondary",
        disabled=not question or not st.session_state.get('processed', False)
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== PROCESS VIDEO =====
if process_clicked:
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

# ===== ASK QUESTION =====
if ask_clicked and st.session_state.processed:
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

# ===== DISPLAY STATUS =====
if st.session_state.status:
    if st.session_state.status_type == "success":
        st.success(st.session_state.status)
    elif st.session_state.status_type == "error":
        st.error(st.session_state.status)
    else:
        st.info(st.session_state.status)

# ===== DISPLAY ANSWER =====
if st.session_state.answer:
    st.markdown(f"""
    <div class="answer-container">
        <div class="answer-label">📝 Answer</div>
        <div class="answer-question">
            <strong>Q:</strong> {question}
        </div>
        <div class="answer-text">
            {st.session_state.answer}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Download
    st.download_button(
        label="📥 Download Answer Summary",
        data=st.session_state.answer,
        file_name="clipchat_answer.txt",
        mime="text/plain"
    )

# ===== FOOTER =====
st.markdown('<div class="footer">Built with ❤️ using Streamlit, LangChain & HuggingFace</div>', unsafe_allow_html=True)
