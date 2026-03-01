import os
import shutil
import re
from langchain_ollama import OllamaEmbeddings 
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# --- STANDARDIZED PATH SETUP ---
# Script location: backend/app/core/ingestion.py
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CORE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)

# Force DB to live in backend/vector_db
VECTOR_DB_DIR = os.path.join(BACKEND_DIR, "vector_db")
DATA_FOLDER = os.path.join(APP_DIR, "data")

print(f"📍 Checking Data Folder: {DATA_FOLDER}")
print(f"📍 Target DB Folder: {VECTOR_DB_DIR}")

# --- EMBEDDINGS ---
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5",
    base_url="http://192.168.1.21:11434"
)

def is_noise(text):
    """Filters out Table of Contents noise based on dot density."""
    if not text.strip(): return True
    dot_count = text.count('.')
    if (dot_count / len(text)) > 0.15: return True
    if len(text) < 100 and re.search(r'\.{3,}', text): return True
    return False

def process_document(file_path: str): 
    loader = PyMuPDFLoader(file_path) if file_path.endswith('pdf') else Docx2txtLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    initial_chunks = text_splitter.split_documents(documents)
    final_chunks = [c for c in initial_chunks if not is_noise(c.page_content)]
    
    print(f"📉 Filtered: {len(initial_chunks) - len(final_chunks)} noise chunks.")

    # FIX: Instead of shutil.rmtree (which fails if the server is running),
    # we just initialize Chroma with the new documents. 
    # This will append/update the existing DB.
    vector_db = Chroma.from_documents(
        documents=final_chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    return f"✅ SUCCESS: {len(final_chunks)} chunks stored in {VECTOR_DB_DIR}"

if __name__ == "__main__":
    if os.path.exists(DATA_FOLDER):
        files = [f for f in os.listdir(DATA_FOLDER) if f.endswith((".pdf", ".docx"))]
        if files:
            file_path = os.path.join(DATA_FOLDER, files[0])
            print(f"🚀 Found Handbook: {file_path}")
            print(process_document(file_path))
        else:
            print(f"❌ No PDF found in: {DATA_FOLDER}")
    else:
        print(f"❌ Folder not found: {DATA_FOLDER}")