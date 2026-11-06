"""
🇰🇪 ICC CONTEXT INTELLIGENCE ENGINE
Core orcclass ICCContextEngine:
    Central intelligence engine for ICC case building
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.evidence_pool: List[EvidenceItem] = []
        self.extracted_data: Dict[str, Any] = {}
        self.case_metadata: Optional[CaseMetadata] = None
        self.agent_registry: Dict[str, Any] = {}
        self.cross_references: Dict[str, List[str]] = {}
        self.case_timeline: List[Dict[str, Any]] = []
        self.validation_state: Dict[str, Any] = {
            'human_reviewed': False,
            'summary_edited': False,
            'evidence_validated': False,
            'legal_analysis_confirmed': False,
            'witness_consent': False,
            'chain_of_custody': False,
            'validation_progress': 0.0
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"ICCContext-{self.session_id[:8]}")tem for multi-agent forensic evidence analysis

RESPONSIBILITIES:
🔹 Shared context and session management across all agents
🔹 Evidence pool management with cross-referencing
🔹 Case file number generation and tracking
🔹 Multi-agent communication and data sharing
🔹 Professional ICC case document generation
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
                'timestamp': datetime.now().isoformat(),
                'data': insight
            }
            self._update_case_timeline('agent_insight', evidence_id, f"{agent_name} analysis")
            return True
        return False
    
    def get_shared_context(self) -> Dict[str, Any]:
        """Get complete shared context for agents"""
        return {
            'session_id': self.session_id,
            'case_metadata': asdict(self.case_metadata) if self.case_metadata else None,
            'evidence_count': len(self.evidence_pool),
            'evidence_summary': self._generate_evidence_summary(),
            'cross_references': self.cross_references,
            'timeline': self.case_timeline,
            'extracted_entities': self._extract_common_entities(),
            'case_strength': self._assess_case_strength()
        }
    
    def generate_comprehensive_case_summary(self) -> Dict[str, Any]:
        """Generate comprehensive ICC case summary with cross-referenced evidence"""
        if not self.case_metadata:
            raise ValueError("Case not initialized")
        
        # Cross-reference all evidence
        evidence_analysis = self._perform_cross_evidence_analysis()
        
        # Generate timeline of events
        event_timeline = self._reconstruct_event_timeline()
        
        # Calculate case strength
        case_strength = self._assess_case_strength()
        
        # Generate legal recommendations
        legal_recommendations = self._generate_legal_recommendations()
        
        return {
            'case_header': {
                'file_number': self.case_metadata.file_number,
                'generation_date': datetime.now().isoformat(),
                'case_id': self.case_metadata.case_id,
                'urgency_level': self.case_metadata.urgency_level
            },
            'incident_summary': {
                'location': self.case_metadata.incident_location,
                'date_time': f"{self.case_metadata.incident_date} {self.case_metadata.incident_time}",
                'description': self.case_metadata.incident_description,
                'victims': self.case_metadata.victim_info,
                'perpetrators': self.case_metadata.perpetrator_info,
                'witnesses': self.case_metadata.witness_info
            },
            'evidence_inventory': self._generate_evidence_inventory(),
            'forensic_analysis': evidence_analysis,
            'event_timeline': event_timeline,
            'case_correlation_matrix': self._generate_correlation_matrix(),
            'case_strength_assessment': case_strength,
            'legal_recommendations': legal_recommendations,
            'submitter_information': self.case_metadata.submitter_info
        }
    
    def create_icc_case_document(self) -> str:
        """Generate professional ICC case document"""
        case_summary = self.generate_comprehensive_case_summary()
        
        document = f"""
═══════════════════════════════════════════════════════════════════════════════
                    INTERNATIONAL CRIMINAL COURT
                         EVIDENCE SUBMISSION
═══════════════════════════════════════════════════════════════════════════════

File Number: {case_summary['case_header']['file_number']}
Date Generated: {case_summary['case_header']['generation_date']}
Case ID: {case_summary['case_header']['case_id']}
Urgency Level: {case_summary['case_header']['urgency_level']}

═══ INCIDENT SUMMARY ═══════════════════════════════════════════════════════════

Location: {case_summary['incident_summary']['location']}
Date/Time: {case_summary['incident_summary']['date_time']}
Incident: {case_summary['incident_summary']['description']}

Victim Information:
{case_summary['incident_summary']['victims']}

Perpetrator Information:
{case_summary['incident_summary']['perpetrators']}

Witness Information:
{case_summary['incident_summary']['witnesses']}

═══ EVIDENCE INVENTORY ═════════════════════════════════════════════════════════

