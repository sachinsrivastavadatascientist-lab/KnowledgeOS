import sys
import uuid
import docx2txt
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader,TextLoader,UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from datetime import datetime

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class DocumentIngestor:
    SUPPORTED_EXTENSIONS = [".pdf",".docx",".txt",".md"]
    def __init__(self,temp_dir:str = "data\\multi_doc_chat",faiss_dir: str = "faiss_index",session_id:str =None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.model_loader = ModelLoader()
             
            # making temp dir 
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True,exist_ok=True)
            
            # making fiass dir
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True,exist_ok=True)

            #  making session id  dir in temp and fiass
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            self.session_temp_dir = self.temp_dir /self.session_id
            self.session_faiss_path = self.faiss_dir /self.session_id

            self.session_temp_dir.mkdir(parents=True,exist_ok=True)
            self.session_faiss_path.mkdir(parents=True,exist_ok=True)
            
            self.log.info("DocumentIngestor class initated",
            temp_dir=str(self.temp_dir),
            faiss_dir=str(self.faiss_dir),
            session_id=str(self.session_id),
            session_temp_dir = str(self.session_temp_dir),
            session_faiss_path = str(self.session_faiss_path))

        except Exception as e:
            self.log.error("Failed to initate the DocumentIngestor class",error=str(e))
            raise DocumentPortalException("Inialization error in DocumentIngestor",sys)

    def ingest_files(self,uploaded_files):
        try:
            documents = []

            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    self.log.warning("Unsupported file format",filename=uploaded_file.name,extension=ext)
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir/unique_filename

                with open(temp_path,"wb") as f:
                    f.write(uploaded_file.read())
                self.log.info("File saved for processing",filename = uploaded_file.name,extension=ext,saved_as=str(temp_path),session_id = self.session_id)

                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext== ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                elif ext== ".txt":
                    loader = TextLoader(str(temp_path))
                elif ext== ".md":
                    loader = UnstructuredMarkdownLoader(str(temp_path))    
                else:
                    self.log.warning("Unsopported file type encountered",filename=uploaded_file.name,extension=ext)
                    continue
                
                docs= loader.load()
                documents.extend(docs)

            if not documents:
                raise DocumentPortalException("No supported files uploaded",sys)

            self.log.info("All documents loaded",total_docs=len(documents),session_id=self.session_id)    

            return self._create_retriever(documents)
        except Exception as e:
            self.log.error("Failed to ingest the document",error=str(e))
            raise DocumentPortalException("Failed to ingest the document",sys)    
    
    def _create_retriever(self,documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
            chunks = splitter.split_documents(documents)
            self.log.info("Text Splitter and Chunks created",chunks_created = len(chunks))


            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(documents=chunks,embedding=embeddings)
            
            #save fiass index
            vectorstore.save_local(str(self.session_faiss_path))
            retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":5})

            self.log.info("Vector store and retreiver created successfully",vectorstore_path=str(self.session_faiss_path))
            return retriever
        except Exception as e:
            self.log.error("Failed to create the retriver",error=str(e))
            raise DocumentPortalException("Failed to create the retriver",sys)