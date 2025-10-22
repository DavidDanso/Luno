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
                temperature=TEMPERATURE,
                convert_system_message_to_human=True
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
            # Create retriever from vector store
            retriever = vector_store.as_retriever(
                search_kwargs={"k": TOP_K_RESULTS}
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(QA_PROMPT_TEMPLATE)
            
            # Create chain: retriever -> format_docs -> prompt -> llm -> parser
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.qa_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            self.retriever = retriever
            
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
        
        Args:
            question: User's question
            vector_store: ChromaDB vector store instance
            
        Returns:
            Dictionary with 'answer' and 'source_documents'
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        # Create or update QA chain
        if self.qa_chain is None:
            self.create_qa_chain(vector_store)
        
        try:
            # Get relevant documents
            source_docs = self.retriever.invoke(question)
            
            # Query the chain
            answer = self.qa_chain.invoke(question)
            
            # Format response
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
        Format source document chunks with metadata for display
        
        Args:
            source_documents: List of source Document objects
            
        Returns:
            Formatted string with document chunks
        """
        if not source_documents:
            return "No source chunks available"
        
        chunks = []
        for idx, doc in enumerate(source_documents, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk_idx = doc.metadata.get("chunk_index", "?")
            content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            
            chunk_text = f"""
**Source {idx}: {source}** (Chunk {chunk_idx})
```
{content}
```
"""
            chunks.append(chunk_text.strip())
        
        return "\n\n".join(chunks)
