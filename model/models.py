from pydantic import BaseModel, Field,RootModel
from typing import Optional, List, Dict, Any
from typing import List, Union
from enum import Enum



class Metadata(BaseModel):
    summary:List[str] = Field(default_factory=list,description="Summary of the document")
    Title:str = Field(description="Key points of the content")
    actionable_insights:str = Field(description="Actionable insights from the content")
    Author:str = Field(description="Author of the document")
    Publication:str = Field(description="Publication of the document")
    Date:str = Field(description="Date of the document")
    LastModified:str = Field(description="Last modified date of the document")
    Language:str = Field(description="Language of the document")
    PageCount:Union[int,str]=Field(description="Page count of the document")
    DocumentCategory:str = Field(description="Category of the document")
    SentimentTone:str

class ChangeFormat(BaseModel):
    page:str
    changes: str

class SummaryResponse(BaseModel):
    changes: List[ChangeFormat] 

class PromptType(str,Enum):
    DOCUMENT_ANALYSIS = "document_analysis"
    DOCUMENT_COMPARISON = "document_comparison"
    CONTEXTUALIZE_QUESTION = "contextualize_question"
    CONTEXT_QA = "context_qa"
    
        


    
    

    