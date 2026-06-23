import sys
import uuid
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from datetime import datetime

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader


class SingleDocIngestor:
    def __init__(self,data_dir: str = "data/single_document_chat",faiss_dir: str = "faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True,exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True,exist_ok=True)
            self.model_loader = ModelLoader()
            self.log.info(f"SingleDocIngestor class initated",temp_path=str(self.data_dir),faiss_path=str(self.faiss_dir))
        except Exception as e:
            self.log.error("Filed to initate the SingleDocIngestor class",error =str(e))
            raise DocumentPortalException("Inialization error in SingleDocIngestor",sys)
    
    def ingest_files(self,uploaded_files):
        try:
            documents =[]
            for uploaded_file in uploaded_files:
                unique_filename = unique_filename = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir/unique_filename
                with open(temp_path,"wb") as f:
                    # if hasattr(uploaded_file,"read"):
                    #     f.write(uploaded_file.read())
                    # else: 
                        f.write(uploaded_file.read())
                self.log.info("PDF saved for ingestion",filename=uploaded_file.name,size=temp_path.stat().st_size)  
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
                self.log.info("PDF FILE LOADED",count = len(documents))  
            return self._create_retriever(documents)
                
        except Exception as e:
            self.log.error("Filed to ingest the document",error = str(e))
            raise DocumentPortalException("Failed to ingest the document", sys)

    def _create_retriever(self,documents:list):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
            chunks = splitter.split_documents(documents)
            self.log.info("Text Splitter and Chunks created",chunks_created = len(chunks))


            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(documents=chunks,embedding=embeddings)
            
            #save fiass index
            vectorstore.save_local(str(self.faiss_dir))
            retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":5})

            self.log.info("Vector store and retreiver created successfully",vectorstore_path=str(self.faiss_dir))

            return retriever
        except Exception as e:
            self.log.error("Failed to create the retriver",error = str(e))
            raise DocumentPortalException("Failed to create the retriver", sys)       
