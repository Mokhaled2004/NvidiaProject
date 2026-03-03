import os
import re
import uuid
from langchain_ollama import OllamaEmbeddings 
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Define project-wide paths for the database and data source
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CORE_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
VECTOR_DB_DIR = os.path.join(BACKEND_DIR, "vector_db")
DATA_FOLDER = os.path.join(APP_DIR, "data")

# Connect to the local Ollama embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5",
    base_url="http://192.168.1.21:11434"
)

def is_noise(text):
    # Detect and skip "garbage" text like long strings of dots or empty lines
    if not text.strip(): return True
    dot_count = text.count('.')
    if (dot_count / len(text)) > 0.15: return True
    if len(text) < 100 and re.search(r'\.{3,}', text): return True
    return False

def process_document(file_path: str): 
    # Select appropriate loader based on file extension
    loader = PyMuPDFLoader(file_path) if file_path.endswith('pdf') else Docx2txtLoader(file_path)
    documents = loader.load()
    filename = os.path.basename(file_path)

    # Break large documents into smaller, overlapping chunks for better search
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    initial_chunks = text_splitter.split_documents(documents)
    
    # Filter out noise and attach metadata (source, page, unique ID)
    final_chunks = []
    for c in initial_chunks:
        if not is_noise(c.page_content):
            c.metadata.update({
                "source": filename,
                "page": c.metadata.get("page", 0) + 1,
                "doc_id": str(uuid.uuid4())
            })
            final_chunks.append(c)
    
    # Initialize connection to the Chroma vector database
    vector_db = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
    )
    
    # Prevent duplicate indexing of the same file
    existing_docs = vector_db.get(where={"source": filename})
    if existing_docs and len(existing_docs['ids']) > 0:
        return f"Skipping: '{filename}' is already indexed."

    # Convert text to vectors and save to disk
    vector_db.add_documents(documents=final_chunks)
    return f"SUCCESS: {len(final_chunks)} chunks stored from {filename}"

if __name__ == "__main__":
    # Batch process all compatible files in the data folder
    os.makedirs(DATA_FOLDER, exist_ok=True)
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith((".pdf", ".docx"))]
    if files:
        for file in files:
            print(process_document(os.path.join(DATA_FOLDER, file)))
    else:
        print(f"No files found in: {DATA_FOLDER}")