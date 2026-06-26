# utils/rag_utils.py - Updated for LangChain 0.2+
import os
import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import time

class RAGProcessor:
    def __init__(self, huggingface_token=None):
        self.huggingface_token = huggingface_token
        if not self.huggingface_token:
            raise ValueError("HUGGINGFACE_API_KEY not set")
        
        self.embedding_model = "sentence-transformers/all-mpnet-base-v2"
        self.yapi = YouTubeTranscriptApi()
        
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
    
    def extract_video_id(self, video_url: str) -> str:
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
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
        
        try:
            language_codes = {
                'en': ['en'],
                'es': ['es', 'es-ES'],
                'fr': ['fr', 'fr-FR'],
                'de': ['de', 'de-DE'],
                'hi': ['hi'],
                'ja': ['ja'],
                'zh': ['zh', 'zh-CN', 'zh-TW'],
                'ar': ['ar'],
            }.get(language, ['en'])
            
            transcript_list = self.yapi.fetch(video_id, languages=language_codes)
            transcript = " ".join(snippet.text for snippet in transcript_list)
            self.transcript_cache[cache_key] = transcript
            return transcript
            
        except TranscriptsDisabled:
            raise Exception(f"No captions available for video {video_id} in language {language}")
        except Exception as e:
            raise Exception(f"Error getting transcript: {str(e)}")
    
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
        
        # Use a smaller, faster model to avoid rate limits
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
        
        # Add retry logic for rate limits
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
