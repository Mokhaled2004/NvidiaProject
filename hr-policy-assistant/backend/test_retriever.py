import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

# --- STANDARDIZED PATH SETUP ---
# Script location: backend/test_retriever.py
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(BACKEND_DIR, "vector_db")

OLLAMA_BASE_URL = "http://192.168.1.21:11434"

embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5",
    base_url=OLLAMA_BASE_URL
)

print(f"🔍 Looking for database in: {VECTOR_DB_DIR}")

if not os.path.exists(VECTOR_DB_DIR):
    print(f"❌ ERROR: Folder does not exist at {VECTOR_DB_DIR}")
    print("Hint: Run 'python -m app.core.ingestion' from the backend folder first.")
else:
    db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    
    # Use "HOURS" as a broad keyword to verify section VII
    query = "HOURS OF WORK"
    print(f"--- Debugging Retrieval for: {query} ---")
    
    docs = db.similarity_search(query, k=5)

    if not docs:
        print("❓ Database found, but it is EMPTY. You need to run ingestion.py again.")
    else:
        for i, doc in enumerate(docs):
            print(f"\n📄 CHUNK {i+1}")
            print("-" * 30)
            print(doc.page_content)
            print("-" * 30)