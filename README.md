# 🎥 VidRAG

**VidRAG** (Video + RAG) - Ask questions about any YouTube video using AI!

## Features
- 🎬 Extract transcripts from any YouTube video
- 🧠 RAG (Retrieval Augmented Generation) powered by LangChain
- 🌐 Multi-language support (English, Spanish, French, German, Hindi, Japanese, Chinese, Arabic)
- 💬 Natural language question answering
- 🚀 Deployed on Streamlit Community Cloud

## How to Use
1. Enter a YouTube video URL
2. Click "Process Video"
3. Ask questions about the video
4. Get AI-powered answers

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: HuggingFace (Google FLAN-T5-Large)
- **Embeddings**: sentence-transformers/all-mpnet-base-v2
- **Vector Store**: FAISS
- **Orchestration**: LangChain

## Local Development

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/vidrag.git
cd vidrag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create secrets file
mkdir .streamlit
echo "HUGGINGFACE_API_KEY = 'your_key_here'" > .streamlit/secrets.toml

# Run the app
streamlit run app.py
