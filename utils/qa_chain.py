"""
QA Chain Module
Handles LangChain QA chain setup with Gemini LLM
"""

from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL, TEMPERATURE, TOP_K_RESULTS


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
        if vector_store is None:
            raise ValueError("Vector store is required")
        
        try:
            self.retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": TOP_K_RESULTS}
            )
            
            template = """Answer based on context. Be direct and concise (1-3 sentences max).

Context:
{context}

Question: {question}

Answer:"""
            
            prompt = ChatPromptTemplate.from_template(template)
            
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.qa_chain = (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
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
            source_docs = self.retriever.invoke(question)
            answer = self.qa_chain.invoke(question)
            
            return {
                "answer": answer.strip(),
                "source_documents": source_docs
            }
            
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
