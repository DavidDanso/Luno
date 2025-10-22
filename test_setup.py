"""
Setup Test Script
Validates the installation and basic functionality
Run this after installing dependencies to verify everything works
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LangChain: {e}")
        return False
    
    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ChromaDB: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Sentence Transformers: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyPDF2: {e}")
        return False
    
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-docx: {e}")
        return False
    
    return True


def test_config():
    """Test if config file can be loaded"""
    print("\nTesting configuration...")
    
    try:
        import config
        print(f"✅ Config loaded successfully")
        print(f"   - Chunk size: {config.CHUNK_SIZE}")
        print(f"   - Embedding model: {config.EMBEDDING_MODEL}")
        print(f"   - Supported formats: {config.SUPPORTED_FORMATS}")
        return True
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False


def test_utils():
    """Test if utility modules can be imported"""
    print("\nTesting utility modules...")
    
    try:
        from utils.document_processor import DocumentProcessor
        print("✅ DocumentProcessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import DocumentProcessor: {e}")
        return False
    
    try:
        from utils.vector_store import VectorStoreManager
        print("✅ VectorStoreManager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import VectorStoreManager: {e}")
        return False
    
    try:
        from utils.qa_chain import QAChainManager
        print("✅ QAChainManager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import QAChainManager: {e}")
        return False
    
    return True


def test_document_processor():
    """Test basic document processor functionality"""
    print("\nTesting DocumentProcessor...")
    
    try:
        from utils.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test with sample text
        sample_text = b"This is a test document. " * 100
        is_valid, msg = processor.validate_file("test.txt", len(sample_text))
        
        if is_valid:
            print("✅ Document validation works")
        else:
            print(f"❌ Document validation failed: {msg}")
            return False
        
        # Test text extraction
        text, metadata = processor.extract_text_from_txt(sample_text)
        if text:
            print("✅ Text extraction works")
        else:
            print("❌ Text extraction failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ DocumentProcessor test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("NotebookLM Clone - Setup Verification")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Utils Test", test_utils),
        ("Document Processor Test", test_document_processor),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 60)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Add your Google API key to .env file")
        print("2. Run: streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("- Ensure you've activated the virtual environment")
        print("- Run: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
