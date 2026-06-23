import os
import sys
#from langchain_core.chat_history import BaseChatMessageHistory
#from langchain.memory import LLMMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self,session_id:str,retriever):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever
            #load LLM
            self.llm = self._load_llm()

            # load prompts
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            
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
                        |(lambda docs:"\n\n".join(doc.page_content for doc in docs))
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

        except Exception as e:
            self.log.error("Error in intializing retrieval module",error=str(e))
            raise DocumentPortalException("Error in intializing retrieval module",sys)


    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            self.log.info("LLM loaded successfully",llm_type="Anthropic")
            return llm
        except Exception as e:
            self.log.error("Error in loading llm in retrieval module",error=str(e))
            raise DocumentPortalException("Error in loading llm in retrieval module",sys) 


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


    def load_retriever_from_faiss(self,index_path:str):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index not found at {index_path}")
                
            vectorstore =FAISS.load_local(index_path,embeddings,allow_dangerous_deserialization=True)
            self.log.info("Retriver loaded successfully")
            return vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":5})
        except Exception as e:
            self.log.error("Failed to load the retriver from fiass in retrieval module",error=str(e))
            raise DocumentPortalException("Failed to load the retriver from fiass in retrieval module",sys)    


    def invoke(self,user_input: str)->str:
        try:
            config = {"configurable":{"session_id":self.session_id}}
            answer =  self.chain.invoke(
                {
                    "input":user_input
                },
                config
            )
            # answer = response.get("answer","No answer")
            # if not answer:
            #     self.log.warning("No answer from LLM for query",session_id=self.session_id)
            # self.log.info("Query invoked successfully",query=user_input)
            return answer
        except Exception as e:
            self.log.error("Failed to invoke query in  retrieval module",error=str(e))
            raise DocumentPortalException("Failed to invoke query in retrieval module",sys)           


