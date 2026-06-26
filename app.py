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
    
    /* Status Box Styles */
    .status-box {
        padding: 15px 20px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: 500;
    }
    .status-box.success {
        background: linear-gradient(135deg, #d4edda, #b7e4c7);
        color: #0d6e2d;
        border-left: 5px solid #28a745;
        box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
    }
    .status-box.error {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        color: #721c24;
        border-left: 5px solid #dc3545;
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
    }
    .status-box.info {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        color: #0c5460;
        border-left: 5px solid #17a2b8;
        box-shadow: 0 2px 4px rgba(23, 162, 184, 0.2);
    }
    
    /* Answer Box Styles - Enhanced */
    .answer-container {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 16px;
        padding: 25px 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        position: relative;
        transition: all 0.3s ease;
    }
    .answer-container:hover {
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    .answer-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(180deg, #FF4B4B, #FF6B6B);
        border-radius: 16px 0 0 16px;
    }
    .answer-question {
        background: linear-gradient(135deg, #f0f2f6, #e8eaed);
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-weight: 600;
        color: #1a1a2e;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .answer-question::before {
        content: '❓';
        font-size: 20px;
    }
    .answer-text {
        background: white;
        padding: 18px 22px;
        border-radius: 10px;
        color: #2c3e50;
        line-height: 1.8;
        font-size: 16px;
        border: 1px solid #e9ecef;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    .answer-text::before {
        content: '💡 ';
        font-size: 18px;
    }
    
    /* Question Input Styling */
    .question-label {
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .question-label::before {
        content: '💬';
        font-size: 18px;
    }
    
    /* Download Button Styling */
    .download-btn {
        margin-top: 15px;
    }
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }
    
    /* Metric Styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e9ecef;
    }
    
    /* Divider Styling */
    hr {
        margin: 30px 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #FF4B4B, transparent);
    }
    
    /* Title Enhancement */
    .main-title {
        background: linear-gradient(135deg, #FF4B4B, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3em !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom title with gradient
st.markdown('<h1 class="main-title">🎥 ClipChat</h1>', unsafe_allow_html=True)
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
    st.metric("📹 Videos Processed", st.session_state.processed_videos)
    st.metric("❓ Questions Asked", st.session_state.questions_asked)

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
            st.caption(f"📌 Video ID: {video_id}")
        except:
            pass

with col2:
    st.subheader("💬 Question & Answer")
    question = st.text_area(
        "Ask a question about the video",
        placeholder="e.g., What is this video about?",
        height=80,
        label_visibility="collapsed"
    )
    
    # Add a label above the text area
    st.markdown('<div class="question-label">Ask a question about the video</div>', unsafe_allow_html=True)
    
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
    st.markdown('<h3 style="color: #1a1a2e; margin-bottom: 20px;">📝 Answer</h3>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="answer-container">
        <div class="answer-question">
            {question}
        </div>
        <div class="answer-text">
            {st.session_state.answer}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced download button
    col_download1, col_download2, col_download3 = st.columns([1, 2, 1])
    with col_download2:
        st.download_button(
            label="📥 Download Answer",
            data=st.session_state.answer,
            file_name="clipchat_answer.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_btn"
        )

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, and HuggingFace")
