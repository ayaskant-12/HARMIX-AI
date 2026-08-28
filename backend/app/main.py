from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from .parser.har_parser import HARParser
from .services.engines import (
    AuthDetector,
    RuleEngine,
    CorrelationEngine
)
from .ai.ollama_client import OllamaClient
from .generator.jmx_builder import JMXGenerator
from .reports.pdf_generator import PDFGenerator

import os
import uuid


# ==========================================
# Pydantic Models
# ==========================================

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    file_id: str
    message: str
    history: List[ChatMessage] = []
    context_data: Optional[Dict[str, Any]] = None


app = FastAPI(title="HARMIX AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "../uploads"
GENERATED_DIR = "../generated"
REPORTS_DIR = "../reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


@app.post("/api/upload-har")
async def upload_har(file: UploadFile = File(...)):

    if not file.filename.endswith(".har"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. HAR required."}
        )

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.har")

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # -------------------------------------
    # Parse HAR
    # -------------------------------------
    parser = HARParser(file_path)
    apis = parser.extract_apis()

    # -------------------------------------
    # Detect Correlations
    # -------------------------------------
    apis = CorrelationEngine.detect(apis)

    # -------------------------------------
    # Authentication Detection
    # -------------------------------------
    for api in apis:
        api["auth_detected"] = AuthDetector.detect(api["headers"])

    # -------------------------------------
    # Rule Engine
    # -------------------------------------
    rules_warnings = RuleEngine.analyze(apis)

    # -------------------------------------
    # Generate JMX
    # -------------------------------------
    jmx_path = os.path.join(GENERATED_DIR, f"{file_id}.jmx")
    JMXGenerator.generate(apis, jmx_path)

    return {
        "status": "success",
        "file_id": file_id,
        "total_requests": len(apis),
        "apis": apis,
        "warnings": rules_warnings,
    }


@app.post("/api/analyze")
async def analyze_ai(payload: dict):

    ai_client = OllamaClient()

    analysis = ai_client.analyze_har(
        payload.get("apis", [])
    )

    return {
        "analysis": analysis
    }


# ==========================================
# AI Chat Endpoint
# ==========================================

@app.post("/api/chat")
async def ai_chat(request: ChatRequest):
    """
    Interactive AI chat about the uploaded HAR.

    Frontend sends:
    - file_id
    - current message
    - previous chat history
    - HAR summary (apis, warnings, etc.)

    Backend remains stateless.
    """

    try:
        ai_client = OllamaClient()

        reply = ai_client.chat(
            user_message=request.message,
            history=[
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in request.history
            ],
            context_data=request.context_data or {}
        )

        return {
            "status": "success",
            "reply": reply
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e)
            }
        )



@app.post("/api/generate-report")
async def generate_report(payload: dict):
    """
    Generates an Executive PDF Report.
    Expected Payload:
    {
        "file_id": "...",
        "apis": [...],
        "warnings": [...],
        "ai_summary": "..."
    }
    """

    file_id = payload.get("file_id")

    if not file_id:
        return JSONResponse(
            status_code=400,
            content={"error": "file_id is required"}
        )

    apis = payload.get("apis", [])
    warnings = payload.get("warnings", [])
    ai_summary = payload.get("ai_summary", "")

    report_path = os.path.join(
        REPORTS_DIR,
        f"{file_id}_report.pdf"
    )

    PDFGenerator.generate_report(
        apis=apis,
        warnings=warnings,
        ai_summary=ai_summary,
        output_path=report_path
    )

    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename="Harmix_Executive_Report.pdf"
    )


@app.get("/api/download-jmx/{file_id}")
async def download_jmx(file_id: str):

    path = os.path.join(
        GENERATED_DIR,
        f"{file_id}.jmx"
    )

    if os.path.exists(path):
        return FileResponse(
            path,
            filename="harmix_testplan.jmx"
        )

    return JSONResponse(
        status_code=404,
        content={"error": "File not found"}
    )


@app.get("/api/download-report/{file_id}")
async def download_report(file_id: str):

    report_path = os.path.join(
        REPORTS_DIR,
        f"{file_id}_report.pdf"
    )

    if os.path.exists(report_path):
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename="Harmix_Executive_Report.pdf"
        )

    return JSONResponse(
        status_code=404,
        content={"error": "Report not found"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )