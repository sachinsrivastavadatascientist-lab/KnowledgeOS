import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils.session_manager import SessionManager
from fastapi.responses import StreamingResponse


from src.document_ingestion.data_ingestion import(
    DocHandler,
    FaissManager,
    ChatIngestor,
    DocumentCompareor
)

from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_compare import DocumentCompareLLM
from src.document_chat.retrieval import ConversationalRAG

from utils.document_ops import FastAPIFileAdapter,read_pdf_via_handler

FAISS_BASE = os.getenv("FAISS_BASE","faiss_index")
UPLOAD_BASE= os.getenv("UPLOAD_BASE","data")
session_manager = SessionManager()
import traceback

##### for correct code#################
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"
#################################


app = FastAPI(title="KnowledgeOS API",version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/health")
def health()->Dict[str,str]:
    return {"status":"ok","service":"knowledge-os"}


@app.post("/analyze")
async def analyze_document(file: UploadFile=File(...)):
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = read_pdf_via_handler(dh,saved_path)

        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        print(type(result)) ## replace after checking
        print(result) ## replace ater checking
        return JSONResponse(content=result.dict())
    except HTTPException:
        raise   
    except Exception as e:
        traceback.print_exc()
        print(type(e))
        print(repr(e))
        raise


@app.post("/compare")
async def compare_documents(reference:UploadFile=File(...),
                            actual:UploadFile=File(...)):
    try:
        dc =DocumentCompareor()
        ref_path,act_path = dc.save_uploaded_files(FastAPIFileAdapter(reference),FastAPIFileAdapter(actual))
        _ =ref_path,act_path
        combined_text = dc.combine_documents()
        comp = DocumentCompareLLM()
        df =comp.compare_documents(combined_text)
        return {"rows":df.to_dict(orient="records"),"session_id":dc.session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        print(type(e))
        print(repr(e))
        raise

@app.post("/chat/index")
async def chat_build_index(
                     files:List[UploadFile]=File(...),
                     use_session_dirs: bool = Form(True),
                     chunk_size: int = Form(1000),
                     chunk_overlap: int =Form(200),
                     user_id: str = Form(...),
                     k: int =Form(5),
                )->Any:
    try:
        session_id = session_manager.generate_session_id(user_id)
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
                  temp_base=UPLOAD_BASE,
                  faiss_base=FAISS_BASE,
                  use_session_dirs=use_session_dirs,
                  session_id=session_id,
                  user_id=user_id,
        )
        retriever = ci.build_retriever(wrapped,chunk_size=chunk_size,chunk_overlap=chunk_overlap,k=k)
        faiss_path = str(ci.faiss_manager.index_dir)
        session_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            faiss_path=faiss_path
        )

        return {"session_id": session_id,
                "status": "index_created"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        print(type(e))
        print(repr(e))
        raise

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    user_id: str = Form(...),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:

    try:

        # ===== VALIDATION =====
        if use_session_dirs and not session_id:
            raise HTTPException(
                status_code=400,
                detail="session_id is required when use_session_dirs=True"
            )

        print(f"\n{'='*60}")
        print("CHAT QUERY REQUEST")
        print(f"User ID    : {user_id}")
        print(f"Session ID : {session_id}")
        print(f"Question   : {question}")
        print(f"{'='*60}\n")

        # ==========================================================
        # Get Session from MongoDB
        # ==========================================================

        session = session_manager.get_session(
            session_id=session_id,
            user_id=user_id
        )

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        print("✓ Session Found")
        print(session)

        # ==========================================================
        # Load FAISS
        # ==========================================================

        faiss_path = session["faiss_path"]

        faiss_manager = FaissManager(
            index_dir=faiss_path
        )

        retriever = faiss_manager.load_retriever(
            k=k
        )

        print("✓ Retriever Loaded")

        # ==========================================================
        # Build RAG
        # ==========================================================

        rag = ConversationalRAG(
            session_id=session_id,
            retriever=retriever,
            user_id=user_id,
        )

        print("✓ RAG Created")

        # ==========================================================
        # Invoke
        # ==========================================================

       # rag.invoke(question)

        print("✓ Response Generated")

        # ==========================================================
        # Update Last Access Time
        # ==========================================================

        session_manager.touch_session(
            session_id=session_id
        )


        return StreamingResponse(
            rag.invoke(question),
            media_type="text/plain"
        )

        # return {
        #     "answer": response,
        #     "session_id": session_id,
        #     "user_id": user_id,
        #     "k": k,
        #     "engine": "LCEL-RAG",
        #     "status": "success"
        # }

    except HTTPException:
        raise

    except Exception as e:

        print(f"\n{'❌'} ERROR IN /chat/query")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )