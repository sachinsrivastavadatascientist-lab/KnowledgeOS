import os
import sys
from dotenv import load_dotenv
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader

class DocumentCompareLLM:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            load_dotenv()
            self.log = CustomLogger().get_logger(__name__)
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            self.prompt = PROMPT_REGISTRY['document_comparison']
            self.structured_llm = self.llm.with_structured_output(SummaryResponse)
            self.chain =self.prompt | self.structured_llm
            self.log.info("DocumentIngestion initalized sucessfully")
        except Exception as e:
            self.log.error(f"Error initalizing DocumentCompare: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)

    def compare_documents(self,combined_docs:str):  
        try:
           self.log.info("Compare documents initated",input=combined_docs)
           response = self.chain.invoke(
            {
               "combined_docs":combined_docs
            }
           )
           self.log.info("DocumentCompare completed successfully",response=response)
           return self._format_response(response)
        except Exception as e:
            self.log.error(f"Error initalizing DocumentCompare: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)      


    def _format_response(self,response: SummaryResponse)->pd.DataFrame:
        try: 
            df = pd.DataFrame(
                [item.model_dump() for item in response.changes]
            )
            self.log.info("Response formatted successfully",df=df)
            return df
        except Exception as e:
            self.log.error(f"Error initalizing DocumentCompare: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentCompare",sys)      
