"""
🇰🇪 ENHANCED ICC EVIDENCE ANALYSIS API
Integrated with specialized AI agents and orchestration engine

FEATURES:
🔹 Multi-agent evidence analysis pipeline
🔹 ICC case document generation
🔹 Real-time AI processing with Groq
🔹 Comprehensive metadata extraction
🔹 Cross-evidence correlation analysis
🔹 Professional ICC submission packages
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import asyncio
import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging

# Import our agents and orchestrator
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from libs.icc_automation.icc_orchestrator import ICCEvidenceOrchestrator, analyze_evidence_batch
    from libs.icc_automation.transcription_agent import TranscriptionAgent
    from libs.icc_automation.visual_analysis_agent import VisualAnalysisAgent
    from libs.icc_automation.document_intelligence_agent import DocumentIntelligenceAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import custom agents: {e}")
    AGENTS_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🇰🇪 ICC Evidence Analysis API - Enhanced",
    description="AI-Powered Multi-Agent Evidence Analysis for ICC Submissions",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class IncidentContext(BaseModel):
    date: Optional[str] = "2025-06-17"
    time: Optional[str] = "14:00:00"
    location: Optional[str] = "CBD, Nairobi, Kenya"
    description: Optional[str] = "Person shot by GSU (General Service Unit)"
    victim_info: Optional[str] = ""
    perpetrator_info: Optional[str] = "GSU Officers"
    witness_info: Optional[str] = ""
    urgency_level: Optional[str] = "High"

class SubmitterInfo(BaseModel):
    name: Optional[str] = "Anonymous"
    email: Optional[str] = ""
    phone: Optional[str] = ""
    role: Optional[str] = "Witness"
    anonymous: Optional[bool] = True
    additional_info: Optional[str] = ""

class EvidenceAnalysisRequest(BaseModel):
    keywords: Optional[str] = None
    incident_context: Optional[IncidentContext] = None
    submitter_info: Optional[SubmitterInfo] = None

# Global orchestrator instance
orchestrator = None
if AGENTS_AVAILABLE:
    orchestrator = ICCEvidenceOrchestrator()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("🇰🇪 ICC Evidence Analysis API starting up...")
    
    if AGENTS_AVAILABLE:
        logger.info("✅ All AI agents loaded successfully")
    else:
        logger.warning("⚠️ Some agents not available - running in fallback mode")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🇰🇪 ICC Evidence Analysis API - Enhanced",
        "version": "3.0.0",
        "agents_available": AGENTS_AVAILABLE,
        "capabilities": [
            "Multi-agent evidence analysis",
            "ICC case document generation", 
            "Real-time AI processing",
            "Cross-evidence correlation",
            "Professional submission packages"
        ],
        "endpoints": [
            "/health - Health check",
            "/analyze_evidence - Single file analysis",
            "/analyze_batch - Batch evidence analysis", 
            "/generate_icc_document - Generate ICC case document",
            "/get_case_summary - Get case summary",
            "/agent_analysis/{agent_type} - Individual agent analysis"
        ]
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with agent status"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_available": AGENTS_AVAILABLE,
        "api_keys_configured": {
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY")),
            "roboflow": bool(os.getenv("ROBOFLOW_API_KEY"))
        },
        "capabilities": {
            "transcription": AGENTS_AVAILABLE,
            "visual_analysis": AGENTS_AVAILABLE,
            "document_intelligence": AGENTS_AVAILABLE,
            "icc_orchestration": AGENTS_AVAILABLE
        }
    }
    
    return status

@app.post("/analyze_evidence")
async def analyze_single_evidence(
    file: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    incident_date: Optional[str] = Form("2025-06-17"),
    incident_time: Optional[str] = Form("14:00:00"),
    incident_location: Optional[str] = Form("CBD, Nairobi, Kenya"),
    incident_description: Optional[str] = Form("Person shot by GSU (General Service Unit)")
):
    """
    Analyze single evidence file with comprehensive AI analysis
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents not available")
    
    try:
        # Read file content
        content = await file.read()
        
        # Prepare file data
        file_data = {
            'content': content,
            'filename': file.filename,
            'type': file.content_type,
            'size': len(content)
        }
        
        # Prepare incident context
        incident_context = {
            'date': incident_date,
            'time': incident_time,
            'location': incident_location,
            'description': incident_description
        }
        
        # Analyze with orchestrator
        result = await orchestrator.process_evidence_pipeline(
            [file_data], 
            keywords, 
            incident_context
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "analysis": result,
            "processing_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze_batch")
