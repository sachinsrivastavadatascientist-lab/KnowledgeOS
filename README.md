# 📚 Knowledge OS – AI-Powered RAG Application

An intelligent document question-answering system built using **Retrieval-Augmented Generation (RAG)**. Upload your documents, ask questions in natural language, and get context-aware answers grounded in your uploaded knowledge base.

The goal is to build a flexible and scalable document intelligence platform supporting multiple LLM providers, embedding models, and vector databases.

---

## 🚀 Key Features

- **Document Upload:** Upload and process documents for intelligent retrieval.
- **Retrieval-Augmented Generation (RAG):** Generate answers using relevant document context.
- **Multiple LLM Providers:** Support for Groq, OpenAI, Gemini, Claude, Hugging Face, and Ollama.
- **Multiple Embedding Models:** Use OpenAI, Hugging Face, or Gemini embeddings.
- **Flexible Vector Storage:** Support for in-memory, on-disk, and cloud-based vector databases.
- **Semantic Search:** Retrieve relevant information based on contextual similarity.
- **Context-Aware Responses:** Generate answers using retrieved document information.
- **Modular Architecture:** Easily extend the application with new models and vector databases.

---

## 🏗️ Architecture Overview

The application follows a Retrieval-Augmented Generation pipeline.

```text
                 USER
                   |
                   v
           Document Upload
                   |
                   v
          Document Processing
                   |
                   v
             Text Splitting
                   |
                   v
           Embedding Generation
                   |
                   v
             Vector Database
                   |
                   |
             User Question
                   |
                   v
          Question Embedding
                   |
                   v
            Similarity Search
                   |
                   v
          Relevant Documents
                   |
                   v
             LLM Processing
                   |
                   v
             Final Answer
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.10 |
| Framework | LangChain |
| LLM Orchestration | LangChain / LangGraph |
| LLM Providers | Groq, OpenAI, Gemini, Claude, Hugging Face, Ollama |
| Embedding Models | OpenAI, Hugging Face, Gemini |
| Vector Databases | In-Memory, On-Disk, Cloud-Based |
| Version Control | Git & GitHub |
| Development Environment | VS Code |

---

## 🤖 Supported LLM Providers

The application is designed to support multiple LLM providers.

| Provider | Access |
|---|---|
| Groq | Free tier available |
| OpenAI | Paid API |
| Google Gemini | Free tier available, subject to limits |
| Anthropic Claude | Paid API |
| Hugging Face | Free models and paid services |
| Ollama | Local model execution |

**Note:** API availability, pricing, rate limits, and free-tier eligibility depend on the provider and may change.

---

## 🔢 Embedding Models

Embedding models convert text into numerical vectors that represent semantic meaning.

Supported providers:

- OpenAI Embeddings
- Hugging Face Embeddings
- Google Gemini Embeddings

---

## 🗄️ Vector Database Options

The project supports three categories of vector storage:

| Type | Description |
|---|---|
| In-Memory | Stores vectors temporarily in memory |
| On-Disk | Persists vector data locally |
| Cloud-Based | Stores and retrieves vectors through cloud infrastructure |

Examples include FAISS, ChromaDB, and Astra DB.

---

## 📋 Prerequisites

Before starting, make sure you have:

- Python 3.10
- Anaconda or Miniconda
- Git
- Visual Studio Code
- Required API keys depending on your selected LLM and embedding providers

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sunnysavita10/document_portal.git
```

### 2. Navigate to the Project Directory

```bash
cd document_portal
```

### 3. Open in VS Code

```bash
code .
```

### 4. Create a Conda Environment

```bash
conda create -p ./venv python=3.10 -y
```

### 5. Activate the Environment

```bash
conda activate ./venv
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Configuration

The application may require API keys depending on the selected LLM and embedding providers.

### Groq API

- Get API Key: https://console.groq.com/keys
- Documentation: https://console.groq.com/docs/overview

### Google Gemini API

- Get API Key: https://aistudio.google.com/apikey
- Documentation: https://ai.google.dev/gemini-api/docs/models

### OpenAI API

- Get API Key: https://platform.openai.com/api-keys
- Documentation: https://platform.openai.com/docs

### Anthropic Claude API

- Get API Key: https://console.anthropic.com/
- Documentation: https://docs.anthropic.com/

### Hugging Face

- Get API Token: https://huggingface.co/settings/tokens
- Documentation: https://huggingface.co/docs

### Ollama

- Download: https://ollama.com/
- Documentation: https://docs.ollama.com/

---

## 🔐 Environment Variables

Create a `.env` file in the root directory and configure the required credentials.

```env
# LLM Providers
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Hugging Face
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

**Security:** Never commit your `.env` file or expose API keys publicly. Add `.env` to `.gitignore`.

Only configure the credentials required by your selected providers.

---

## ▶️ Running the Application

After installing dependencies and configuring the required environment variables, run the application using the appropriate entry point.

For example, if the application uses FastAPI:

```bash
uvicorn main:app --reload
```

If it uses Streamlit:

```bash
streamlit run app.py
```

Replace the command with the actual entry point used in your project.

---

## 📁 Project Structure

```text
document_portal/
│
├── src/
│   ├── ...
│
├── data/
│
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── ...
```

The exact structure may vary depending on the implementation.

---

## 🔄 Git & GitHub Workflow

Initialize Git:

```bash
git init
```

Stage project files:

```bash
git add .
```

Commit changes:

```bash
git commit -m "Initial project setup"
```

Add the GitHub remote:

```bash
git remote add origin https://github.com/USERNAME/REPOSITORY.git
```

Push to GitHub:

```bash
git branch -M main
git push -u origin main
```

For subsequent updates:

```bash
git add .
git commit -m "Update document portal"
git push
```

---

## 🔮 Future Enhancements

Potential improvements for the project:

- Hybrid Search (Semantic + Keyword Search)
- Advanced Document Chunking Strategies
- Reranking Models
- Conversation History and Memory
- Multi-Document Retrieval
- Agentic RAG Workflows
- Authentication and Authorization
- Multitenant Architecture
- API Rate Limiting and Caching
- Production Deployment and Monitoring

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## 📄 License

This project is available under the license specified in the repository.

---

**Built with Python, LangChain, and modern Generative AI technologies.**
