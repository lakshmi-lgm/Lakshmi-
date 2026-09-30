import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.gemini_service import GeminiService
from app.rag_service import RAGService

app = FastAPI(title="EduGenie - Gemini Powered Learning Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
gemini_svc = GeminiService()
rag_svc = RAGService()

class ChatRequest(BaseModel):
    question: str

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        chunk_count = rag_svc.process_and_index_pdf(file_path)
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_processed": chunk_count,
            "message": "PDF uploaded and vector index built successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.post("/api/chat")
async def chat_with_tutor(request: ChatRequest):
    try:
        context = rag_svc.retrieve_context(request.question)
        response = gemini_svc.ask_tutor(request.question, context)
        return {
            "question": request.question,
            "response": response,
            "context_used": bool(context)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_material(tool_type: str = Form(...)):
    if not rag_svc.chunks:
        raise HTTPException(status_code=400, detail="Please upload a PDF document first.")
    
    try:
        full_context = "\n".join(rag_svc.chunks[:10])
        result = gemini_svc.generate_study_material(tool_type, full_context)
        return {"tool": tool_type, "content": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Frontend static assets
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)