async def analyze_evidence_batch(
    files: List[UploadFile] = File(...),
    analysis_request: str = Form(...)
):
    """
    Analyze multiple evidence files and generate complete ICC case
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents not available")
    
    try:
        # Parse analysis request
        request_data = json.loads(analysis_request)
        keywords = request_data.get('keywords')
        incident_context = request_data.get('incident_context', {})
        submitter_info = request_data.get('submitter_info', {})
        
        # Prepare file data
        files_data = []
        for file in files:
            content = await file.read()
            files_data.append({
                'content': content,
                'filename': file.filename,
                'type': file.content_type,
                'size': len(content)
            })
        
        # Process with orchestrator
        result = await analyze_evidence_batch(
            files_data,
            keywords,
            incident_context,
            submitter_info
        )
        
        return {
            "success": True,
            "files_processed": len(files),
            "analysis": result,
            "processing_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/generate_icc_document")
async def generate_icc_document():
    """
    Generate professional ICC case document from analyzed evidence
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents not available")
    
    try:
        if not orchestrator.context_engine.case_metadata:
            raise HTTPException(status_code=400, detail="No case initialized. Process evidence first.")
        
        # Generate ICC document
        icc_document = orchestrator.generate_icc_case_document()
        file_number = orchestrator.get_file_number()
        
        return PlainTextResponse(
            content=icc_document,
            headers={
                "Content-Disposition": f"attachment; filename=ICC_Case_{file_number}_{datetime.now().strftime('%Y%m%d')}.txt"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating ICC document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@app.get("/get_case_summary")
async def get_case_summary():
    """
    Get comprehensive case summary with all evidence analysis
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents not available")
    
    try:
        if not orchestrator.context_engine.case_metadata:
            return {"message": "No case initialized", "evidence_count": 0}
        
        case_summary = orchestrator.get_case_summary()
        evidence_summary = orchestrator.get_evidence_summary()
        file_number = orchestrator.get_file_number()
        
        return {
            "file_number": file_number,
            "case_summary": case_summary,
            "evidence_summary": evidence_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting case summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get case summary: {str(e)}")

@app.post("/agent_analysis/transcription")
async def transcription_analysis(
    file: UploadFile = File(...),
    incident_context: str = Form("{}")
):
    """
    Specialized transcription analysis using Transcription Agent
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Transcription agent not available")
    
    try:
        # Check if file is audio/video
        file_type = file.content_type or ""
        if not (file_type.startswith('audio/') or file_type.startswith('video/')):
            raise HTTPException(status_code=400, detail="File must be audio or video format")
        
        content = await file.read()
        
        file_data = {
            'content': content,
            'filename': file.filename,
            'type': file.content_type,
            'size': len(content),
            'metadata': {}
        }
        
        # Parse context
        context = json.loads(incident_context) if incident_context != "{}" else {}
        shared_context = {'case_metadata': context}
        
        # Analyze with transcription agent
        agent = TranscriptionAgent()
        result = await agent.analyze_audio_evidence(file_data, shared_context)
        
        return {
            "success": True,
            "agent": "transcription_specialist",
            "filename": file.filename,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Transcription analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription analysis failed: {str(e)}")

@app.post("/agent_analysis/visual")
async def visual_analysis(
    file: UploadFile = File(...),
    incident_context: str = Form("{}")
):
    """
    Specialized visual analysis using Visual Analysis Agent
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visual analysis agent not available")
    
    try:
        # Check if file is image/video
        file_type = file.content_type or ""
        if not (file_type.startswith('image/') or file_type.startswith('video/')):
            raise HTTPException(status_code=400, detail="File must be image or video format")
        
        content = await file.read()
        
        file_data = {
            'content': content,
            'filename': file.filename,
            'type': file.content_type,
            'size': len(content),
            'metadata': {}
        }
        
        # Parse context
        context = json.loads(incident_context) if incident_context != "{}" else {}
        shared_context = {'case_metadata': context}
        
        # Analyze with visual agent
        agent = VisualAnalysisAgent()
        result = await agent.analyze_visual_evidence(file_data, shared_context)
        
        return {
            "success": True,
            "agent": "visual_analyst",
            "filename": file.filename,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Visual analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Visual analysis failed: {str(e)}")

@app.post("/agent_analysis/document")
async def document_analysis(
    file: UploadFile = File(...),
    incident_context: str = Form("{}")
):
    """
    Specialized document analysis using Document Intelligence Agent
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Document intelligence agent not available")
    
    try:
        # Check if file is document
        file_type = file.content_type or ""
        filename = file.filename or ""
        
        is_document = (
            file_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'] or
            any(filename.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt'])
        )
        
        if not is_document:
            raise HTTPException(status_code=400, detail="File must be a document (PDF, Word, or Text)")
        
        content = await file.read()
        
        file_data = {
            'content': content,
            'filename': file.filename,
            'type': file.content_type,
            'size': len(content),
            'metadata': {}
        }
        
        # Parse context
        context = json.loads(incident_context) if incident_context != "{}" else {}
        shared_context = {'case_metadata': context}
        
        # Analyze with document agent
        agent = DocumentIntelligenceAgent()
        result = await agent.analyze_document_evidence(file_data, shared_context)
        
        return {
            "success": True,
            "agent": "document_intelligence",
            "filename": file.filename,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@app.post("/initialize_case")
async def initialize_case(
    incident_context: IncidentContext,
    submitter_info: Optional[SubmitterInfo] = None
):
    """
    Initialize new ICC case with incident and submitter details
    """
    
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    try:
        # Convert Pydantic models to dictionaries
        incident_dict = incident_context.dict()
        submitter_dict = submitter_info.dict() if submitter_info else None
        
        # Initialize case
        file_number = orchestrator.initialize_case(incident_dict, submitter_dict)
        
        return {
            "success": True,
            "file_number": file_number,
            "message": f"ICC case initialized with file number: {file_number}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Case initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Case initialization failed: {str(e)}")

@app.get("/case_status")
async def get_case_status():
    """
    Get current case status and evidence count
    """
    
    if not AGENTS_AVAILABLE:
        return {"status": "agents_not_available"}
    
    try:
        if not orchestrator.context_engine.case_metadata:
            return {
                "status": "no_case_initialized",
                "evidence_count": 0,
                "message": "No case initialized. Use /initialize_case or process evidence to start."
            }
        
        case_metadata = orchestrator.context_engine.case_metadata
        evidence_count = len(orchestrator.context_engine.evidence_pool)
        case_strength = orchestrator.context_engine._assess_case_strength()
        
        return {
            "status": "active",
            "file_number": case_metadata.file_number,
            "incident_date": case_metadata.incident_date,
            "incident_location": case_metadata.incident_location,
            "evidence_count": evidence_count,
            "case_strength": case_strength.get('overall_score', 0),
            "last_updated": case_metadata.last_updated
        }
        
    except Exception as e:
        logger.error(f"Error getting case status: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/supported_formats")
async def get_supported_formats():
    """
    Get list of supported file formats for each analysis type
    """
    
    return {
        "visual_analysis": {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
            "videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"]
        },
        "transcription_analysis": {
            "audio": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
            "video": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"]
        },
        "document_analysis": {
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
            "data": [".json"]
        },
        "general_analysis": "All above formats supported through orchestrator"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting ICC Evidence Analysis API...")
    uvicorn.run(
        "enhanced_fast_api_backend:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
