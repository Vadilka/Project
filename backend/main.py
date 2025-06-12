from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Optional
import os
import shutil
import uuid
import requests
from dotenv import load_dotenv
import chromadb

from document_processing import process_document
from vector_store import VectorStore
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HF_API_TOKEN")

app = FastAPI(
    title="Chatbot LLM + RAG dla programu studiów",
    description="API do chatbota odpowiadającego na pytania dotyczące programu studiów z wykorzystaniem LLM i RAG.",
    version="1.0.0"
)

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели для чата
class Message(BaseModel):
    content: str
    role: str = "user"

class ChatRequest(BaseModel):
    query: str
    language: str = "pl"

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

# Initialize vector store
vector_store = VectorStore()

# Генерация ответа через Hugging Face Inference API
def generate_hf_response(prompt, model="mistralai/Mistral-7B-Instruct-v0.2"):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 256}}
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    elif isinstance(result, dict) and "error" in result:
        return f"Błąd API: {result['error']}"
    else:
        return str(result)

@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"status": "ok", "message": "Chatbot LLM + RAG API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the LLM using RAG
    
    Args:
        request: ChatRequest containing query and language
        
    Returns:
        ChatResponse containing answer and sources
    """
    try:
        # Validate language
        if request.language not in ["pl", "en"]:
            raise HTTPException(
                status_code=400,
                detail="Language must be either 'pl' or 'en'"
            )
        
        # Get relevant documents
        relevant_docs = vector_store.search(request.query)
        
        if not relevant_docs:
            return ChatResponse(
                answer="Nie znalazłem odpowiednich informacji w bazie danych. Proszę najpierw załadować dokumenty.",
                sources=[]
            )
        
        # Generate answer using LLM
        answer = vector_store.generate_answer(request.query, relevant_docs, request.language)
        
        return ChatResponse(
            answer=answer,
            sources=[doc if isinstance(doc, str) else getattr(doc, 'page_content', str(doc)) for doc in relevant_docs]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    
    Args:
        file: The document file to upload (PDF, CSV, or HTML)
        
    Returns:
        dict: Status message and number of chunks processed
    """
    try:
        # Validate file type
        allowed_types = {
            "application/pdf": "pdf",
            "text/csv": "csv",
            "text/html": "html"
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types.keys())}"
            )
        
        # Process document
        file_type = allowed_types[file.content_type]
        content = await file.read()
        chunks = process_document(content, file_type)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text content could be extracted from the document"
            )
        
        # Store chunks in vector database
        vector_store.add_documents(chunks)
        
        return {
            "status": "success",
            "message": f"Document processed successfully. {len(chunks)} chunks added to database."
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 