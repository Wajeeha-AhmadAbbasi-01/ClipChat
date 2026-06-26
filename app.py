import streamlit as st
import os
import time
from rag import RAGProcessor

st.set_page_config(
    page_title="ClipChat - YouTube Q&A",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS for beautiful UI
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Title Styles */
    .gradient-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5em !important;
        text-align: center;
        padding: 20px 0;
        letter-spacing: -1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2em;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    
    /* Video Input Section */
    .video-section {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.8);
        backdrop-filter: blur(10px);
    }
    
    /* Question Section */
    .question-section {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.8);
        backdrop-filter: blur(10px);
        min-height: 400px;
    }
    
    /* Answer Container - Premium Design */
    .answer-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255,255,255,0.6);
        position: relative;
        animation: slideUp 0.5s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .answer-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        border-radius: 20px;
        pointer-events: none;
    }
    
    .answer-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f0f0;
        position: relative;
        z-index: 1;
    }
    
    .answer-header-icon {
        font-size: 28px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 10px;
        border-radius: 12px;
        color: white;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .answer-header-text {
        flex: 1;
    }
    
    .answer-header-text h4 {
        margin: 0;
        color: #2d3748;
        font-weight: 600;
        font-size: 1.1em;
    }
    
    .answer-header-text .timestamp {
        color: #a0aec0;
        font-size: 0.85em;
        margin-top: 2px;
    }
    
    .question-bubble {
        background: linear-gradient(135deg, #ebf4ff, #e0e7ff);
        padding: 15px 20px;
        border-radius: 15px;
        margin: 15px 0 20px 0;
        border-left: 4px solid #667eea;
        position: relative;
        z-index: 1;
        font-weight: 500;
        color: #2d3748;
    }
    
    .question-bubble::before {
        content: '📝 ';
        font-size: 18px;
    }
    
    .answer-content {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative;
        z-index: 1;
        line-height: 1.8;
        color: #2d3748;
        font-size: 1.05em;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .answer-content:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    .answer-content::before {
        content: '💡 ';
        font-size: 20px;
    }
    
    .answer-content strong {
        color: #667eea;
    }
    
    /* Status Messages */
    .status-box {
        padding: 16px 24px;
        border-radius: 15px;
        margin: 15px 0;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideUp 0.3s ease-out;
    }
    
    .status-box.success {
        background: linear-gradient(135deg, #d4edda, #b7e4c7);
        color: #0d6e2d;
        border-left: 5px solid #28a745;
    }
    
    .status-box.error {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        color: #721c24;
        border-left: 5px solid #dc3545;
    }
    
    .status-box.info {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        color: #0c5460;
        border-left: 5px solid #17a2b8;
    }
    
    /* Button Styles */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        min-height: 100px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-right: 1px solid #e2e8f0 !important;
        padding: 20px !important;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    [data-testid="metric-label"] {
        font-weight: 600 !important;
        color: #4a5568 !important;
    }
    
    [data-testid="metric-value"] {
        color: #667eea !important;
        font-weight: 800 !important;
    }
    
    /* Download Button */
    .download-btn-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    
    /* Divider */
    hr {
        margin: 30px 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
    }
    
    /* Sidebar sections */
    .sidebar-section {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .gradient-title {
            font-size: 2.5em !important;
        }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    </style>
""", unsafe_allow_html=True)

# Title Section
st.markdown('<h1 class="gradient-title">🎥 ClipChat</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">✨ Ask questions about any YouTube video using AI</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
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
    
    st.markdown("### 📖 How it Works")
    st.markdown("""
    <div class="sidebar-section">
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <div><span style="font-weight: bold; color: #667eea;">1.</span> 📹 Enter YouTube URL</div>
            <div><span style="font-weight: bold; color: #667eea;">2.</span> 🔄 Click "Process Video"</div>
            <div><span style="font-weight: bold; color: #667eea;">3.</span> 💬 Ask your question</div>
            <div><span style="font-weight: bold; color: #667eea;">4.</span> 🤖 Get AI answer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Stats")
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = 0
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📹 Processed", st.session_state.processed_videos)
    with col2:
        st.metric("❓ Questions", st.session_state.questions_asked)

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

# Main Layout
col1, col2 = st.columns([2, 3], gap="large")

with col1:
    st.markdown('<div class="video-section">', unsafe_allow_html=True)
    st.subheader("📹 Video Input")
    
    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://youtube.com/watch?v=...",
        help="Enter the full YouTube video URL",
        label_visibility="collapsed"
    )
    
    process_button = st.button(
        "🔄 Process Video",
        type="primary",
        use_container_width=True,
        disabled=not video_url
    )
    
    if video_url and ("youtube.com/watch" in video_url or "youtu.be" in video_url):
        try:
            if "youtu.be" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url.split("v=")[1].split("&")[0]
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
            st.caption(f"📌 Video ID: {video_id}")
        except:
            pass
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="question-section">', unsafe_allow_html=True)
    st.subheader("💬 Question & Answer")
    
    question = st.text_area(
        "Ask a question about the video",
        placeholder="e.g., What is this video about?",
        height=80,
        label_visibility="collapsed"
    )
    
    ask_button = st.button(
        "❓ Ask Question",
        type="primary",
        use_container_width=True,
        disabled=not question or not st.session_state.get('processed', False)
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
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

# Process Video
if process_button:
    if not video_url:
        st.session_state.status = "⚠️ Please enter a YouTube URL"
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

# Ask Question
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
        st.session_state.status = "✅ Answer generated successfully!"
        st.session_state.status_type = "success"
        st.rerun()
        
    except Exception as e:
        st.session_state.status = f"❌ Error: {str(e)}"
        st.session_state.status_type = "error"

# Display Status
if st.session_state.status:
    icon = "✅" if st.session_state.status_type == "success" else "❌" if st.session_state.status_type == "error" else "ℹ️"
    st.markdown(f"""
    <div class="status-box {st.session_state.status_type}">
        <span style="font-size: 20px;">{icon}</span>
        <span>{st.session_state.status}</span>
    </div>
    """, unsafe_allow_html=True)

# Display Answer
if st.session_state.answer:
    st.markdown("---")
    
    st.markdown(f"""
    <div class="answer-container">
        <div class="answer-header">
            <div class="answer-header-icon">🤖</div>
            <div class="answer-header-text">
                <h4>AI Answer</h4>
                <div class="timestamp">Generated just now</div>
            </div>
        </div>
        
        <div class="question-bubble">
            {question}
        </div>
        
        <div class="answer-content">
            {st.session_state.answer}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Download Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download Answer",
            data=st.session_state.answer,
            file_name="clipchat_answer.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_btn"
        )

st.markdown("---")
st.markdown('<p style="text-align: center; color: #a0aec0; font-size: 0.9em;">Built with ❤️ using Streamlit, LangChain, and HuggingFace</p>', unsafe_allow_html=True)
