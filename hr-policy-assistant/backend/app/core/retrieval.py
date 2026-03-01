import os
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings # Updated to new package
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# --- DYNAMIC PATH SETUP ---
# This script is in: backend/app/core/retrieval.py
# Move up 2 levels to get to the 'backend' folder
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(CORE_DIR))
VECTOR_DB_DIR = os.path.join(BACKEND_DIR, "vector_db")

OLLAMA_BASE_URL = "http://192.168.1.21:11434"

# 1. Setup Embeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5",
    base_url=OLLAMA_BASE_URL
)

# 2. Load Vector DB (Targets backend/vector_db)
if not os.path.exists(VECTOR_DB_DIR):
    print(f"⚠️ Warning: DB folder NOT found at {VECTOR_DB_DIR}")

vector_db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)

# 3. MMR Retriever
retriever = vector_db.as_retriever(
    search_type="mmr", 
    search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.5}
)

# 4. Prompt Template
template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a strict HR Assistant. Use ONLY the provided Context to answer.
- If the answer is not in the context, say: "I'm sorry, that detail is not in the handbook."
- Do not use outside knowledge.
- Reference Section numbers (like Section VII) if they appear in the text.
<|eot_id|><|start_header_id|>user<|end_header_id|>
Context:
{context}

Question: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

prompt = ChatPromptTemplate.from_template(template)

# 5. Remote LLM
llm = ChatOllama(
    model="llama3.2:latest", 
    base_url=OLLAMA_BASE_URL,
    temperature=0
)

# 6. LCEL Chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def query_documents(user_question: str):
    try:
        return rag_chain.invoke(user_question)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print(f"🔍 Successfully pointing to: {VECTOR_DB_DIR}")
    print(query_documents("What are HOURS OF WORK?"))