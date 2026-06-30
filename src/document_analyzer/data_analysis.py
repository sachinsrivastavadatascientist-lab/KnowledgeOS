import os
import sys
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import*
from prompt.prompt_library import PROMPT_REGISTRY


class DocumentAnalyzer:
    '''
    '''
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            # prepare parser
            self.structured_llm = self.llm.with_structured_output(Metadata)
            self.prompt=PROMPT_REGISTRY['document_analysis']
            self.log.info("DocumentAnalyzer initalized sucessfully")
        except Exception as e:
            self.log.error(f"Error initalizing DocumentAnalyzer: {e}")
            raise DocumentPortalException(f"Error in initalizing DocumentAnalyzer",sys)

    def analyze_document(self,document_text):
        try:
            chain = self.prompt | self.structured_llm
            self.log.info("Metadata analysis chain intialized")
            
            response = chain.invoke({
            "document_text": document_text
        })

            return response
            self.log.info("Document analyzed sucessfully")
        except Exception as e:
            self.log.error(f"Error analyzing document: {e}")
            raise DocumentPortalException(f"Error in analyzing document",sys)