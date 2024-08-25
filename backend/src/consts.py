# postgres config
DB_INIT_FILE = 'database.ini'
CONFIG = 'config'
POSTGRES_SECTION = 'postgresql'

# google generative ai config
EMBEDDING_MODEL = 'models/text-embedding-004'
LLM = 'models/gemini-1.5-flash-latest'

# RAG setting
PROMPT = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
