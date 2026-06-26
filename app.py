import streamlit as st
import os
import time
from rag import RAGProcessor

st.set_page_config(
    page_title="ClipChat - YouTube Q&A",
    page_icon="🎥",
    layout="wide"
)

# Clean, professional CSS
st.markdown("""
    <style>
    /* Reset and Base */
    .main {
        background: #f8f9fa;
    }
    
    /* Title */
    .app-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .app-subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border: 2px solid #e9ecef !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
        background: #f8f9fa !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4A90D9 !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.1) !important;
    }
    
    .stTextArea > div > div > textarea {
        border: 2px solid #e9ecef !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        min-height: 100px !important;
        transition: all 0.2s ease !important;
        background: #f8f9fa !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #4A90D9 !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        border: none !important;
        width: 100% !important;
    }
    
    .stButton > button[kind="primary"] {
        background: #4A90D9 !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #3a7bc8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74, 144, 217, 0.3) !important;
    }
    
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    /* Status Messages */
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 12px 18px;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 12px 0;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 12px 18px;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 12px 0;
    }
    
    .status-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 12px 18px;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 12px 0;
    }
    
    /* Answer Box - Clean Design */
    .answer-box {
        background: white;
        border-radius: 16px;
        padding: 28px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-top: 20px;
    }
    
    .answer-question {
        background: #f8f9fa;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 16px;
        border-left: 4px solid #4A90D9;
        color: #1a1a2e;
        font-weight: 500;
    }
    
    .answer-text {
        color: #2d3748;
        line-height: 1.8;
        font-size: 1rem;
        padding: 4px 0;
    }
    
    .answer-label {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .answer-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #e9ecef;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: white !important;
        border-right: 1px solid #e9ecef !important;
        padding: 24px !important;
    }
    
    .sidebar-header {
        font-weight: 700;
        font-size: 1.2rem;
        color: #1a1a2e;
        margin-bottom: 20px;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    [data-testid="metric-label"] {
        color: #6c757d !important;
        font-weight: 500 !important;
    }
    
    [data-testid="metric-value"] {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }
    
    /* Download Button Container */
    .download-wrapper {
        display: flex;
        justify-content: center;
        margin-top: 16px;
    }
    
    .download-wrapper .stButton > button {
        width: auto !important;
        padding: 8px 32px !important;
        background: #28a745 !important;
    }
    
    .download-wrapper .stButton > button:hover {
        background: #218838 !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* Divider */
    hr {
        margin: 28px 0;
        border: none;
        border-top: 2px solid #e9ecef;
    }
    
    /* Video Thumbnail */
    .video-thumbnail {
        border-radius: 12px;
        overflow: hidden;
        margin: 12px 0;
        border: 1px solid #e9ecef;
    }
    
    .video-id {
        color: #6c757d;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 6px;
    }
    
    /* How it works steps */
    .step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        color: #2d3748;
    }
    
    .step-number {
        background: #4A90D9;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #adb5bd;
        font-size: 0.85rem;
        padding: 20px 0 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ===== TITLE SECTION =====
st.markdown('<div class="app-title">🎥 ClipChat</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Ask questions about any YouTube video using AI</div>', unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
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
    
    st.markdown("**📖 How it Works**")
    st.markdown("""
    <div class="step">
        <span class="step-number">1</span>
        <span>Enter YouTube URL</span>
    </div>
    <div class="step">
        <span class="step-number">2</span>
        <span>Click "Process Video"</span>
    </div>
    <div class="step">
        <span class="step-number">3</span>
        <span>Ask a question</span>
    </div>
    <div class="step">
        <span class="step-number">4</span>
        <span>Get AI answer</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**📊 Stats**")
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = 0
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Videos", st.session_state.processed_videos)
    with col2:
        st.metric("Questions", st.session_state.questions_asked)

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
col1, col2 = st.columns([2, 3])

# LEFT COLUMN - Video Input
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
    
    # Show thumbnail
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
            st.markdown(f'<div class="video-id">📌 Video ID: {video_id}</div>', unsafe_allow_html=True)
        except:
            pass
    
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN - Question & Answer
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💬 Question & Answer</div>', unsafe_allow_html=True)
    
    question = st.text_area(
        "Ask a question",
        placeholder="e.g., What is this video about?",
        height=80,
        label_visibility="collapsed"
    )
    
    ask_clicked = st.button(
        "❓ Ask Question",
        type="primary",
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
    status_class = {
        "success": "status-success",
        "error": "status-error",
        "info": "status-info"
    }.get(st.session_state.status_type, "status-info")
    
    st.markdown(f'<div class="{status_class}">{st.session_state.status}</div>', unsafe_allow_html=True)

# ===== DISPLAY ANSWER =====
if st.session_state.answer:
    st.markdown("---")
    
    st.markdown("""
    <div class="answer-box">
        <div class="answer-label">📝 Answer</div>
        <div class="answer-question">
            <strong>Q:</strong> {question}
        </div>
        <div class="answer-text">
            <strong>A:</strong> {answer}
        </div>
    </div>
    """.format(question=question, answer=st.session_state.answer), unsafe_allow_html=True)
    
    # Download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download Answer",
            data=st.session_state.answer,
            file_name="clipchat_answer.txt",
            mime="text/plain",
            use_container_width=True
        )

# ===== FOOTER =====
st.markdown("---")
st.markdown('<div class="footer">Built with ❤️ using Streamlit, LangChain & HuggingFace</div>', unsafe_allow_html=True)
