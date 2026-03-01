import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

# --- DYNAMIC PATH SETUP ---
# Standardized to point to /backend/vector_db
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_DIR = os.path.join(CURRENT_DIR, "vector_db")

# 1. Setup Embeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5",
    base_url="http://192.168.1.21:11434"
)

# 2. Load DB
if not os.path.exists(VECTOR_DB_DIR):
    print(f"❌ ERROR: No database at {VECTOR_DB_DIR}")
else:
    vector_db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)

    # 3. Quick Test Query
    query = "What are the hours of work?"
    docs = vector_db.similarity_search(query, k=3)

    print(f"--- Found {len(docs)} chunks in {VECTOR_DB_DIR} ---")
    for i, doc in enumerate(docs):
        # Clean up text for summary display
        preview = doc.page_content.replace('\n', ' ')[:200]
        print(f"Chunk {i+1}: {preview}...")