import os
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
import logging
from dotenv import load_dotenv
import requests
import json
from website_scraper import SANScraper

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self):
        """Initialize vector store with ChromaDB and sentence transformer model"""
        try:
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(path="chroma_db")
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize sentence transformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Groq API settings
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # Можно задать через env
            
            # Initialize with website data if collection is empty
            if self.collection.count() == 0:
                self._initialize_with_website_data()
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def _initialize_with_website_data(self):
        """Initialize vector store with data from SAN website"""
        try:
            logger.info("Initializing vector store with website data...")
            scraper = SANScraper()
            content = scraper.get_all_content()
            
            if not content:
                logger.warning("No content found on website")
                return
            
            # Process and add content
            for item in content:
                # Create chunks from content
                chunks = self._create_chunks(item['content'])
                
                # Generate embeddings
                embeddings = self.model.encode(chunks)
                
                # Add to collection
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=chunks,
                    ids=[f"website_{item['title']}_{i}" for i in range(len(chunks))],
                    metadatas=[{
                        'source': 'website',
                        'title': item['title'],
                        'url': item.get('url', '')
                    } for _ in chunks]
                )
            
            logger.info(f"Added {len(content)} items from website to vector store")
            
        except Exception as e:
            logger.error(f"Error initializing with website data: {str(e)}")
            raise
    
    def _create_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            if end > text_length:
                end = text_length
            else:
                # Try to find a good breaking point
                last_period = text.rfind('.', start, end)
                if last_period != -1 and last_period > start + chunk_size // 2:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def add_documents(self, chunks: List[str]) -> None:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of text chunks to add
        """
        try:
            # Generate embeddings
            embeddings = self.model.encode(chunks)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                ids=[f"doc_{i}" for i in range(len(chunks))],
                metadatas=[{'source': 'uploaded_document'} for _ in chunks]
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 1) -> list:
        """
        Search for relevant documents
        """
        try:
            query_embedding = self.model.encode(query)
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            return results["documents"][0]
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    def generate_answer(self, query: str, context: list, language: str = "pl") -> str:
        """
        Generate answer using Groq API (OpenAI-compatible)
        """
        try:
            if language == "pl":
                system_prompt = (
                    "Jesteś pomocnym asystentem. Odpowiadaj wyłącznie na podstawie poniższego kontekstu. "
                    "Jeśli odpowiedzi nie ma w kontekście, odpowiedz: 'Nie wiem.'"
                )
                context_label = "Kontekst"
                question_label = "Pytanie"
                answer_label = "Odpowiedź"
                idk = "Nie wiem."
            else:
                system_prompt = (
                    "You are a helpful assistant. Answer ONLY based on the context below. "
                    "If the answer is not in the context, say: 'I don't know.'"
                )
                context_label = "Context"
                question_label = "Question"
                answer_label = "Answer"
                idk = "I don't know."
            context_text = "\n".join(context)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<{context_label}>\n{context_text}\n</{context_label}>"},
                {"role": "user", "content": f"<{question_label}>{query}</{question_label}>\n<{answer_label}>"}
            ]
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.groq_model,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.7
            }
            response = requests.post(self.groq_api_url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"Groq API error {response.status_code}: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            result = response.json()
            logger.info(f"Groq API raw response: {result}")
            answer = result["choices"][0]["message"]["content"].strip()
            # Если ответ слишком похож на контекст — вернуть 'I don't know.'
            if answer.strip() == context_text.strip() or len(answer.strip()) < 5:
                return idk
            return answer
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            if language == "pl":
                return "Przepraszam, wystąpił błąd podczas generowania odpowiedzi."
            else:
                return "Sorry, an error occurred while generating the answer." 