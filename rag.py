# rag.py - Complete working version with proxy support
import os
import re
import time
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api._errors import NoTranscriptFound, YouTubeRequestFailed
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class RAGProcessor:
    def __init__(self, huggingface_token=None):
        self.huggingface_token = huggingface_token
        if not self.huggingface_token:
            raise ValueError("HUGGINGFACE_API_KEY not set")
        
        self.embedding_model = "sentence-transformers/all-mpnet-base-v2"
        
        # Initialize YouTube API with proxy support
        self.yapi = self._init_youtube_api()
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        self.prompt = PromptTemplate(
            template="""
            You are a helpful assistant.
            Answer Only from the provided transcript context.
            If the context is insufficient, just say you don't know.

            Context: {context}
            Question: {question}

            Answer:
            """,
            input_variables=['context', 'question']
        )
        
        self.vectorstores = {}
        self.transcript_cache = {}
    
    def _init_youtube_api(self):
        """Initialize YouTube API with proxy from environment"""
        try:
            # Try to get proxy credentials from environment
            proxy_username = os.getenv("PROXY_USERNAME")
            proxy_password = os.getenv("PROXY_PASSWORD")
            proxy_host = os.getenv("PROXY_HOST", "p.webshare.io")
            proxy_port = os.getenv("PROXY_PORT", "80")
            
            if proxy_username and proxy_password:
                print("✅ Using proxy for YouTube API")
                # Create proxy configuration for webshare
                proxy_config = {
                    "http": f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}",
                    "https": f"https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                }
                
                # Set proxy in environment for requests
                os.environ['HTTP_PROXY'] = proxy_config['http']
                os.environ['HTTPS_PROXY'] = proxy_config['https']
                
                return YouTubeTranscriptApi()
            else:
                print("ℹ️ No proxy configured, using direct connection")
                return YouTubeTranscriptApi()
        except Exception as e:
            print(f"⚠️ Proxy initialization failed: {e}")
            return YouTubeTranscriptApi()
    
    def extract_video_id(self, video_url: str) -> str:
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
            r'(?:youtube\.com\/v\/)([\w-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        raise ValueError(f"Could not extract video ID from URL: {video_url}")
    
    def get_transcript(self, video_id: str, language: str = 'en') -> str:
        cache_key = f"{video_id}_{language}"
        if cache_key in self.transcript_cache:
            return self.transcript_cache[cache_key]
        
        language_codes = {
            'en': ['en', 'en-US'],
            'es': ['es', 'es-ES', 'es-MX'],
            'fr': ['fr', 'fr-FR'],
            'de': ['de', 'de-DE'],
            'hi': ['hi'],
            'ja': ['ja'],
            'zh': ['zh', 'zh-CN', 'zh-TW'],
            'ar': ['ar'],
        }.get(language, ['en'])
        
        # Try multiple methods to get transcript
        transcript = None
        errors = []
        
        # Method 1: Direct fetch with language
        try:
            print(f"🔍 Trying to fetch transcript for {video_id} in {language}...")
            transcript_list = self.yapi.fetch(video_id, languages=language_codes)
            transcript = " ".join(snippet.text for snippet in transcript_list)
            self.transcript_cache[cache_key] = transcript
            print(f"✅ Transcript fetched successfully")
            return transcript
        except TranscriptsDisabled as e:
            errors.append(f"Transcripts disabled: {e}")
        except NoTranscriptFound as e:
            errors.append(f"No transcript found: {e}")
        except Exception as e:
            errors.append(str(e))
        
        # Method 2: Try without language restriction (any available)
        if not transcript:
            try:
                print("🔄 Trying to fetch any available transcript...")
                transcript_list = self.yapi.fetch(video_id)
                transcript = " ".join(snippet.text for snippet in transcript_list)
                self.transcript_cache[cache_key] = transcript
                print(f"✅ Transcript fetched successfully")
                return transcript
            except Exception as e:
                errors.append(f"Fallback failed: {e}")
        
        # Method 3: Try using yt-dlp (fallback)
        if not transcript:
            try:
                print("🔄 Trying yt-dlp fallback...")
                transcript = self._get_transcript_ytdlp(video_id)
                if transcript:
                    self.transcript_cache[cache_key] = transcript
                    print(f"✅ Transcript fetched via yt-dlp")
                    return transcript
            except Exception as e:
                errors.append(f"yt-dlp failed: {e}")
        
        # If all methods fail, raise error with details
        raise Exception(
            f"Could not retrieve transcript for video {video_id}.\n"
            f"Errors: {'; '.join(errors)}\n\n"
            f"Try these solutions:\n"
            f"1. Use a different YouTube video (some have no captions)\n"
            f"2. Add proxy credentials to Streamlit secrets:\n"
            f"   PROXY_USERNAME=your_username\n"
            f"   PROXY_PASSWORD=your_password\n"
            f"3. Or try a different URL format"
        )
    
    def _get_transcript_ytdlp(self, video_id: str) -> str:
        """Fallback method using yt-dlp"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'es', 'fr', 'de', 'hi', 'ja', 'zh'],
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
                
                # Try subtitles
                subtitles = info.get('subtitles', {})
                for lang in ['en', 'es', 'fr', 'de', 'hi', 'ja', 'zh']:
                    if lang in subtitles and subtitles[lang]:
                        transcript = ""
                        for sub in subtitles[lang]:
                            if 'text' in sub:
                                transcript += sub['text'] + " "
                        if transcript:
                            return transcript.strip()
                
                # Try automatic captions
                automatic_captions = info.get('automatic_captions', {})
                for lang in ['en', 'es', 'fr', 'de']:
                    if lang in automatic_captions and automatic_captions[lang]:
                        transcript = ""
                        for sub in automatic_captions[lang]:
                            if 'text' in sub:
                                transcript += sub['text'] + " "
                        if transcript:
                            return transcript.strip()
                
                return None
        except ImportError:
            print("yt-dlp not installed, skipping")
            return None
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return None
    
    def process_video(self, video_url: str, language: str = 'en', progress_callback=None):
        video_id = self.extract_video_id(video_url)
        cache_key = f"{video_id}_{language}"
        
        if cache_key in self.vectorstores:
            return cache_key
        
        if progress_callback:
            progress_callback("Getting transcript...", 20)
        
        transcript = self.get_transcript(video_id, language)
        
        if progress_callback:
            progress_callback("Splitting text into chunks...", 40)
        
        chunks = self.text_splitter.create_documents([transcript])
        
        if progress_callback:
            progress_callback("Creating embeddings...", 60)
        
        embeddings = HuggingFaceEndpointEmbeddings(
            model=self.embedding_model,
            huggingfacehub_api_token=self.huggingface_token
        )
        
        if progress_callback:
            progress_callback("Building vector store...", 80)
        
        vector_store = FAISS.from_documents(chunks, embeddings)
        self.vectorstores[cache_key] = vector_store
        
        if progress_callback:
            progress_callback("Processing complete!", 100)
        
        return cache_key
    
    def query_video(self, video_url: str, question: str, language: str = 'en'):
        cache_key = self.process_video(video_url, language)
        vector_store = self.vectorstores[cache_key]
        
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        parallel_chain = RunnableParallel({
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        })
        
        # Use a smaller model to avoid rate limits
        model_name = 'google/flan-t5-large'
        
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            task="text-generation",
            max_new_tokens=256,
            do_sample=False,
            repetition_penalty=1.03,
            huggingfacehub_api_token=self.huggingface_token
        )
        
        chat_model = ChatHuggingFace(llm=llm)
        parser = StrOutputParser()
        
        main_chain = parallel_chain | self.prompt | chat_model | parser
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                answer = main_chain.invoke(question)
                return answer
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    time.sleep(30)
                    continue
                raise e
        
        raise Exception("Max retries exceeded")
