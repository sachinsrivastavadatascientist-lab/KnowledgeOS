import os
import sys
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain.memory import LLMMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from typing import List,Optional
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self,session_id:str,retriever=None):
        try:
            self.log =CustomLogger().get_logger(__name__)
            self.session_id =session_id
            self.llm = self._load_llm()
            self.contextualize_prompt:ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            if retriever is None:
                raise ValueError("Retriever cannot be None")
            self.retriever = retriever  
            self.chain =self._build_lcel_chain()

            self.log.info("initate the ConversatinalRAG class",session_id = self.session_id)  
        except Exception as e:
            self.log.error("Failed to initate the ConversatinalRAG class",error=str(e))
            raise DocumentPortalException("Inialization error in ConversatinalRAG",sys)
    
    def load_retriever_from_faiss(self,index_path:str):
        """
        Load the retriever from the FAISS vector store
        """
        try:
            embeddings =ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index not found at : {index_path}")

            vectorstore = FAISS.load_local(
                              index_path,
                              embeddings,
                              allow_dangerous_deserialization=True
                              )   
            self.retriever = vectorstore.as_retriever(search_type = "similarity",search_kwargs={"k":5})
            self.log.info("FAISS vector store loaded Successfully",session_id = self.session_id,index_path=index_path)
            return self.retriever
        except Exception as e:
            self.log.error("Failed to load FAISS vector store",error=str(e))
            raise DocumentPortalException("FAISS vector store loading error",sys)

    def invoke(self,query:str):
        try:
            config = {
                "configurable":{
                    "session_id":self.session_id
                }
            }

            return self.chain.invoke(
            {
                "input":query
            },
            config
        )

        except Exception as e:
            self.log.error("Failed to invoke chain",error=str(e))
            raise DocumentPortalException("Invoke error",sys)    

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.log.info("LLM loaded successfully",llm_type="Anthropic")
            return llm
        except Exception as e:
            self.log.error("Failed to load LLM",error=str(e))
            raise DocumentPortalException("LLM loading error",sys)  

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_lcel_chain(self):
        try:
            self.history_aware_chain = (
                {
                    "input":itemgetter("input"),
                    "chat_history":itemgetter("chat_history")
                }
                |self.contextualize_prompt
                |self.llm
                |StrOutputParser()
            )

            ######## Adding RAG chain
            self.rag_chain = (
             {
                "context":(
                        self.history_aware_chain
                        |self.retriever
                        |self._format_docs
                    ),
                "input":itemgetter("input"),
                "chat_history":itemgetter("chat_history")
             }
             |self.qa_prompt
             |self.llm
             |StrOutputParser()
             )

            ####### Add chat Memory
            self.chain = RunnableWithMessageHistory(
            self.rag_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            #output_messages_key="answer" - it is used when response was dictionary but we have added stroutput parser in chain so converts it in string not dict
             )  
            self.log.info("ConversatinalRAG chain created successfully",session_id=self.session_id)

            return self.chain

        except Exception as e:
            self.log.error("Failed to build LCEL chain",error=str(e))
            raise DocumentPortalException("LCEL chain building error",sys)  

    def _get_session_history(self,session_id: str):  # protected method create when we call from another method and we dont want to call it externally
        try:
            if not hasattr(self, "store"):
                self.store = {}

            if session_id not in self.store:
                self.store[session_id] = ChatMessageHistory()

            return self.store[session_id]
        except Exception as e:
            self.log.error("Failed to access session history in retrieval module",error=str(e))
            raise DocumentPortalException("Failed to access session history in retrieval module",sys)              