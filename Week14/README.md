# Agentic RAG with Tavily + OpenRouter

This Streamlit application demonstrates an agentic retrieval-augmented generation (RAG) system that intelligently routes queries to the most appropriate source:

- 📚 Wikipedia for encyclopedic information
- 🔬 ArXiv for academic papers
- 🌐 Web Search via Tavily for current information
- 📄 PDF documents uploaded by the user

## Features

- Smart query routing to the most appropriate source
- PDF document upload and indexing for RAG
- Environment variable support for API keys
- Streamlit-based user interface

## API Keys

The application requires two API keys:

1. **OpenRouter API Key** - For accessing language models like GPT-4
2. **Tavily API Key** - For web search capabilities

### Environment Variables

You can pre-load your API keys using a `.env` file with the following variables:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
TVLY_API_KEY=your_tavily_api_key_here
```

If these environment variables are set, the application will automatically use them as default values in the UI.

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API keys (optional but recommended)

3. Run the application:
   ```
   streamlit run arag.py
   ```

## Usage

1. Enter your API keys in the sidebar (if not pre-loaded from `.env`)
2. Upload PDF documents for RAG context (optional)
3. Enter your query in the text input
4. Click "Run Query" to get results

The system will automatically choose the best source for your query and provide relevant information.

## Troubleshooting

If you encounter warnings about deprecated imports, make sure you have the latest versions of the required packages installed. The application has been updated to use the latest LangChain packages:

- `langchain_community.vectorstores.FAISS` instead of `langchain.vectorstores.FAISS`
- `langchain_huggingface.HuggingFaceEmbeddings` instead of `langchain_community.embeddings.HuggingFaceEmbeddings`

