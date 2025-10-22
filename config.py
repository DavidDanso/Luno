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
QA_PROMPT_TEMPLATE = """You are a helpful AI assistant. Answer the question based on the context provided below.

Context:
{context}

Question: {question}

Provide a clear, concise answer based on the context above. If the context doesn't contain the answer, say "I don't have enough information in the provided documents to answer that question."""
