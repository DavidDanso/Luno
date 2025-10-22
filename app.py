"""
Luno AI - Main Application
A production-grade document Q&A system using LangChain and Gemini
"""

import streamlit as st
import os
from pathlib import Path

from config import (
    APP_TITLE, 
    APP_DESCRIPTION, 
    GOOGLE_API_KEY,
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE_MB
)
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStoreManager
from utils.qa_chain import QAChainManager


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
        background-color: #f0f8ff;
    }
    .source-citation {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f5f5f5;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    .document-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 0.3rem;
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'vector_store_manager' not in st.session_state:
        st.session_state.vector_store_manager = None
    
    if 'qa_manager' not in st.session_state:
        st.session_state.qa_manager = None
    
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'api_key_validated' not in st.session_state:
        st.session_state.api_key_validated = False


def initialize_managers(api_key: str):
    """Initialize vector store and QA managers"""
    try:
        if st.session_state.vector_store_manager is None:
            with st.spinner("Initializing vector store..."):
                st.session_state.vector_store_manager = VectorStoreManager()
        
        if st.session_state.qa_manager is None:
            with st.spinner("Initializing AI system..."):
                st.session_state.qa_manager = QAChainManager(api_key)
        
        st.session_state.api_key_validated = True
        return True
    
    except Exception as e:
        st.error(f"Initialization error: {str(e)}")
        return False


def handle_file_upload(uploaded_files):
    """Process uploaded files"""
    if not uploaded_files:
        return
    
    success_count = 0
    error_count = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Read file bytes
            file_bytes = uploaded_file.read()
            
            # Process document
            documents = st.session_state.doc_processor.process_document(
                uploaded_file.name, 
                file_bytes
            )
            
            # Add to vector store
            st.session_state.vector_store_manager.add_documents(documents)
            
            # Get document info
            doc_info = st.session_state.doc_processor.get_document_info(documents)
            
            st.success(
                f"✅ {uploaded_file.name}: {doc_info['total_chunks']} chunks created"
            )
            success_count += 1
            
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            error_count += 1
        
        # Update progress
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.empty()
    progress_bar.empty()
    
    # Summary
    if success_count > 0:
        st.success(f"Successfully processed {success_count} document(s)")
    if error_count > 0:
        st.warning(f"Failed to process {error_count} document(s)")


def display_sidebar():
    """Render sidebar with controls"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key input
        api_key = GOOGLE_API_KEY
        if not api_key:
            api_key = st.text_input(
                "Google API Key",
                type="password",
                help="Enter your Gemini API key"
            )
        
        if api_key and not st.session_state.api_key_validated:
            if initialize_managers(api_key):
                st.success("✅ System initialized")
        
        st.markdown("---")
        
        # File uploader
        st.markdown("### 📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=[fmt.replace('.', '') for fmt in SUPPORTED_FORMATS],
            accept_multiple_files=True,
            help=f"Supported formats: {', '.join(SUPPORTED_FORMATS)}. Max size: {MAX_FILE_SIZE_MB}MB"
        )
        
        if uploaded_files and st.button("Process Documents", type="primary"):
            if st.session_state.vector_store_manager is None:
                st.error("Please initialize the system first (enter API key)")
            else:
                handle_file_upload(uploaded_files)
        
        st.markdown("---")
        
        # Document management
        st.markdown("### 📚 Loaded Documents")
        
        if st.session_state.vector_store_manager:
            documents = st.session_state.vector_store_manager.get_all_documents()
            chunk_count = st.session_state.vector_store_manager.get_document_count()
            
            if documents:
                st.info(f"**{len(documents)}** documents ({chunk_count} chunks)")
                
                for doc in documents:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"<div class='document-item'>📄 {doc}</div>", 
                                  unsafe_allow_html=True)
                    with col2:
                        if st.button("🗑️", key=f"del_{doc}"):
                            try:
                                st.session_state.vector_store_manager.delete_document(doc)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("No documents loaded yet")
        
        st.markdown("---")
        
        # Clear all button
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.session_state.vector_store_manager:
                try:
                    st.session_state.vector_store_manager.clear_all_documents()
                    st.session_state.chat_history = []
                    st.success("All data cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def display_chat_interface():
    """Render main chat interface"""
    # Header
    st.markdown(f"<h1 class='main-header'>📚 {APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{APP_DESCRIPTION}</p>", unsafe_allow_html=True)
    
    # Check if system is ready
    if not st.session_state.api_key_validated:
        st.warning("⚠️ Please enter your Google API key in the sidebar to get started")
        return
    
    if not st.session_state.vector_store_manager or \
       st.session_state.vector_store_manager.get_document_count() == 0:
        st.info("📤 Upload documents in the sidebar to start asking questions")
        return
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        for chat in st.session_state.chat_history:
            st.markdown(f"**Q:** {chat['question']}")
            st.markdown(f"<div class='chat-message'>{chat['answer']}</div>", 
                       unsafe_allow_html=True)
            
            if chat['sources']:
                with st.expander("📎 View Sources"):
                    st.markdown(f"<div class='source-citation'>{chat['sources']}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Query input
    st.markdown("### 🔍 Ask a Question")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        question = st.text_input(
            "Your question",
            placeholder="What would you like to know about your documents?",
            label_visibility="collapsed"
        )
    
    with col2:
        ask_button = st.button("Ask", type="primary", use_container_width=True)
    
    # Process question
    if ask_button and question:
        if not question.strip():
            st.warning("Please enter a question")
            return
        
        try:
            with st.spinner("🤔 Thinking..."):
                # Get vector store
                vector_store = st.session_state.vector_store_manager.get_vector_store()
                
                # Ask question
                result = st.session_state.qa_manager.ask_question(
                    question, 
                    vector_store
                )
                
                # Format sources
                sources = st.session_state.qa_manager.format_sources(
                    result['source_documents']
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': question,
                    'answer': result['answer'],
                    'sources': sources
                })
                
                # Rerun to display new message
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Show example questions
    if not st.session_state.chat_history:
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        - What are the main topics covered in these documents?
        - Can you summarize the key points?
        - What does the document say about [specific topic]?
        - Compare the information across different documents
        """)


def main():
    """Main application entry point"""
    initialize_session_state()
    display_sidebar()
    display_chat_interface()


if __name__ == "__main__":
    main()
