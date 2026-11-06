"""
🇰🇪 ICC CONTEXT INTELLIGENCE ENGINE
Core orchestration system for multi-agent forensic evidence analysis

RESPONSIBILITIES:
🔹 Shared context and session management across all agents
🔹 Evidence pool management with cross-referencing
🔹 Case file number generation and tracking
🔹 Multi-agent communication and data sharing
🔹 Professional ICC case document generation
🔹 Human-in-the-loop validation state management
"""

import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class EvidenceItem:
    """Structured evidence item with metadata"""
    file_id: str
    filename: str
    file_type: str
    size: int
    upload_timestamp: str
    content_hash: str
    metadata: Dict[str, Any]
    analysis_results: Dict[str, Any]
    agent_insights: Dict[str, Any]  # Insights from different agents
    legal_relevance: float
    quality_score: float
    validation_status: str = "pending"  # pending, validated, rejected

@dataclass
class CaseMetadata:
    """ICC case metadata structure"""
    case_id: str
    file_number: str
    incident_date: str
    incident_time: str
    incident_location: str
    incident_description: str
    victim_info: str
    perpetrator_info: str
    witness_info: str
    urgency_level: str
    submitter_info: Dict[str, Any]
    creation_timestamp: str
    last_updated: str
    case_status: str = "draft"  # draft, under_review, validated, submitted

