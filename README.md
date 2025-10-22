# 📚 NotebookLM Clone - Production-Grade Document Q&A System

A fully functional NotebookLM clone built with Python, LangChain, and Google Gemini. Upload documents, ask questions, and get AI-powered answers with source citations.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1.0+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### Core Functionality
- **Multi-Format Support**: Upload PDF, TXT, and DOCX documents
- **Intelligent Chunking**: Documents split with overlap for better context preservation
- **Semantic Search**: Find relevant information using vector embeddings
- **AI-Powered Q&A**: Get accurate answers using Google Gemini
- **Source Citations**: Every answer includes references to source documents
- **Conversation History**: Track all your questions and answers
- **Document Management**: Add, view, and delete documents easily

### Technical Features
- **Persistent Storage**: ChromaDB vector database survives restarts
- **Professional UI**: Clean, responsive Streamlit interface
- **Error Handling**: Comprehensive validation and error messages
- **Production-Ready**: Modular architecture, type hints, and documentation
- **Fast Performance**: Optimized for queries under 3 seconds

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
cd notebooklm-clone
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Configure API Key
- If not set in `.env`, enter your Google API key in the sidebar
- Click outside the input field to initialize the system

### Step 2: Upload Documents
1. Click "Browse files" in the sidebar
2. Select one or more documents (PDF, TXT, or DOCX)
3. Click "Process Documents"
4. Wait for processing confirmation

### Step 3: Ask Questions
1. Type your question in the input field
2. Click "Ask" or press Enter
3. View the AI-generated answer with source citations
4. Expand "View Sources" to see relevant document chunks

### Step 4: Manage Documents
- View all loaded documents in the sidebar
- Delete individual documents with the 🗑️ button
- Clear all data with "Clear All Data" button

## 🏗️ Project Structure

```
notebooklm-clone/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and constants
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not committed)
├── .env.example                   # Example environment file
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── utils/
│   ├── document_processor.py      # Document loading and chunking
│   ├── vector_store.py           # ChromaDB operations
│   └── qa_chain.py               # LangChain QA setup
└── chroma_db/                    # ChromaDB persistent storage (auto-created)
```

## 🔧 Configuration

### Environment Variables
Edit `.env` file:
```bash
GOOGLE_API_KEY=your_api_key_here
```

### Application Settings
Edit `config.py` to customize:
- **Chunk Size**: Default 1000 characters
- **Chunk Overlap**: Default 200 characters
- **Max File Size**: Default 10MB
- **Embedding Model**: Default 'all-MiniLM-L6-v2'
- **LLM Temperature**: Default 0.7
- **Top K Results**: Default 4 relevant chunks

## 🛠️ Architecture

### Document Processing Flow
1. **Upload**: User uploads document via Streamlit
2. **Validation**: Check format and file size
3. **Extraction**: Extract text based on file type
4. **Chunking**: Split text with overlap using RecursiveCharacterTextSplitter
5. **Embedding**: Generate vector embeddings using sentence-transformers
6. **Storage**: Store in ChromaDB with metadata

### Q&A Flow
1. **Query**: User asks a question
2. **Retrieval**: Find top K relevant chunks via semantic search
3. **Context Building**: Combine retrieved chunks as context
4. **LLM Generation**: Send to Gemini with custom prompt
5. **Response**: Return answer with source citations

## 📦 Dependencies

### Core Libraries
- **streamlit**: Web interface
- **langchain**: LLM orchestration framework
- **langchain-google-genai**: Google Gemini integration
- **chromadb**: Vector database for embeddings
- **sentence-transformers**: Text embedding models

### Document Processing
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX text extraction

### Utilities
- **python-dotenv**: Environment variable management

## 🔍 Troubleshooting

### Common Issues

**Issue**: "Google API key is required"
- **Solution**: Add your API key to `.env` file or enter it in the sidebar

**Issue**: "Error extracting text from PDF"
- **Solution**: Ensure PDF contains extractable text (not scanned images)

**Issue**: "ChromaDB initialization failed"
- **Solution**: Delete `chroma_db/` folder and restart the application

**Issue**: "Module not found"
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Slow performance
- **Solution**: Reduce chunk size or top K results in `config.py`

## 🎯 Best Practices

### Document Upload
- Use clear, descriptive filenames
- Ensure documents contain readable text
- Keep files under 10MB for optimal performance
- Upload related documents together for cross-referencing

### Asking Questions
- Be specific and clear in your questions
- Reference document names if asking about specific files
- Use follow-up questions to dive deeper
- Check source citations for accuracy

### Performance Optimization
- Delete unused documents regularly
- Use "Clear All Data" to reset the system
- Restart the app periodically for best performance

## 🚀 Deployment

### Local Deployment
The application runs locally by default. For production deployment:

### Docker Deployment (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t notebooklm-clone .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key notebooklm-clone
```

### Cloud Deployment
Compatible with:
- **Streamlit Community Cloud**: Push to GitHub and deploy
- **Heroku**: Add `Procfile` and deploy
- **AWS/GCP/Azure**: Deploy as containerized application

## 📝 API Rate Limits

- **Gemini API**: Check [Google's documentation](https://ai.google.dev/docs/rate_limits) for current limits
- **Recommended**: Implement rate limiting for production use
- **Caching**: Consider caching frequent queries

## 🤝 Contributing

This is a portfolio project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: Powerful LLM orchestration framework
- **Google Gemini**: State-of-the-art language model
- **ChromaDB**: Fast and efficient vector database
- **Streamlit**: Beautiful and easy-to-use web framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Gemini API Guide](https://ai.google.dev/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Built with ❤️ for portfolio demonstration and learning purposes**

⭐ Star this repository if you find it useful!