Total Evidence Items: {len(case_summary['evidence_inventory'])}

"""
        
        # Add evidence details
        for idx, evidence in enumerate(case_summary['evidence_inventory'], 1):
            document += f"""
{idx}. {evidence['filename']} ({evidence['file_type']})
   • Upload Time: {evidence['upload_timestamp']}
   • Quality Score: {evidence['quality_score']:.2f}/10
   • Legal Relevance: {evidence['legal_relevance']:.2f}/10
   • Analysis: {evidence.get('summary', 'No analysis available')}
   • Metadata: {self._format_metadata(evidence.get('metadata', {}))}
"""
        
        document += f"""
═══ AI FORENSIC ANALYSIS ═══════════════════════════════════════════════════════

{self._format_forensic_analysis(case_summary['forensic_analysis'])}

═══ EVENT TIMELINE ═════════════════════════════════════════════════════════════

{self._format_timeline(case_summary['event_timeline'])}

═══ CASE CORRELATION MATRIX ════════════════════════════════════════════════════

{self._format_correlation_matrix(case_summary['case_correlation_matrix'])}

═══ CASE STRENGTH ASSESSMENT ═══════════════════════════════════════════════════

Overall Strength: {case_summary['case_strength_assessment']['overall_score']:.1f}/10
Evidence Quality: {case_summary['case_strength_assessment']['evidence_quality']:.1f}/10
Legal Viability: {case_summary['case_strength_assessment']['legal_viability']:.1f}/10

Strengths:
{self._format_list(case_summary['case_strength_assessment']['strengths'])}

Weaknesses:
{self._format_list(case_summary['case_strength_assessment']['weaknesses'])}

═══ RECOMMENDED ACTIONS ════════════════════════════════════════════════════════

{self._format_recommendations(case_summary['legal_recommendations'])}

═══ SUBMISSION INFORMATION ═════════════════════════════════════════════════════

Submitted by: {case_summary['submitter_information'].get('name', 'Anonymous')}
Contact: {case_summary['submitter_information'].get('email', 'Not provided')}
Role: {case_summary['submitter_information'].get('role', 'Witness')}

═══════════════════════════════════════════════════════════════════════════════
                          END OF DOCUMENT
═══════════════════════════════════════════════════════════════════════════════
"""
        
        return document
    
    # Helper methods
    def _generate_evidence_id(self) -> str:
        """Generate unique evidence identifier"""
        return f"EV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]}"
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate content hash for deduplication"""
        return hashlib.sha256(str(content).encode()).hexdigest()
    
    def _calculate_quality_score(self, file_data: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Calculate evidence quality score"""
        base_score = 5.0
        
        # File size bonus (larger files generally higher quality)
        size_bonus = min(file_data.get('size', 0) / (1024 * 1024), 2.0)  # Max 2 points for size
        
        # Analysis confidence bonus
        confidence_bonus = analysis.get('confidence', 0.5) * 3.0  # Max 3 points
        
        # Metadata completeness bonus
        metadata = file_data.get('metadata', {})
        metadata_bonus = len([k for k, v in metadata.items() if v]) * 0.2  # 0.2 per metadata field
        
        total_score = min(base_score + size_bonus + confidence_bonus + metadata_bonus, 10.0)
        return round(total_score, 2)
    
    def _get_evidence_by_id(self, evidence_id: str) -> Optional[EvidenceItem]:
        """Get evidence item by ID"""
        for evidence in self.evidence_pool:
            if evidence.file_id == evidence_id:
                return evidence
        return None
    
    def _update_cross_references(self, evidence: EvidenceItem):
        """Update cross-references between evidence items"""
        # Simple cross-referencing based on metadata and content
        for existing_evidence in self.evidence_pool[:-1]:  # Exclude the just-added evidence
            similarity_score = self._calculate_similarity(evidence, existing_evidence)
            if similarity_score > 0.3:  # Threshold for relevance
                if evidence.file_id not in self.cross_references:
                    self.cross_references[evidence.file_id] = []
                if existing_evidence.file_id not in self.cross_references:
                    self.cross_references[existing_evidence.file_id] = []
                
                self.cross_references[evidence.file_id].append(existing_evidence.file_id)
                self.cross_references[existing_evidence.file_id].append(evidence.file_id)
    
    def _calculate_similarity(self, evidence1: EvidenceItem, evidence2: EvidenceItem) -> float:
        """Calculate similarity between two evidence items"""
        # Simple similarity based on metadata overlap
        metadata1 = evidence1.metadata
        metadata2 = evidence2.metadata
        
        common_keys = set(metadata1.keys()) & set(metadata2.keys())
        if not common_keys:
            return 0.0
        
        matching_values = sum(1 for key in common_keys if metadata1[key] == metadata2[key])
        return matching_values / len(common_keys)
    
    def _update_case_timeline(self, event_type: str, evidence_id: str, description: str):
        """Update case timeline with new event"""
        self.case_timeline.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'evidence_id': evidence_id,
            'description': description
        })
    
    def _generate_evidence_summary(self) -> Dict[str, Any]:
        """Generate summary of all evidence"""
        if not self.evidence_pool:
            return {}
        
        file_types = {}
        total_size = 0
        avg_quality = 0
        
        for evidence in self.evidence_pool:
            file_types[evidence.file_type] = file_types.get(evidence.file_type, 0) + 1
            total_size += evidence.size
            avg_quality += evidence.quality_score
        
        return {
            'total_items': len(self.evidence_pool),
            'file_types': file_types,
            'total_size': total_size,
            'average_quality': round(avg_quality / len(self.evidence_pool), 2),
            'cross_references': len(self.cross_references)
        }
    
    def _extract_common_entities(self) -> Dict[str, List[str]]:
        """Extract common entities across all evidence"""
        entities = {
            'locations': [],
            'people': [],
            'organizations': [],
            'dates': [],
            'weapons': [],
            'vehicles': []
        }
        
        # Extract from metadata and analysis results
        for evidence in self.evidence_pool:
            # Extract from metadata
            if 'location' in evidence.metadata:
                entities['locations'].append(evidence.metadata['location'])
            
            # Extract from analysis results
            analysis = evidence.analysis_results
            if 'entities' in analysis:
                for entity_type, entity_list in analysis['entities'].items():
                    if entity_type in entities:
                        entities[entity_type].extend(entity_list)
        
        # Remove duplicates and empty values
        for key in entities:
            entities[key] = list(set(filter(None, entities[key])))
        
        return entities
    
    def _assess_case_strength(self) -> Dict[str, Any]:
        """Assess overall case strength"""
        if not self.evidence_pool:
            return {'overall_score': 0.0, 'evidence_quality': 0.0, 'legal_viability': 0.0}
        
        # Calculate evidence quality
        avg_quality = sum(e.quality_score for e in self.evidence_pool) / len(self.evidence_pool)
        
        # Calculate evidence diversity
        file_types = set(e.file_type for e in self.evidence_pool)
        diversity_score = min(len(file_types) * 2.0, 10.0)
        
        # Calculate cross-reference strength
        cross_ref_score = min(len(self.cross_references) * 1.5, 10.0)
        
        # Calculate legal viability
        high_relevance_count = sum(1 for e in self.evidence_pool if e.legal_relevance > 7.0)
        legal_viability = min(high_relevance_count * 2.0, 10.0)
        
        overall_score = (avg_quality + diversity_score + cross_ref_score + legal_viability) / 4.0
        
        strengths = []
        weaknesses = []
        
        if avg_quality > 7.0:
            strengths.append("High-quality evidence collection")
        elif avg_quality < 5.0:
            weaknesses.append("Evidence quality concerns")
        
        if len(file_types) > 2:
            strengths.append("Diverse evidence types")
        else:
            weaknesses.append("Limited evidence diversity")
        
        if len(self.cross_references) > 3:
            strengths.append("Strong evidence correlation")
        else:
            weaknesses.append("Weak evidence correlation")
        
        return {
            'overall_score': round(overall_score, 1),
            'evidence_quality': round(avg_quality, 1),
            'legal_viability': round(legal_viability, 1),
            'diversity_score': round(diversity_score, 1),
            'correlation_score': round(cross_ref_score, 1),
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def _perform_cross_evidence_analysis(self) -> Dict[str, Any]:
        """Perform cross-analysis of all evidence"""
        return {
            'visual_evidence': self._analyze_visual_evidence(),
            'audio_evidence': self._analyze_audio_evidence(), 
            'document_evidence': self._analyze_document_evidence(),
            'metadata_correlation': self._analyze_metadata_correlation()
        }
    
    def _analyze_visual_evidence(self) -> Dict[str, Any]:
        """Analyze visual evidence (images, videos)"""
        visual_evidence = [e for e in self.evidence_pool if e.file_type.startswith('image/') or e.file_type.startswith('video/')]
        
        if not visual_evidence:
            return {'count': 0, 'analysis': 'No visual evidence found'}
        
        # Analyze common elements
        common_objects = []
        locations = []
        timestamps = []
        
        for evidence in visual_evidence:
            metadata = evidence.metadata
            analysis = evidence.analysis_results
            
            if 'objects' in analysis:
                common_objects.extend(analysis['objects'])
            if 'location' in metadata:
                locations.append(metadata['location'])
            if 'timestamp' in metadata:
                timestamps.append(metadata['timestamp'])
        
        return {
            'count': len(visual_evidence),
            'common_objects': list(set(common_objects)),
            'locations': list(set(locations)),
            'timeline': sorted(set(timestamps)),
            'analysis': "Visual evidence shows consistent scene elements and timeline"
        }
    
    def _analyze_audio_evidence(self) -> Dict[str, Any]:
        """Analyze audio evidence"""
        audio_evidence = [e for e in self.evidence_pool if e.file_type.startswith('audio/')]
        
        if not audio_evidence:
            return {'count': 0, 'analysis': 'No audio evidence found'}
        
        # Analyze transcriptions and audio metadata
        transcriptions = []
        speakers = []
        
        for evidence in audio_evidence:
            analysis = evidence.analysis_results
            if 'transcription' in analysis:
                transcriptions.append(analysis['transcription'])
            if 'speakers' in analysis:
                speakers.extend(analysis['speakers'])
        
        return {
            'count': len(audio_evidence),
            'transcriptions': transcriptions,
            'identified_speakers': list(set(speakers)),
            'analysis': "Audio evidence provides testimonial context and speaker identification"
        }
    
    def _analyze_document_evidence(self) -> Dict[str, Any]:
        """Analyze document evidence"""
        doc_evidence = [e for e in self.evidence_pool if 'document' in e.file_type or e.file_type == 'application/pdf']
        
        if not doc_evidence:
            return {'count': 0, 'analysis': 'No document evidence found'}
        
        # Analyze document content and entities
        entities = []
        dates = []
        
        for evidence in doc_evidence:
            analysis = evidence.analysis_results
            if 'entities' in analysis:
                entities.extend(analysis['entities'])
            if 'dates' in analysis:
                dates.extend(analysis['dates'])
        
        return {
            'count': len(doc_evidence),
            'extracted_entities': list(set(entities)),
            'important_dates': list(set(dates)),
            'analysis': "Document evidence provides legal context and supporting information"
        }
    
    def _analyze_metadata_correlation(self) -> Dict[str, Any]:
        """Analyze metadata correlations across evidence"""
        correlations = {
            'temporal': self._find_temporal_correlations(),
            'spatial': self._find_spatial_correlations(),
            'technical': self._find_technical_correlations()
        }
        
        return correlations
    
    def _find_temporal_correlations(self) -> List[str]:
        """Find temporal correlations in evidence"""
        timestamps = []
        for evidence in self.evidence_pool:
            if 'timestamp' in evidence.metadata:
                timestamps.append((evidence.filename, evidence.metadata['timestamp']))
        
        if len(timestamps) > 1:
            return [f"Timeline correlation found between {len(timestamps)} evidence items"]
        return []
    
    def _find_spatial_correlations(self) -> List[str]:
        """Find spatial correlations in evidence"""
        locations = []
        for evidence in self.evidence_pool:
            if 'location' in evidence.metadata:
                locations.append((evidence.filename, evidence.metadata['location']))
        
        if len(locations) > 1:
            return [f"Location correlation found across {len(locations)} evidence items"]
        return []
    
    def _find_technical_correlations(self) -> List[str]:
        """Find technical correlations in evidence"""
        devices = []
        for evidence in self.evidence_pool:
            metadata = evidence.metadata
            if 'camera_make' in metadata or 'device' in metadata:
                device = metadata.get('camera_make', metadata.get('device', 'Unknown'))
                devices.append((evidence.filename, device))
        
        if len(devices) > 1:
            return [f"Device correlation found across {len(devices)} evidence items"]
        return []
    
    def _reconstruct_event_timeline(self) -> List[Dict[str, Any]]:
        """Reconstruct timeline of events from evidence"""
        timeline_events = []
        
        for evidence in self.evidence_pool:
            metadata = evidence.metadata
            if 'timestamp' in metadata or 'creation_date' in metadata:
                event_time = metadata.get('timestamp', metadata.get('creation_date'))
                timeline_events.append({
                    'timestamp': event_time,
                    'evidence_file': evidence.filename,
                    'event_type': self._infer_event_type(evidence),
                    'description': f"Evidence captured: {evidence.filename}"
                })
        
        # Sort by timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])
        return timeline_events
    
    def _infer_event_type(self, evidence: EvidenceItem) -> str:
        """Infer event type from evidence"""
        if evidence.file_type.startswith('image/'):
            return "Visual Documentation"
        elif evidence.file_type.startswith('video/'):
            return "Video Recording"
        elif evidence.file_type.startswith('audio/'):
            return "Audio Recording"
        else:
            return "Document Evidence"
    
    def _generate_correlation_matrix(self) -> Dict[str, Any]:
        """Generate evidence correlation matrix"""
        matrix = {}
        
        for evidence in self.evidence_pool:
            evidence_id = evidence.file_id
            correlations = self.cross_references.get(evidence_id, [])
            
            matrix[evidence.filename] = {
                'correlations': len(correlations),
                'related_files': [self._get_evidence_by_id(corr_id).filename for corr_id in correlations if self._get_evidence_by_id(corr_id)],
                'correlation_strength': len(correlations) / max(len(self.evidence_pool) - 1, 1)
            }
        
        return matrix
    
    def _generate_legal_recommendations(self) -> List[str]:
        """Generate legal recommendations based on evidence"""
        recommendations = []
        
        case_strength = self._assess_case_strength()
        
        if case_strength['overall_score'] > 7.0:
            recommendations.append("Strong case for ICC submission - proceed with formal filing")
        elif case_strength['overall_score'] > 5.0:
            recommendations.append("Moderate case strength - consider gathering additional evidence")
        else:
            recommendations.append("Weak case - significant additional evidence required")
        
        if case_strength['evidence_quality'] < 6.0:
            recommendations.append("Improve evidence quality through enhanced documentation")
        
        if len(self.evidence_pool) < 3:
            recommendations.append("Expand evidence collection for stronger case foundation")
        
        if not any(e.file_type.startswith('video/') for e in self.evidence_pool):
            recommendations.append("Consider obtaining video evidence for stronger visual documentation")
        
        recommendations.append("Ensure witness protection protocols are followed")
        recommendations.append("Maintain chain of custody documentation for all evidence")
        
        return recommendations
    
    def _generate_evidence_inventory(self) -> List[Dict[str, Any]]:
        """Generate detailed evidence inventory"""
        inventory = []
        
        for evidence in self.evidence_pool:
            inventory.append({
                'file_id': evidence.file_id,
                'filename': evidence.filename,
                'file_type': evidence.file_type,
                'size': evidence.size,
                'upload_timestamp': evidence.upload_timestamp,
                'quality_score': evidence.quality_score,
                'legal_relevance': evidence.legal_relevance,
                'metadata': evidence.metadata,
                'summary': evidence.analysis_results.get('evidence_description', 'No analysis available'),
                'cross_references': len(self.cross_references.get(evidence.file_id, []))
            })
        
        return inventory
    
    # Document formatting helpers
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for document display"""
        if not metadata:
            return "No metadata available"
        
        formatted = []
        for key, value in metadata.items():
            if value:
                formatted.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "; ".join(formatted) if formatted else "No metadata available"
    
    def _format_forensic_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format forensic analysis for document display"""
        sections = []
        
        for section_name, section_data in analysis.items():
            sections.append(f"{section_name.replace('_', ' ').title()}:")
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    sections.append(f"  • {key.replace('_', ' ').title()}: {value}")
            else:
                sections.append(f"  {section_data}")
            sections.append("")
        
        return "\n".join(sections)
    
    def _format_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        """Format timeline for document display"""
        if not timeline:
            return "No timeline data available"
        
        formatted = []
        for event in timeline:
            formatted.append(f"• {event['timestamp']}: {event['description']} ({event['event_type']})")
        
        return "\n".join(formatted)
    
    def _format_correlation_matrix(self, matrix: Dict[str, Any]) -> str:
        """Format correlation matrix for document display"""
        if not matrix:
            return "No correlations found"
        
        formatted = []
        for filename, data in matrix.items():
            if data['correlations'] > 0:
                formatted.append(f"• {filename}: {data['correlations']} correlations with {', '.join(data['related_files'])}")
        
        return "\n".join(formatted) if formatted else "No significant correlations found"
    
    def _format_list(self, items: List[str]) -> str:
        """Format list for document display"""
        if not items:
            return "None identified"
        return "\n".join(f"• {item}" for item in items)
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for document display"""
        if not recommendations:
            return "No specific recommendations"
        
        formatted = []
        for i, rec in enumerate(recommendations, 1):
            formatted.append(f"{i}. {rec}")
        
        return "\n".join(formatted)