class ICCContextEngine:
    """Central intelligence engine for ICC case building"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.evidence_pool: List[EvidenceItem] = []
        self.extracted_data: Dict[str, Any] = {}
        self.case_metadata: Optional[CaseMetadata] = None
        self.agent_registry: Dict[str, Any] = {}
        self.cross_references: Dict[str, List[str]] = {}
        self.case_timeline: List[Dict[str, Any]] = []
        
        # Human validation state tracking
        self.validation_state: Dict[str, Any] = {
            'human_reviewed': False,
            'summary_edited': False,
            'evidence_validated': False,
            'legal_analysis_confirmed': False,
            'witness_consent': False,
            'chain_of_custody': False,
            'validation_progress': 0.0,
            'validation_notes': [],
            'reviewer_id': None,
            'review_timestamp': None
        }
        
        # Case summary for human review
        self.case_summary: Dict[str, Any] = {
            'ai_generated_summary': '',
            'human_edited_summary': '',
            'key_findings': [],
            'evidence_summary': [],
            'legal_assessment': '',
            'recommendations': []
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"ICCContext-{self.session_id[:8]}")
        
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        return str(uuid.uuid4())
    
    def initialize_case(self, incident_details: Dict[str, Any]) -> str:
        """Initialize new ICC case with metadata"""
        case_id = self._generate_case_id()
        file_number = self._generate_icc_file_number(incident_details)
        
        self.case_metadata = CaseMetadata(
            case_id=case_id,
            file_number=file_number,
            incident_date=incident_details.get('date', ''),
            incident_time=incident_details.get('time', ''),
            incident_location=incident_details.get('location', ''),
            incident_description=incident_details.get('description', ''),
            victim_info=incident_details.get('victim_info', ''),
            perpetrator_info=incident_details.get('perpetrator_info', ''),
            witness_info=incident_details.get('witness_info', ''),
            urgency_level=incident_details.get('urgency_level', 'High'),
            submitter_info=incident_details.get('submitter_info', {}),
            creation_timestamp=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        self._update_case_timeline('case_initialized', case_id, file_number)
        self.logger.info(f"Initialized case: {file_number}")
        return file_number
    
    def _generate_case_id(self) -> str:
        """Generate unique case identifier"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]
        return f"CASE-{timestamp}-{random_suffix}"
    
    def _generate_icc_file_number(self, incident_details: Dict[str, Any]) -> str:
        """Generate systematic ICC file number"""
        # Extract location components
        location = incident_details.get('location', 'UNKNOWN')
        
        # Parse location for country and city
        location_parts = location.split(',')
        country = "KE"  # Default to Kenya
        city = "UNKNOWN"
        
        if len(location_parts) >= 2:
            city = location_parts[0].strip().upper().replace(' ', '-')
            if 'kenya' in location.lower():
                country = "KE"
        
        # Extract incident type
        description = incident_details.get('description', '').upper()
        incident_type = "VIOLATION"
        
        if 'SHOOT' in description or 'SHOT' in description:
            incident_type = "SHOOTING"
        elif 'TORTURE' in description:
            incident_type = "TORTURE"
        elif 'DISAPPEAR' in description:
            incident_type = "DISAPPEARANCE"
        elif 'ARREST' in description:
            incident_type = "ARREST"
        
        # Extract perpetrator info
        perpetrator = incident_details.get('perpetrator_info', '').upper()
        perpetrator_code = "UNKNOWN"
        
        if 'GSU' in perpetrator:
            perpetrator_code = "GSU"
        elif 'POLICE' in perpetrator:
            perpetrator_code = "POLICE"
        elif 'MILITARY' in perpetrator:
            perpetrator_code = "MILITARY"
        
        # Generate date component
        date_component = datetime.now().strftime("%Y%m%d")
        
        # Combine components
        file_number = f"ICC-{country}-{city}-{perpetrator_code}-{incident_type}-{date_component}"
        
        return file_number
    
    def add_evidence(self, file_data: Dict[str, Any], agent_analysis: Dict[str, Any]) -> str:
        """Add evidence to the pool with agent analysis"""
        file_id = self._generate_evidence_id()
        content_hash = self._generate_content_hash(file_data.get('content', ''))
        
        evidence_item = EvidenceItem(
            file_id=file_id,
            filename=file_data.get('filename', ''),
            file_type=file_data.get('type', ''),
            size=file_data.get('size', 0),
            upload_timestamp=datetime.now().isoformat(),
            content_hash=content_hash,
            metadata=file_data.get('metadata', {}),
            analysis_results=agent_analysis,
            agent_insights={},
            legal_relevance=agent_analysis.get('relevance_score', 0.0),
            quality_score=self._calculate_quality_score(file_data, agent_analysis)
        )
        
        self.evidence_pool.append(evidence_item)
        self._update_cross_references(evidence_item)
        self._update_case_timeline('evidence_added', file_id, evidence_item.filename)
        
        self.logger.info(f"Added evidence: {evidence_item.filename} (ID: {file_id})")
        return file_id
    
    def add_agent_insight(self, evidence_id: str, agent_name: str, insight: Dict[str, Any]) -> bool:
        """Add insight from specific agent to evidence"""
        evidence = self._get_evidence_by_id(evidence_id)
        if evidence:
            evidence.agent_insights[agent_name] = {
                'insight': insight,
                'timestamp': datetime.now().isoformat(),
                'confidence': insight.get('confidence', 0.0)
            }
            self._update_case_timeline('agent_insight', evidence_id, f"{agent_name} analysis")
            return True
        return False
    
    def update_validation_state(self, field: str, value: Any, reviewer_id: str = None) -> bool:
        """Update human validation state"""
        if field in self.validation_state:
            self.validation_state[field] = value
            if reviewer_id:
                self.validation_state['reviewer_id'] = reviewer_id
            self.validation_state['review_timestamp'] = datetime.now().isoformat()
            
            # Update progress
            self._calculate_validation_progress()
            
            self._update_case_timeline('validation_update', field, str(value))
            self.logger.info(f"Validation state updated: {field} = {value}")
            return True
        return False
    
    def update_case_summary(self, summary_data: Dict[str, Any], editor_id: str = None) -> bool:
        """Update case summary with human edits"""
        for key, value in summary_data.items():
            if key in self.case_summary:
                self.case_summary[key] = value
        
        if editor_id:
            self.case_summary['editor_id'] = editor_id
            self.case_summary['edit_timestamp'] = datetime.now().isoformat()
        
        # Mark as human edited
        self.validation_state['summary_edited'] = True
        self._calculate_validation_progress()
        
        self._update_case_timeline('summary_updated', 'human_edit', 'Case summary edited')
        self.logger.info("Case summary updated by human reviewer")
        return True
    
    def validate_evidence(self, evidence_id: str, validation_result: Dict[str, Any], validator_id: str = None) -> bool:
        """Validate specific evidence item"""
        evidence = self._get_evidence_by_id(evidence_id)
        if evidence:
            evidence.validation_status = validation_result.get('status', 'pending')
            evidence.metadata['validation'] = {
                'result': validation_result,
                'validator_id': validator_id,
                'timestamp': datetime.now().isoformat()
            }
            
            self._update_case_timeline('evidence_validated', evidence_id, f"Status: {evidence.validation_status}")
            self.logger.info(f"Evidence validated: {evidence_id} - {evidence.validation_status}")
            
            # Check if all evidence is validated
            self._check_evidence_validation_complete()
            return True
        return False
    
    def generate_icc_document(self) -> Dict[str, Any]:
        """Generate complete ICC submission document"""
        if not self.case_metadata:
            raise ValueError("Case metadata not initialized")
        
        # Compile evidence summaries
        evidence_summaries = []
        for evidence in self.evidence_pool:
            if evidence.validation_status == "validated":
                evidence_summaries.append({
                    'filename': evidence.filename,
                    'type': evidence.file_type,
                    'analysis': evidence.analysis_results,
                    'insights': evidence.agent_insights,
                    'relevance': evidence.legal_relevance,
                    'quality': evidence.quality_score
                })
        
        # Generate comprehensive document
        icc_document = {
            'header': {
                'title': 'COMMUNICATION TO THE INTERNATIONAL CRIMINAL COURT',
                'file_number': self.case_metadata.file_number,
                'submission_date': datetime.now().strftime("%Y-%m-%d"),
                'case_id': self.case_metadata.case_id
            },
            'case_information': asdict(self.case_metadata),
            'incident_summary': {
                'description': self.case_summary.get('human_edited_summary') or self.case_summary.get('ai_generated_summary'),
                'key_findings': self.case_summary.get('key_findings', []),
                'legal_assessment': self.case_summary.get('legal_assessment', '')
            },
            'evidence_analysis': {
                'total_evidence_items': len(evidence_summaries),
                'validated_items': len([e for e in self.evidence_pool if e.validation_status == "validated"]),
                'evidence_summaries': evidence_summaries
            },
            'cross_references': self.cross_references,
            'timeline': self.case_timeline,
            'validation_status': self.validation_state,
            'recommendations': self.case_summary.get('recommendations', []),
            'submitter_certification': {
                'reviewed_by_human': self.validation_state['human_reviewed'],
                'evidence_validated': self.validation_state['evidence_validated'],
                'legal_analysis_confirmed': self.validation_state['legal_analysis_confirmed'],
                'validation_progress': self.validation_state['validation_progress']
            }
        }
        
        self._update_case_timeline('document_generated', 'icc_submission', 'ICC document prepared')
        self.logger.info("ICC submission document generated")
        
        return icc_document
    
    def get_context_state(self) -> Dict[str, Any]:
        """Get complete context state for frontend"""
        return {
            'session_id': self.session_id,
            'case_metadata': asdict(self.case_metadata) if self.case_metadata else None,
            'evidence_pool': [asdict(evidence) for evidence in self.evidence_pool],
            'validation_state': self.validation_state,
            'case_summary': self.case_summary,
            'cross_references': self.cross_references,
            'timeline': self.case_timeline,
            'extracted_data': self.extracted_data
        }
    
    def _generate_evidence_id(self) -> str:
        """Generate unique evidence identifier"""
        return f"EVD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate content hash for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _calculate_quality_score(self, file_data: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Calculate evidence quality score"""
        base_score = 0.5
        
        # File size factor
        size = file_data.get('size', 0)
        if size > 1000:  # Minimum meaningful size
            base_score += 0.1
        
        # Analysis confidence factor
        confidence = analysis.get('confidence', 0.0)
        base_score += (confidence * 0.3)
        
        # Relevance factor
        relevance = analysis.get('relevance_score', 0.0)
        base_score += (relevance * 0.1)
        
        return min(base_score, 1.0)
    
    def _get_evidence_by_id(self, evidence_id: str) -> Optional[EvidenceItem]:
        """Find evidence by ID"""
        for evidence in self.evidence_pool:
            if evidence.file_id == evidence_id:
                return evidence
        return None
    
    def _update_cross_references(self, evidence: EvidenceItem):
        """Update cross-reference mapping"""
        # Extract entities for cross-referencing
        analysis = evidence.analysis_results
        entities = analysis.get('entities', [])
        
        for entity in entities:
            entity_name = entity.get('name', '').lower()
            if entity_name not in self.cross_references:
                self.cross_references[entity_name] = []
            
            if evidence.file_id not in self.cross_references[entity_name]:
                self.cross_references[entity_name].append(evidence.file_id)
    
    def _update_case_timeline(self, event_type: str, item_id: str, description: str):
        """Add event to case timeline"""
        self.case_timeline.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'item_id': item_id,
            'description': description
        })
    
    def _calculate_validation_progress(self):
        """Calculate overall validation progress"""
        total_checks = 6  # Number of validation fields
        completed_checks = sum([
            self.validation_state['human_reviewed'],
            self.validation_state['summary_edited'],
            self.validation_state['evidence_validated'],
            self.validation_state['legal_analysis_confirmed'],
            self.validation_state['witness_consent'],
            self.validation_state['chain_of_custody']
        ])
        
        self.validation_state['validation_progress'] = completed_checks / total_checks
    
    def _check_evidence_validation_complete(self):
        """Check if all evidence items are validated"""
        total_evidence = len(self.evidence_pool)
        validated_evidence = len([e for e in self.evidence_pool if e.validation_status == "validated"])
        
        if total_evidence > 0 and validated_evidence == total_evidence:
            self.validation_state['evidence_validated'] = True
            self._calculate_validation_progress()
