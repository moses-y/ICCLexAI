"""
🇰🇪 ICC CONTEXT ENGINE API
FastAPI backend that integrates the ICC Context Engine with frontend validation workflow

FEATURES:
🔹 Session management and state persistence
🔹 Evidence upload and multi-agent analysis
🔹 Human-in-the-loop validation endpoints
🔹 Case summary editing and review
🔹 ICC document generation and submission
🔹 Real-time validation progress tracking
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import sys

# Add paths for our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from libs.icc_automation.icc_context_engine import ICCContextEngine
    from libs.icc_automation.icc_orchestrator import ICCEvidenceOrchestrator
    CONTEXT_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import context engine: {e}")
    CONTEXT_ENGINE_AVAILABLE = False
    
    # Create mock classes for development
    class ICCContextEngine:
        def __init__(self, session_id=None):
            import uuid
            self.session_id = session_id or str(uuid.uuid4())
            self.evidence_pool = []
            self.case_metadata = None
            self.validation_state = {
                'human_reviewed': False,
                'summary_edited': False,
                'evidence_validated': False,
                'legal_analysis_confirmed': False,
                'witness_consent': False,
                'chain_of_custody': False,
                'validation_progress': 0.0
            }
            self.case_summary = {}
        
        def initialize_case(self, details):
            return "MOCK-CASE-123"
        
        def get_context_state(self):
            return {"mock": "state"}
        
        def add_evidence(self, file_data, analysis):
            return f"EVD-{len(self.evidence_pool)}"
        
        def update_validation_state(self, field, value, reviewer_id=None):
            return True
        
        def update_case_summary(self, data, editor_id=None):
            return True
        
        def validate_evidence(self, evidence_id, result, validator_id=None):
            return True
        
        def generate_icc_document(self):
            return {"mock": "document"}
    
    class ICCEvidenceOrchestrator:
        async def analyze_evidence_item(self, path, data):
            return {"mock": "analysis"}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🇰🇪 ICC Context Engine API",
    description="Context management and validation API for ICC evidence analysis",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (in production, use Redis or database)
active_sessions: Dict[str, ICCContextEngine] = {}
orchestrators: Dict[str, ICCEvidenceOrchestrator] = {}

# Pydantic models
class IncidentDetails(BaseModel):
    date: str
    time: str
    location: str
    description: str
    victim_info: str = ""
    perpetrator_info: str = ""
    witness_info: str = ""
    urgency_level: str = "High"
    submitter_info: Dict[str, Any] = {}

class ValidationUpdate(BaseModel):
    field: str
    value: Any
    reviewer_id: Optional[str] = None

class SummaryUpdate(BaseModel):
    ai_generated_summary: Optional[str] = None
    human_edited_summary: Optional[str] = None
    key_findings: Optional[List[str]] = None
    evidence_summary: Optional[List[str]] = None
    legal_assessment: Optional[str] = None
    recommendations: Optional[List[str]] = None
    editor_id: Optional[str] = None

class EvidenceValidation(BaseModel):
    evidence_id: str
    status: str  # "validated", "rejected", "needs_review"
    notes: Optional[str] = None
    validator_id: Optional[str] = None

# Session management endpoints
@app.post("/api/session/create")
async def create_session(incident_details: IncidentDetails):
    """Create new ICC context session"""
    try:
        context_engine = ICCContextEngine()
        file_number = context_engine.initialize_case(incident_details.dict())
        
        # Store session
        active_sessions[context_engine.session_id] = context_engine
        orchestrators[context_engine.session_id] = ICCEvidenceOrchestrator()
        
        logger.info(f"Created session {context_engine.session_id[:8]} for case {file_number}")
        
        return {
            "session_id": context_engine.session_id,
            "file_number": file_number,
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/state")
async def get_session_state(session_id: str):
    """Get complete session state for frontend"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    return context_engine.get_context_state()

@app.get("/api/session/{session_id}/validation")
async def get_validation_state(session_id: str):
    """Get validation state and progress"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    return {
        "validation_state": context_engine.validation_state,
        "case_summary": context_engine.case_summary,
        "validation_progress": context_engine.validation_state.get('validation_progress', 0.0)
    }

# Evidence management endpoints
@app.post("/api/session/{session_id}/evidence/upload")
async def upload_evidence(
    session_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload and analyze evidence files"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    evidence_ids = []
    
    try:
        for file in files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Prepare file data
            file_data = {
                "filename": file.filename,
                "type": file.content_type,
                "size": len(content),
                "content": content.decode('utf-8', errors='ignore'),
                "metadata": {
                    "upload_timestamp": datetime.now().isoformat(),
                    "temp_path": temp_file_path
                }
            }
            
            # Schedule background analysis
            background_tasks.add_task(
                analyze_evidence_background,
                session_id,
                file_data,
                temp_file_path
            )
            
            # Add to context with placeholder analysis
            placeholder_analysis = {
                "status": "processing",
                "confidence": 0.0,
                "relevance_score": 0.5,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            evidence_id = context_engine.add_evidence(file_data, placeholder_analysis)
            evidence_ids.append(evidence_id)
        
        logger.info(f"Uploaded {len(files)} files to session {session_id[:8]}")
        
        return {
            "evidence_ids": evidence_ids,
            "status": "uploaded",
            "processing": True,
            "message": f"Uploaded {len(files)} files. Analysis in progress."
        }
        
    except Exception as e:
        logger.error(f"Evidence upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_evidence_background(session_id: str, file_data: Dict[str, Any], temp_file_path: str):
    """Background task for evidence analysis"""
    try:
        orchestrator = orchestrators[session_id]
        
        # Run orchestrated analysis
        await orchestrator.analyze_evidence_item(temp_file_path, file_data)
        
        logger.info(f"Completed analysis for {file_data['filename']} in session {session_id[:8]}")
        
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except Exception:
            pass
            
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")

@app.get("/api/session/{session_id}/evidence")
async def get_evidence_pool(session_id: str):
    """Get all evidence items in the session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    return {"evidence_pool": context_engine.evidence_pool}

