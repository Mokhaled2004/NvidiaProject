import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.retrieval import query_documents

# Setup pathing for local module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="HR Policy Assistant")

# Enable cross-origin requests for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data directory for PDF storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    question: str

@app.post('/upload')
async def upload_pdf(file: UploadFile = File(...)):
    # Validate and save uploaded PDF to the data directory
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(DATA_DIR, file.filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Trigger document processing and indexing
        from app.core.ingestion import process_document 
        status = process_document(file_path)
        return {"message": f"File '{file.filename}' indexed.", "details": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/ask')
def ask_hr(request: ChatRequest):
    # Query the RAG system with context-aware history
    try:
        answer = query_documents(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/reset')
def reset_chat():
    # Wipe the existing conversation history from memory
    try:
        from app.core import retrieval
        retrieval.chat_history = []
        return {"message": "Chat history cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)