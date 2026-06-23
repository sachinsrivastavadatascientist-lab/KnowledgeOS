import os
import sys
from pathlib import Path
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from langchain_community.document_loaders import PyPDFLoader
from datetime import datetime
import uuid



class DocumentIngestion:
    def __init__(self,base_dir:str='data\\document_compare',session_id=None):
        try:
           self.log = CustomLogger().get_logger(__name__)
           self.base_dir = Path(base_dir)
           self.base_dir.mkdir(parents=True,exist_ok=True)
           self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

           self.session_path = self.base_dir / self.session_id
           self.session_path.mkdir(
                parents=True,
                exist_ok=True
            )
           self.log.info("DocumentCompare initalized",session_id=self.session_id,session_path=self.session_path)   
           
        except Exception as e:
            self.log.error(f"Error initalizing DocumentCompare: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)      

    

    def delete_existing_file(self):
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                self.log.info("All previous files deleted",path =str(file))    
        except Exception as e:
            self.log.error(f"Error deleting existing files: {e}")
            raise DocumentPortalException(f"Error deleting existing files",sys)      

    

    def save_uploaded_files(self,reference_file,actual_file):
        try:
            # self.delete_existing_file()
            # self.log.info("All previous files deleted")

            ref_path = self.session_path/reference_file.name   
            act_path = self.session_path/actual_file.name   

            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):
                raise ValueError("Both files must be of type PDF")    
            

            with open(ref_path,"wb") as f:
                f.write(reference_file.getbuffer())    

            with open(act_path,"wb") as f:
                f.write(actual_file.getbuffer())
  

            self.log.info("Files_saved",reference_path = str(ref_path),actual_path = str(act_path))
            
            return ref_path, act_path


        except Exception as e:
            self.log.error(f"Error saving document: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)      



    def read_pdf(self,pdf_path):
        try:
           loader = PyPDFLoader(str(pdf_path))

           documents = loader.load()

           all_text = []

           for page_num, doc in enumerate(documents, start=1):
                text = doc.page_content

                if text.strip():
                    all_text.append(
                        f"\n --- Page {page_num} --- \n{text}"
                    )

           self.log.info(
                "PDF read successfully",
                file=str(pdf_path),
                pages=len(documents)
            )

           return "\n".join(all_text)

        except Exception as e:
            self.log.error(f"Error reading pdf: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)     
 
    def combine_documents(self):
        try:
           content_dict = {}
           doc_parts =[]

           for filename in sorted(self.base_dir.iterdir()):
               if filename.is_file() and filename.suffix == ".pdf":
                   content_dict[filename.name] = self.read_pdf(filename)
            
           for filename, content in content_dict.items():
                doc_parts.append(
                    f'''
                        "file_name":{filename}\n
                        "content":{content}
                    '''
                )

           combined_text = "\n\n".join(doc_parts)
           self.log.info("Documents combined successfully",combined_text=combined_text)
           return combined_text
        except Exception as e:
            self.log.error(f"Error combining documents: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)  


    def clean_old_sessions(self, keep_latest: int = 3):
        """
        Optional method to delete older session folders, keeping only the latest N.
        """
        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
            )
            for folder in session_folders[keep_latest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info("Old session folder deleted", path=str(folder))

        except Exception as e:
            self.log.error("Error cleaning old sessions", error=str(e))
            raise DocumentPortalException("Error cleaning old sessions", sys)
        
