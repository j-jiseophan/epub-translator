import asyncio
import os
import subprocess
import shutil
from uuid import uuid4
from typing import Dict

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .api.websocket import manager
from .core.epub_parser import EPUBParser
from .core.translator import TranslationOrchestrator, TranslationJob
from .core.ollama_client import OllamaClient
from .models.schemas import (
    TranslationRequest,
    FileUploadResponse,
    JobStatusResponse,
    TranslationStatus,
)

app = FastAPI(title="EPUB Translator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

jobs: Dict[str, TranslationJob] = {}
orchestrators: Dict[str, TranslationOrchestrator] = {}
tasks: Dict[str, asyncio.Task] = {}


@app.get("/api/ollama/status")
async def get_ollama_status():
    """Check if Ollama is installed and running."""
    ollama_installed = shutil.which("ollama") is not None

    if not ollama_installed:
        return {"installed": False, "running": False}

    try:
        client = OllamaClient()
        await client.list_models()
        await client.close()
        return {"installed": True, "running": True}
    except Exception:
        return {"installed": True, "running": False}


@app.post("/api/ollama/start")
async def start_ollama():
    """Start Ollama server in background."""
    if shutil.which("ollama") is None:
        raise HTTPException(status_code=400, detail="Ollama is not installed")

    try:
        subprocess.Popen(
            ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Ollama: {str(e)}")


@app.get("/api/models")
async def list_models():
    """List available Ollama models."""
    client = OllamaClient()
    try:
        models = await client.list_models()
        return {"models": models}
    finally:
        await client.close()


@app.get("/api/languages")
async def list_languages():
    """List supported languages."""
    languages = [
        {"code": "en", "name": "English"},
        {"code": "ko", "name": "Korean"},
        {"code": "ja", "name": "Japanese"},
        {"code": "zh", "name": "Chinese"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
    ]
    return {"languages": languages}


@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload EPUB file for translation."""
    if not file.filename or not file.filename.endswith(".epub"):
        raise HTTPException(status_code=400, detail="File must be an EPUB")

    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.epub")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    parser = EPUBParser(file_path)
    chapters = parser.get_chapters()

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename or "unknown.epub",
        file_size=len(content),
        chapter_count=len(chapters),
    )


@app.post("/api/translate")
async def start_translation(request: TranslationRequest):
    """Start a translation job."""
    file_path = os.path.join(UPLOAD_DIR, f"{request.file_id}.epub")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    job_id = str(uuid4())
    job = TranslationJob(
        job_id=job_id,
        file_id=request.file_id,
        source_lang=request.source_language,
        target_lang=request.target_language,
        model=request.model,
    )
    jobs[job_id] = job

    async def progress_callback(message: dict):
        await manager.broadcast_to_job(job_id, message)

    orchestrator = TranslationOrchestrator(
        job=job,
        upload_dir=UPLOAD_DIR,
        output_dir=OUTPUT_DIR,
        progress_callback=progress_callback,
    )
    orchestrators[job_id] = orchestrator

    task = asyncio.create_task(run_translation(job_id))
    tasks[job_id] = task

    return {"job_id": job_id}


async def run_translation(job_id: str):
    """Background task to run translation."""
    orchestrator = orchestrators.get(job_id)
    if not orchestrator:
        return

    try:
        await orchestrator.run()
    except asyncio.CancelledError:
        orchestrator.job.status = TranslationStatus.CANCELLED
        await orchestrator._notify_progress()
    except Exception:
        pass
    finally:
        if job_id in orchestrators:
            del orchestrators[job_id]
        if job_id in tasks:
            del tasks[job_id]


@app.get("/api/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        current_chapter=job.current_chapter,
        total_chapters=job.total_chapters,
        current_chunk=job.current_chunk,
        total_chunks=job.total_chunks,
        percentage=0.0,
        error_message=job.error_message,
        download_url=f"/api/download/{job_id}"
        if job.status == TranslationStatus.COMPLETED
        else None,
    )


@app.delete("/api/job/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a translation job."""
    orchestrator = orchestrators.get(job_id)
    task = tasks.get(job_id)

    if orchestrator:
        orchestrator.cancel()

    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return {"success": True}

    if orchestrator:
        return {"success": True}

    return {"success": False, "message": "Job not found or already completed"}


@app.get("/api/download/{job_id}")
async def download_translated(job_id: str):
    """Download translated EPUB."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != TranslationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Translation not completed")

    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        job.output_path,
        media_type="application/epub+zip",
        filename=f"translated_{job_id}.epub",
    )


@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await manager.connect(websocket, job_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
