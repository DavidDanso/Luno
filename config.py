"""
Configuration file for NotebookLM Clone
Contains all constants, settings, and environment variable loading
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Embedding Model Configuration
EMBEDDING_MODEL = "all-mpnet-base-v2"

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported file formats
SUPPORTED_FORMATS = [".pdf", ".txt", ".docx"]

# ChromaDB Configuration
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

# Vector Search Configuration
TOP_K_RESULTS = 4

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.7

# UI Configuration
APP_TITLE = "Luno AI"
APP_DESCRIPTION = "Upload documents and ask questions using AI-powered semantic search"

# Custom QA Prompt Template
QA_PROMPT_TEMPLATE = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer or if the answer is not contained in the context, just say "I don't know based on the provided documents" - don't try to make up an answer.
Always cite the source documents when providing answers.

Context:
{context}

Question: {question}

Answer with citations:"""
