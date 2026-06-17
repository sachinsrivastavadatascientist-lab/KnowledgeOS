from langchain_core.prompts.chat import ChatPromptTemplate

# Prepare prompt template
prompt = ChatPromptTemplate.from_template("""
You are a highly capable assistant trained to analyze and summarize documents.

Analyze this document and extract metadata.

Document:
{document_text}
""")