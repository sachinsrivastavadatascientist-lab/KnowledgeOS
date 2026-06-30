import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

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
retriever_store = {}
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

# class FastAPIFileAdapter:
#     """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
#     def __init__(self, uf: UploadFile):
#         self._uf = uf
#         self.name = uf.filename
#     def getbuffer(self) -> bytes:
#         self._uf.file.seek(0)
#         return self._uf.file.read()

# def _read_pdf_via_handler(handler: DocHandler, path: str) -> str:
#     """
#     Helper function to read PDF using DocHandler.
#     """
#     try:
#         if hasattr(handler, "read_pdf"):
#             return handler.read_pdf(path)  # type: ignore
#         if hasattr(handler, "read_"):
#             return handler.read_(path)  # type: ignore
#         raise RuntimeError("DocHandler has neither read_pdf nor read_ method.")

    # except Exception as e:
    #     return handler.read_pdf(path)
    #     raise HTTPException(status_code=
    # \500, detail=f"Error reading PDF: {str(e)}")        


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
                     session_id:Optional[str]=Form(None),
                     use_session_dirs: bool = Form(True),
                     chunk_size: int = Form(1000),
                     chunk_overlap: int =Form(200),
                     k: int =Form(5),
                )->Any:
    try:
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
                  temp_base=UPLOAD_BASE,
                  faiss_base=FAISS_BASE,
                  use_session_dirs=use_session_dirs,
                  session_id=session_id or None,
        )
        retriever = ci.build_retriever(wrapped,chunk_size=chunk_size,chunk_overlap=chunk_overlap,k=k)
        retriever_store[ci.session_id] = retriever
        ##############################################
        print("INDEX STORE:", retriever_store)
        print("INDEX STORE ID:", id(retriever_store))
        ##############################################
        return {'session_id':ci.session_id,"k":k,"use_session_dirs":use_session_dirs}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        print(type(e))
        print(repr(e))
        raise
@app.post("/chat/query")
async def chat_query(
              question:str=Form(...),
              session_id:Optional[str]=Form(None),
              use_session_dirs: bool = Form(True),
              k:int =Form(5),
             )->Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400,detail="session_id is required when use_session_dirs is True")
        #PREPAING FAISS INDEX
        index_dir = os.path.join(FAISS_BASE,session_id) if use_session_dirs else FAISS_BASE   
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404,detail="no index found for this session") 

        # INITALIZING LCEL - styleRAG PIPELINE
        retriever = retriever_store.get(session_id)
        print(retriever)
        print(retriever_store.keys())
        rag = ConversationalRAG(
            retriever=retriever
        )
        #rag.load_retriever_from_faiss(index_dir)

        # optional for rag we pass emty chat history
        response = rag.invoke(question)

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine":"LCEL-RAG"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        print(type(e))
        print(repr(e))
        raise