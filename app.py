import streamlit as st
import os
import time
from rag import RAGProcessor

st.set_page_config(
    page_title="ClipChat - YouTube Q&A",
    page_icon="🎥",
    layout="wide"
)

# Clean, minimal CSS that works
st.markdown("""
    <style>
    /* Reset */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Title */
    .title-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    .title-container h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
    }
    .title-container p {
        color: #6c757d;
        font-size: 1.1rem;
        margin: 0.3rem 0 0 0;
    }
    
    /* Cards */
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border: 1.5px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        background: #fafafa !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4A90D9 !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.1) !important;
    }
    
    .stTextArea > div > div > textarea {
        border: 1.5px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        background: #fafafa !important;
        min-height: 80px !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #4A90D9 !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s !important;
        border: none !important;
        width: 100% !important;
        font-size: 0.95rem !important;
    }
    .stButton > button[kind="primary"] {
        background: #4A90D9 !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #3a7bc8 !important;
        box-shadow: 0 2px 8px rgba(74, 144, 217, 0.3) !important;
        transform: translateY(-1px);
    }
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    /* Status */
    .status-msg {
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        font-weight: 500;
        border-left: 4px solid;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
        border-left-color: #28a745;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
        border-left-color: #dc3545;
    }
    .status-info {
        background: #d1ecf1;
        color: #0c5460;
        border-left-color: #17a2b8;
    }
    
    /* Answer Box */
    .answer-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-top: 1rem;
    }
    .answer-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.8rem;
    }
    .answer-question {
        background: #f8f9fa;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        border-left: 3px solid #4A90D9;
        margin-bottom: 1rem;
        color: #1a1a2e;
        font-weight: 500;
    }
    .answer-text {
        color: #2d3748;
        line-height: 1.7;
        padding: 0.2rem 0;
    }
    .answer-text strong {
        color: #4A90D9;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #fafafa !important;
        padding: 1.5rem !important;
    }
    
    /* Sidebar steps */
    .step-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.4rem 0;
        color: #2d3748;
        font-size: 0.95rem;
    }
    .step-num {
        background: #4A90D9;
        color: white;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        text-align: center;
    }
    [data-testid="metric-label"] {
        color: #6c757d !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="metric-value"] {
        color: #1a1a2e !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    /* Download button */
    .download-wrapper {
        display: flex;
        justify-content: center;
        margin-top: 1rem;
    }
    .download-wrapper .stButton > button {
        width: auto !important;
        padding: 0.5rem 2.5rem !important;
        background: #28a745 !important;
        color: white !important;
    }
    .download-wrapper .stButton > button:hover {
        background: #218838 !important;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #adb5bd;
        font-size: 0.8rem;
        padding: 1.5rem 0 0.5rem 0;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1.5px solid #e9ecef;
    }
    
    /* Thumbnail */
    .thumbnail-container {
        border-radius: 10px;
        overflow: hidden;
        margin: 0.8rem 0;
        border: 1px solid #e9ecef;
    }
    .video-id-text {
        color: #6c757d;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 0.3rem;
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
    with st.container():
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
    with st.container():
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
    
    st.markdown(f'<div class="status-msg {status_class}">{st.session_state.status}</div>', unsafe_allow_html=True)

# ===== DISPLAY ANSWER =====
if st.session_state.answer:
    st.markdown("---")
    
    st.markdown(f"""
    <div class="answer-container">
        <div class="answer-label">📝 Answer</div>
        <div class="answer-question">
            <strong>Q:</strong> {question}
        </div>
        <div class="answer-text">
            <strong>A:</strong> {st.session_state.answer}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Download
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
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
