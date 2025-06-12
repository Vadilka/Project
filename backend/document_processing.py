import PyPDF2
import pandas as pd
from bs4 import BeautifulSoup
import io
import logging
from typing import List, Dict, Any
import re
import traceback
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
        
    # Limit maximum text size to prevent memory issues
    MAX_TEXT_SIZE = 10_000_000  # 10MB of text
    if len(text) > MAX_TEXT_SIZE:
        logger.warning(f"Text too large ({len(text)} chars), truncating to {MAX_TEXT_SIZE} chars")
        text = text[:MAX_TEXT_SIZE]
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to find a good breaking point
        if end < text_length:
            # Look for sentence endings
            for sep in ['. ', '! ', '? ', '\n']:
                last_sep = text.rfind(sep, start, end)
                if last_sep != -1 and last_sep > start + chunk_size // 2:
                    end = last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position, accounting for overlap
        start = end - overlap if end < text_length else end
        
        # Safety check to prevent infinite loops
        if start >= end:
            break
    
    logger.info(f"Created {len(chunks)} chunks from text of length {text_length}")
    return chunks

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def process_pdf(content: bytes) -> List[str]:
    """
    Process PDF document
    
    Args:
        content: PDF file content as bytes
        
    Returns:
        List of text chunks
    """
    try:
        pdf_file = io.BytesIO(content)
        logger.info("Created BytesIO object from PDF content")
        
        pdf_reader = PdfReader(pdf_file)
        logger.info(f"PDF loaded successfully. Number of pages: {len(pdf_reader.pages)}")
        
        text = ""
        for i, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                logger.info(f"Extracted text from page {i}")
            else:
                logger.warning(f"No text extracted from page {i}")
        
        if not text.strip():
            logger.warning("No text content extracted from PDF")
            return []
            
        text = clean_text(text)
        chunks = chunk_text(text)
        logger.info(f"PDF processed successfully. Created {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        raise

def process_csv(content: bytes) -> List[str]:
    """
    Process CSV document
    
    Args:
        content: CSV file content as bytes
        
    Returns:
        List of text chunks
    """
    try:
        df = pd.read_csv(io.BytesIO(content))
        text = df.to_string(index=False)
        text = clean_text(text)
        return chunk_text(text)
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise

def process_html(content: bytes) -> List[str]:
    """
    Process HTML document
    
    Args:
        content: HTML file content as bytes
        
    Returns:
        List of text chunks
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        text = clean_text(text)
        return chunk_text(text)
        
    except Exception as e:
        logger.error(f"Error processing HTML: {str(e)}")
        raise

def process_document(content: bytes, file_type: str) -> List[str]:
    """
    Process document based on its type
    
    Args:
        content: Document content as bytes
        file_type: Type of document (pdf, csv, or html)
        
    Returns:
        List of text chunks
    """
    processors = {
        "pdf": process_pdf,
        "csv": process_csv,
        "html": process_html
    }
    
    if file_type not in processors:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    try:
        return processors[file_type](content)
    except Exception as e:
        logger.error(f"Error processing {file_type} document: {str(e)}")
        raise 