# import os
# import sys
# from pathlib import Path
# from src.document_analyzer.data_analysis import DocumentAnalyzer
# from src.document_analyzer.data_ingestion import DocumentHandler


# pdf_path =r"C:\\Users\\Admin\\Desktop\\LLMOPS\\KnowledgeOS\\data\\document_analysis\\NIPS-2017-attention-is-all-you-need-Paper.pdf"

# class DummyFile: 
#         def __init__(self,file_path):
#             self.name =Path(file_path).name
#             self._file_path =file_path

#         def getbuffer(self):
#             return open(self._file_path,"rb").read()


# def main():
#     try:
#         # -------- STEP 1: DATA INGESTION --------

#         print("Starting PDF ingestion...")

#         dummy_pdf = DummyFile(pdf_path)

#         handler = DocumentHandler(session_id="test_ingestion_analysis")

#         saved_path = handler.save_pdf(dummy_pdf)

#         print(f"PDF saved at: {saved_path}")


#         text_content = handler.read_pdf(saved_path)

#         print(f"Extracted text length: {len(text_content)} chars")


#         # -------- STEP 2: DATA ANALYSIS --------

#         print("Starting metadata analysis...")

#         analyzer = DocumentAnalyzer()   # Loads LLM + parser

#         analysis_result = analyzer.analyze_document(text_content) 

#         # -------- STEP 3: DISPLAY RESULTS --------

#         print("\n==== METADATA ANALYSIS RESULT ====")

#         print(analysis_result)

#         # agar fields alag-alag print karni hain
#         print("\nTitle:", analysis_result.Title)
#         print("Author:", analysis_result.Author)
#         print("Date:", analysis_result.Date)
#         print("Language:", analysis_result.Language)
#         print("Category:", analysis_result.DocumentCategory)

#     except Exception as e:
#          print(f"Test failed: {e}")    

# if __name__ == "__main__":
#     main()

############## Document compare modeule check #############/




# import io
# from pathlib import Path
# from src.document_compare.data_ingestion import DocumentIngestion
# from src.document_compare.document_compare import DocumentCompareLLM


# def load_fake_uploaded_file(file_path:Path):
#     return io.BytesIO(file_path.read_bytes())

# def test_compare_documents():
#     ref_path = Path("data\\document_compare\\NIPS-2017-attention-is-all-you-need-Paper.pdf")   
#     act_path = Path("data\\document_compare\\llama_reasearch.pdf") 

#     class FakeUpload:
#         def __init__(self,file_path:Path):
#             self.name = file_path.name
#             self._buffer = file_path.read_bytes()
#         def getbuffer(self):
#             return self._buffer

#     compareror =DocumentIngestion()  
#     ref_upload = FakeUpload(ref_path)   
#     act_upload = FakeUpload(act_path)

#     ref_file,act_file = compareror.save_uploaded_files(ref_upload,act_upload)
#     combined_text = compareror.combine_documents()
#     compareror.clean_old_sessions(keep_latest=3)

#     print("\n Combined Text preview (First 1000 characters):\n")
#     print(combined_text[:1])

#     llm_compare = DocumentCompareLLM()
#     comparison_df = llm_compare.compare_documents(combined_text)

#     print("\n===== Comparison Result =====")
#     print(comparison_df.head())


# if __name__ == "__main__":
#     test_compare_documents()    


############## SingleDocChat modeule check #############

# import sys
# from pathlib import Path
# from langchain_community.vectorstores import FAISS
# from src.singledocchat.data_ingestion import SingleDocIngestor
# from src.singledocchat.retrieval import ConversationalRAG
# from utils.model_loader import ModelLoader

# FAISS_INDEX_PATH = Path("faiss_index")


# def test_conversational_rag_on_pdf(pdf_path:str,question:str):
#     try:
#         model_loader = ModelLoader()

#         if FAISS_INDEX_PATH.exists():
#             print("Loading existing FIASS INDEX")
#             embeddings =model_loader.load_embeddings()
#             vectorstore = FAISS.load_local(folder_path=str(FAISS_INDEX_PATH),embeddings=embeddings,allow_dangerous_deserialization=True)
#             retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":5})
#         else:
#             # if vectorstore is not there upload document via data_ingestion
#             print("FAISS index not found. Ingesting PDF and creating index...")
#             with open(pdf_path,"rb") as f:
#                 uploaded_files = [f]
#                 ingestor = SingleDocIngestor()
#                 retriever = ingestor.ingest_files(uploaded_files)

#         print("Running Coversational RAG....")
#         session_id = "test_conversational_rag"
#         rag = ConversationalRAG(retriever = retriever,session_id=session_id)

#         response = rag.invoke(question)
#         print(f"\n\nQuestion: {question}\nResponse: {response}")


#     except Exception as e:
#         print(f"test failed : {str(e)}")
#         sys.exit(1)


# if __name__ == "__main__":
#     pdf_path = r"data\\single_document_chat\\NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     question = "What is its encoder_decoder explain with formulaes in paragraph and markdown format?"


#     # Run the test
#     test_conversational_rag_on_pdf(pdf_path,question)





############## MultiDocChat modeule check #############

import sys
from pathlib import Path
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.retrieval import ConversationalRAG

def test_document_ingestion_and_rag():
    try:
        test_files = [
            "data\\multi_doc_chat\\Elon.txt",
            "data\\multi_doc_chat\\llama_reasearch.pdf",
            "data//multi_doc_chat//NIPS-2017-attention-is-all-you-need-Paper.pdf",
            "data\\multi_doc_chat\\spiderman_rag_test_document.docx"
        ]

        uploaded_files = []
        for file_path in test_files:
          if Path(file_path).exists():
            uploaded_files.append(open(file_path,"rb"))
          else:
             print(f"File doesn't exists: {file_path}")    

        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)

        ingestor =DocumentIngestor()
        retriever =ingestor.ingest_files(uploaded_files)

        for f in uploaded_files:
           f.close()

        session_id = "test_multi_doc_chat"

        rag = ConversationalRAG(session_id=session_id,retriever=retriever)
        question = "How are Neuralink and The Boring Company different in their technological goals??"
        response = rag.invoke(question)

        print(f"\n\nQuestion : {question}\n\nResponse: {response}")





    except Exception as e:
        print(f"error :{e}")



if __name__=="__main__":
    test_document_ingestion_and_rag()




