"""
QA Chain Module
Handles LangChain QA chain setup with Gemini LLM
"""

from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL, TEMPERATURE, QA_PROMPT_TEMPLATE, TOP_K_RESULTS


class QAChainManager:
    """Manages QA chain operations with Gemini LLM"""
    
    def __init__(self, api_key: str):
        """
        Initialize QA chain manager
        
        Args:
            api_key: Google API key for Gemini
        """
        if not api_key:
            raise ValueError("Google API key is required")
        
        self.api_key = api_key
        self.llm = None
        self.qa_chain = None
        self.retriever = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize Gemini LLM"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=self.api_key,
                temperature=TEMPERATURE
            )
        except Exception as e:
            raise Exception(f"Error initializing Gemini LLM: {str(e)}")
    
    def create_qa_chain(self, vector_store):
        """
        Create a RAG chain with custom prompt
        
        Args:
            vector_store: ChromaDB vector store instance
            
        Returns:
            RAG chain instance
        """
        if vector_store is None:
            raise ValueError("Vector store is required to create QA chain")
        
        try:
            # Create retriever from vector store (MMR for diversity)
            retriever = vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": TOP_K_RESULTS,
                    "fetch_k": max(10, TOP_K_RESULTS * 3),
                    "lambda_mult": 0.25,
                },
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(QA_PROMPT_TEMPLATE)
            
            # Create chain: retriever -> format_docs -> prompt -> llm -> parser
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            # Store retriever for later use
            self.retriever = retriever
            
            self.qa_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            return self.qa_chain
            
        except Exception as e:
            raise Exception(f"Error creating QA chain: {str(e)}")
    
    def ask_question(
        self, 
        question: str, 
        vector_store
    ) -> Dict[str, Any]:
        """
        Ask a question and get an answer with source documents
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        # Create or update QA chain
        if self.qa_chain is None:
            self.create_qa_chain(vector_store)
        
        try:
            # Get relevant documents
            source_docs = self.retriever.get_relevant_documents(question)
            
            # Heuristic extractive answer for goal/objective-style questions
            lower_q = question.lower()
            keywords = ["goal", "objective", "purpose", "aim", "mission"]
            extractive = None
            if any(k in lower_q for k in keywords):
                snippets = []
                for doc in source_docs:
                    lines = [l.strip() for l in doc.page_content.split('\n') if l.strip()]
                    for i, line in enumerate(lines):
                        llow = line.lower()
                        if any(k in llow for k in keywords):
                            window = " ".join(lines[max(0, i-1):min(len(lines), i+3)])
                            snippets.append(window)
                if snippets:
                    # Deduplicate and compact
                    joined = " ".join(snippets)
                    # Keep to ~350 chars
                    extractive = (joined[:350] + "...") if len(joined) > 350 else joined
            
            # Query the chain
            answer = self.qa_chain.invoke(question)
            answer = answer.strip()
            
            # Prefer extractive if available and concise
            if extractive and (len(answer) < 10 or len(extractive) < len(answer) * 0.7):
                answer = extractive
            
            response = {
                "answer": answer,
                "source_documents": source_docs
            }
            
            return response
            
        except Exception as e:
            raise Exception(f"Error processing question: {str(e)}")
    
    def format_sources(self, source_documents) -> str:
        """
        Format source documents into readable citation text
        
        Args:
            source_documents: List of source Document objects
            
        Returns:
            Formatted string with source citations
        """
        if not source_documents:
            return "No sources found"
        
        citations = []
        seen_sources = set()
        
        for doc in source_documents:
            source = doc.metadata.get("source", "Unknown")
            
            # Only include each source once
            if source not in seen_sources:
                seen_sources.add(source)
                
                # Get additional metadata
                chunk_info = ""
                if "pages" in doc.metadata:
                    chunk_info = f" (PDF, {doc.metadata['pages']} pages)"
                elif "paragraphs" in doc.metadata:
                    chunk_info = f" (DOCX, {doc.metadata['paragraphs']} paragraphs)"
                elif "lines" in doc.metadata:
                    chunk_info = f" (TXT, {doc.metadata['lines']} lines)"
                
                citations.append(f"• {source}{chunk_info}")
        
        return "\n".join(citations)
    
    def format_source_chunks(self, source_documents) -> str:
        """
        Compact chunk preview for debugging; prefer format_sources for UI.
        """
        if not source_documents:
            return "No source chunks available"
        lines = []
        for idx, doc in enumerate(source_documents, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk_idx = doc.metadata.get("chunk_index", "?")
            preview = doc.page_content.replace("\n", " ")
            if len(preview) > 180:
                preview = preview[:180] + "..."
            lines.append(f"• {source} (chunk {chunk_idx}): {preview}")
        return "\n".join(lines)
