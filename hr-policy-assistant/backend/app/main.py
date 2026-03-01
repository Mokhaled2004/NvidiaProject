import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.retrieval import query_documents
from app.core.ingestion import process_document # Import your ingestion logic

app = FastAPI(title="HR Policy Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "app", "data")
os.makedirs(DATA_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    question: str

@app.post('/upload')
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(DATA_DIR, file.filename)
    
    try:
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Process and index
        status = process_document(file_path)
        print(f"DEBUG: {status}")
        
        return {"message": f"File '{file.filename}' indexed.", "details": status}
    except Exception as e:
        print(f"UPLOAD ERROR: {e}") # This will show in your terminal
        raise HTTPException(status_code=500, detail=str(e))
@app.post('/ask')
def ask_hr(request: ChatRequest):
    try:
        answer = query_documents(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)