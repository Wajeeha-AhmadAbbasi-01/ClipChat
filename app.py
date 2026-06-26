# app.py
import streamlit as st
import os
import time
from utils.rag_utils import RAGProcessor

# Page configuration
st.set_page_config(
    page_title="ClipChat - YouTube Q&A",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stTextArea > div > div > textarea {
        font-size: 16px;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #ff4b4b;
    }
    .video-info {
        background-color: #e8f0fe;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
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

# Title
st.title("🎥 ClipChat")
st.markdown("Ask questions about any YouTube video using AI!")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Language selection
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
    3. Ask questions about the video
    4. Get AI-powered answers
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = 0
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    st.metric("Videos Processed", st.session_state.processed_videos)
    st.metric("Questions Asked", st.session_state.questions_asked)

# Main area - Two columns
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📹 Video Input")
    
    # Video URL input
    video_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://youtube.com/watch?v=...",
        help="Enter the full YouTube video URL"
    )
    
    # Process button
    process_button = st.button(
        "🔄 Process Video",
        type="primary",
        use_container_width=True,
        disabled=not video_url
    )
    
    # Show video preview if URL is valid
    if video_url and "youtube.com/watch" in video_url:
        try:
            video_id = video_url.split("v=")[1].split("&")[0]
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
            st.caption(f"Video ID: {video_id}")
        except:
            pass

with col2:
    st.subheader("💬 Question & Answer")
    
    # Question input
    question = st.text_area(
        "Ask a question about the video",
        placeholder="What is this video about?",
        height=80
    )
    
    # Ask button
    ask_button = st.button(
        "❓ Ask Question",
        type="primary",
        use_container_width=True,
        disabled=not question or not st.session_state.get('processed', False)
    )

# Status and progress display
status_container = st.container()
progress_container = st.container()

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = None
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

# Get API key from secrets (for Streamlit Cloud) or environment (for local)
def get_api_key():
    # Try Streamlit secrets first (for Cloud deployment)
    try:
        api_key = st.secrets.get("HUGGINGFACE_API_KEY")
        if api_key:
            return api_key
    except:
        pass
    
    # Try environment variable (for local development)
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if api_key:
        return api_key
    
    return None

# Check for API key
hf_token = get_api_key()

if not hf_token:
    st.error("""
    ⚠️ **HUGGINGFACE_API_KEY not found!**
    
    To deploy on Streamlit Cloud:
    1. Go to your app settings
    2. Click on "Secrets"
    3. Add `HUGGINGFACE_API_KEY` with your HuggingFace API key
    
    To run locally:
    1. Create `.streamlit/secrets.toml` file
    2. Add `HUGGINGFACE_API_KEY = "your_key_here"`
    """)
    st.stop()

# Initialize processor
@st.cache_resource
def get_processor():
    return RAGProcessor(hf_token)

try:
    processor = get_processor()
except Exception as e:
    st.error(f"⚠️ Error initializing processor: {str(e)}")
    st.stop()

# Process video
if process_button:
    if not video_url:
        st.session_state.status = "Please enter a YouTube URL"
        st.session_state.status_type = "error"
    else:
        try:
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Define progress callback
            def update_progress(msg, percent):
                status_text.text(msg)
                progress_bar.progress(percent / 100)
            
            # Process video
            with st.spinner("Processing video..."):
                processor.process_video(
                    video_url, 
                    language, 
                    update_progress
                )
            
            st.session_state.processed = True
            st.session_state.video_url = video_url
            st.session_state.processed_videos += 1
            st.session_state.status = "✅ Video processed successfully! You can now ask questions."
            st.session_state.status_type = "success"
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Rerun to update UI
            st.rerun()
            
        except Exception as e:
            st.session_state.status = f"❌ Error processing video: {str(e)}"
            st.session_state.status_type = "error"

# Ask question
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
        
        # Rerun to update UI
        st.rerun()
        
    except Exception as e:
        st.session_state.status = f"❌ Error getting answer: {str(e)}"
        st.session_state.status_type = "error"

# Display status
if st.session_state.status:
    status_type = st.session_state.status_type or "info"
    st.markdown(f"""
    <div class="status-box {status_type}">
        {st.session_state.status}
    </div>
    """, unsafe_allow_html=True)

# Display answer
if st.session_state.answer:
    st.markdown("---")
    st.subheader("📝 Answer")
    
    # Display in a styled box
    st.markdown(f"""
    <div class="answer-box">
        <strong>Q:</strong> {question}<br><br>
        <strong>A:</strong> {st.session_state.answer}
    </div>
    """, unsafe_allow_html=True)
    
    # Add download button for answer
    st.download_button(
        label="📥 Download Answer",
        data=st.session_state.answer,
        file_name="vidrag_answer.txt",
        mime="text/plain"
    )

# Display video info if processed
if st.session_state.processed and st.session_state.video_url:
    st.markdown("---")
    st.markdown(f"""
    <div class="video-info">
        ✅ <strong>Currently processing:</strong> {st.session_state.video_url}
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, and HuggingFace")

# Clear session button
if st.button("🗑️ Clear All"):
    for key in ['answer', 'status', 'processed', 'video_url']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()