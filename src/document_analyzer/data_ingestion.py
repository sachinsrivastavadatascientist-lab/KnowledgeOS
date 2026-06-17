import os
import sys
import fitz
import uuid # for creating universal identification number
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from langchain_community.document_loaders import PyPDFLoader

class DocumentHandler:
    
    def __init__(self,data_dir:str=None,session_id=None):
        try:
            self.log =  CustomLogger().get_logger(__name__)
            self.data_dir =  data_dir or os.getenv("DATA_STORAGE_PATH",
                                                    os.path.join(os.getcwd(),"data","document_analysis"))
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # create the base session directory
            self.session_path = os.path.join(self.data_dir,self.session_id)
            print("\n\n\n\n\n\n\n",self.session_path)
            os.makedirs(self.session_path, exist_ok=True)
            

            self.log.info("PDFHandler initalized",session_id=self.session_id,session_path=self.session_path) 
        except Exception as e:
            self.log.error(f"Error initalizing PDFHandler: {e}")
            raise DocumentPortalException(f"Error in initalizing PDFHandler",sys)


    def save_pdf(self,uploaded_file):   
        try:
            filename = os.path.basename(uploaded_file.name)

            if not filename.lower().endswith(".pdf"):
                raise DocumentPortalException("File is not in PDF format",sys)

            save_path = os.path.join(self.session_path,filename)   
            
            with open(save_path,"wb") as f:
                f.write(uploaded_file.getbuffer())

            self.log.info("PDF save successfully",file=filename,session_id=self.session_id,save_path=save_path)   
            return save_path
        except Exception as e:  
            self.log.error(f"Error saving PDF: {e}")
            raise DocumentPortalException(f"Error in saving PDF",sys)   

    def read_pdf(self,pdf_path):
        try:
            loader = PyPDFLoader(pdf_path)

            documents = loader.load()

            text_chunks = []

            for page_num, doc in enumerate(documents, start=1):
                text_chunks.append(
                    f"\n--- Page {page_num} ---\n{doc.page_content}"
                )

            text = "\n".join(text_chunks)

            self.log.info(
                "PDF read successfully",
                pdf_path=pdf_path,
                session_id=self.session_id,
                pages=len(documents)
            )

            return text
        except Exception as e:
            self.log.error(f"Error reading PDF: {e}")
            raise DocumentPortalException("Error reading PDF", sys)

if __name__ =="__main__":
    from pathlib import Path
    from io import BytesIO

    
    pdf_path =r"C:\\Users\\Admin\\Desktop\\LLMOPS\\KnowledgeOS\\data\\document_analysis\\NIPS-2017-attention-is-all-you-need-Paper.pdf"

    class DummyFile:
        def __init__(self,file_path):
            self.name =Path(file_path).name
            self._file_path =file_path

        def getbuffer(self):
            return open(self._file_path,"rb").read()


    dummy_pdf = DummyFile(pdf_path)

    handler = DocumentHandler(session_id="test_session")
    
    try:
        saved_path = handler.save_pdf(dummy_pdf)
        print(saved_path)
        content=handler.read_pdf(saved_path)
        print(content[:500])
    except Exception as e:
        print(f"Error:{e}")

    