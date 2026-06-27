import importlib.metadata

packages = [
    "ipykernel>=7.3.0",
    "python-dotenv",
    "langchain==1.2.18",
    "langchain-core",
    "langgraph==1.1.10",
    "langsmith==0.8.3",
    "langchain-groq==1.1.2",
    "langchain-community==0.4.1",
    "langchain-huggingface==1.2.2",
    "openai",
    "streamlit",
    "duckduckgo-search",
    "ddgs",
    "faiss-cpu",
    "sentence-transformers",
    "structlog",
    "pymupdf",
    "langchain-google-genai",
    "langchain-openai",
    "langchain_anthropic",
    "pypdf",
    "pandas",
    "streamlit",
    "pytest",
    "langchain-core[tracing]",
    "docx2txt",
    "fastapi",
    "uvicorn",
    "python-multipart",
    "jinja2",
    "pydantic",
    
]
for pkg in packages:
    try:
        version = importlib.metadata.version(pkg)
        print(f"{pkg}=={version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{pkg} (not installed)")