# Validation endpoints
@app.post("/api/session/{session_id}/validation/update")
async def update_validation_state(session_id: str, validation: ValidationUpdate):
    """Update validation state"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    success = context_engine.update_validation_state(
        validation.field,
        validation.value,
        validation.reviewer_id
    )
    
    if success:
        return {
            "status": "updated",
            "field": validation.field,
            "value": validation.value,
            "validation_progress": context_engine.validation_state.get('validation_progress', 0.0)
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid validation field")

@app.post("/api/session/{session_id}/summary/update")
async def update_case_summary(session_id: str, summary: SummaryUpdate):
    """Update case summary with human edits"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    summary_data = {k: v for k, v in summary.dict().items() if v is not None and k != 'editor_id'}
    
    success = context_engine.update_case_summary(summary_data, summary.editor_id)
    
    if success:
        return {
            "status": "updated",
            "case_summary": context_engine.case_summary,
            "validation_progress": context_engine.validation_state.get('validation_progress', 0.0)
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update summary")

@app.post("/api/session/{session_id}/evidence/validate")
async def validate_evidence(session_id: str, validation: EvidenceValidation):
    """Validate specific evidence item"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    validation_result = {
        "status": validation.status,
        "notes": validation.notes,
        "timestamp": datetime.now().isoformat()
    }
    
    success = context_engine.validate_evidence(
        validation.evidence_id,
        validation_result,
        validation.validator_id
    )
    
    if success:
        return {
            "status": "validated",
            "evidence_id": validation.evidence_id,
            "validation_status": validation.status,
            "overall_validation_progress": context_engine.validation_state.get('validation_progress', 0.0)
        }
    else:
        raise HTTPException(status_code=404, detail="Evidence not found")

# Case management endpoints
@app.get("/api/session/{session_id}/summary/generate")
async def generate_ai_summary(session_id: str):
    """Generate AI summary of case and evidence"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    
    # Mock AI summary generation
    mock_summary = {
        "ai_generated_summary": "Mock AI-generated case summary with key findings and analysis.",
        "key_findings": ["Evidence item 1 analysis", "Evidence item 2 analysis"],
        "evidence_summary": ["Summary of uploaded evidence"],
        "legal_assessment": "Potential ICC violations identified.",
        "recommendations": ["Complete validation", "Submit for review"]
    }
    
    context_engine.case_summary.update(mock_summary)
    
    return {
        "status": "generated",
        "case_summary": context_engine.case_summary
    }

@app.post("/api/session/{session_id}/document/generate")
async def generate_icc_document(session_id: str):
    """Generate final ICC submission document"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context_engine = active_sessions[session_id]
    
    try:
        # Check validation completeness
        if context_engine.validation_state.get('validation_progress', 0.0) < 0.8:
            raise HTTPException(
                status_code=400,
                detail="Case validation must be at least 80% complete before document generation"
            )
        
        # Generate ICC document
        icc_document = context_engine.generate_icc_document()
        
        return {
            "status": "generated",
            "document": icc_document,
            "validation_complete": context_engine.validation_state.get('validation_progress', 0.0) >= 1.0
        }
        
    except Exception as e:
        logger.error(f"ICC document generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints
@app.get("/api/sessions")
async def list_active_sessions():
    """List all active sessions"""
    sessions = []
    for session_id, context_engine in active_sessions.items():
        sessions.append({
            "session_id": session_id,
            "evidence_count": len(context_engine.evidence_pool),
            "validation_progress": context_engine.validation_state.get('validation_progress', 0.0),
        })
    
    return {"active_sessions": sessions}

@app.delete("/api/session/{session_id}")
async def close_session(session_id: str):
    """Close and cleanup session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
    if session_id in orchestrators:
        del orchestrators[session_id]
    
    logger.info(f"Closed session {session_id[:8]}")
    return {"status": "closed", "session_id": session_id}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "context_engine_available": CONTEXT_ENGINE_AVAILABLE,
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🇰🇪 Starting ICC Context Engine API...")
    uvicorn.run(
        "icc_context_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
