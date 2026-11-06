"""
🇰🇪 ICC EVIDENCE ORCHESTRATOR
Core logic extracted from Streamlit app for API-first architecture

RESPONSIBILITIES:
🔹 Multi-agent evidence analysis pipeline
🔹 File processing with metadata extraction
🔹 AI-powered legal analysis using Groq
🔹 Evidence correlation and context building
🔹 ICC case document generation
🔹 Streamlit-free orchestration logic
"""

import os
import io
import hashlib
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from PIL import Image
import exifread
from geopy.geocoders import Nominatim
from mutagen import File as MutagenFile
import fitz  # PyMuPDF
from docx import Document
import cv2
from groq import Groq
from dotenv import load_dotenv

# Import our context engine
from .icc_context_engine import ICCContextEngine

# Load environment variables
load_dotenv()

class ICCEvidenceOrchestrator:
    """Main orchestrator for ICC evidence analysis pipeline"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_client = Groq(api_key=groq_api_key or os.getenv('GROQ_API_KEY'))
        self.context_engine = ICCContextEngine()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # File type mappings
        self.supported_formats = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm'],
            'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'],
            'document': ['.pdf', '.doc', '.docx', '.txt']
        }
        
        # Default incident details for GSU shooting case
        self.default_incident = {
            'date': '2025-06-17',
            'time': '14:00:00',
            'location': 'CBD, Nairobi, Kenya',
            'description': 'Person shot by GSU (General Service Unit)',
            'victim_info': '',
            'perpetrator_info': 'GSU Officers',
            'witness_info': '',
            'urgency_level': 'High'
        }
    
    def initialize_case(self, incident_details: Optional[Dict[str, Any]] = None, 
                       submitter_info: Optional[Dict[str, Any]] = None) -> str:
        """Initialize new ICC case with incident and submitter details"""
        
        # Use provided details or defaults
        incident = incident_details or self.default_incident.copy()
        
        # Add submitter info if provided
        if submitter_info:
            incident['submitter_info'] = submitter_info
        else:
            incident['submitter_info'] = {
                'name': 'Anonymous',
                'email': '',
                'phone': '',
                'role': 'Witness',
                'anonymous': True
            }
        
        # Initialize case in context engine
        file_number = self.context_engine.initialize_case(incident)
        
        self.logger.info(f"Initialized ICC case: {file_number}")
        return file_number
    
    async def process_evidence_pipeline(self, files: List[Dict[str, Any]], 
                                      keywords: Optional[str] = None,
                                      incident_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main evidence processing pipeline
        
        Args:
            files: List of file data dictionaries with 'content', 'filename', 'type', 'size'
            keywords: Optional keywords for analysis context
            incident_context: Optional incident context for enhanced analysis
            
        Returns:
            Comprehensive analysis results with case summary
        """
        
        # Ensure case is initialized
        if not self.context_engine.case_metadata:
            self.initialize_case(incident_context)
        
        analysis_results = []
        
        # Process each file through the pipeline
        for file_data in files:
            try:
                self.logger.info(f"Processing file: {file_data.get('filename', 'unknown')}")
                
                # Extract metadata
                metadata = self.extract_comprehensive_metadata(file_data)
                
                # Perform AI analysis
                ai_analysis = await self.analyze_with_groq(file_data, metadata, keywords, incident_context)
                
                # Add to context engine
                evidence_id = self.context_engine.add_evidence(file_data, ai_analysis)
                
                analysis_results.append({
                    'evidence_id': evidence_id,
                    'filename': file_data.get('filename'),
                    'metadata': metadata,
                    'analysis': ai_analysis,
                    'quality_score': self._calculate_evidence_quality(file_data, metadata, ai_analysis),
                    'legal_relevance': ai_analysis.get('relevance_score', 5.0)
                })
                
            except Exception as e:
                self.logger.error(f"Error processing file {file_data.get('filename', 'unknown')}: {str(e)}")
                analysis_results.append({
                    'filename': file_data.get('filename'),
                    'error': str(e),
                    'status': 'failed'
                })
        
        # Generate comprehensive case summary
        case_summary = self.context_engine.generate_comprehensive_case_summary()
        
        return {
            'case_summary': case_summary,
            'evidence_analyses': analysis_results,
            'processing_summary': {
                'total_files': len(files),
                'successful': len([r for r in analysis_results if 'error' not in r]),
                'failed': len([r for r in analysis_results if 'error' in r]),
                'case_strength': case_summary.get('case_strength_assessment', {}).get('overall_score', 0.0)
            }
        }
    
    def extract_comprehensive_metadata(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive metadata from file based on type"""
        
        metadata = {
            'filename': file_data.get('filename', 'unknown'),
            'size': file_data.get('size', 0),
            'type': file_data.get('type', 'unknown'),
            'upload_timestamp': datetime.now().isoformat(),
            'content_hash': self._generate_content_hash(file_data.get('content', '')),
            'location': None,
            'timestamp': None,
            'gps_coords': None,
            'creation_date': None
        }
        
        try:
            content = file_data.get('content', b'')
            if isinstance(content, str):
                content = content.encode()
            
            file_type = file_data.get('type', '')
            filename = file_data.get('filename', '')
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Route to appropriate metadata extractor
            if file_type.startswith('image/') or file_ext in self.supported_formats['image']:
                metadata.update(self._extract_image_metadata(content))
            elif file_type.startswith('video/') or file_ext in self.supported_formats['video']:
                metadata.update(self._extract_video_metadata(content))
            elif file_type.startswith('audio/') or file_ext in self.supported_formats['audio']:
                metadata.update(self._extract_audio_metadata(content))
            elif file_type == 'application/pdf' or file_ext == '.pdf':
                metadata.update(self._extract_pdf_metadata(content))
            elif 'document' in file_type or file_ext in ['.doc', '.docx']:
                metadata.update(self._extract_document_metadata(content))
            
            # Convert GPS coordinates to address if available
            if metadata.get('gps_coords'):
                location_name = self._get_location_from_coords(metadata['gps_coords'])
                if location_name:
                    metadata['location'] = location_name
            
        except Exception as e:
            self.logger.warning(f"Error extracting metadata from {metadata['filename']}: {str(e)}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def analyze_with_groq(self, file_data: Dict[str, Any], metadata: Dict[str, Any], 
                               keywords: Optional[str] = None, 
                               incident_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced evidence analysis using Groq with comprehensive context"""
        
        # Get shared context from context engine
        shared_context = self.context_engine.get_shared_context()
        
        # Build comprehensive prompt
        prompt = self._build_analysis_prompt(file_data, metadata, keywords, incident_context, shared_context)
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert forensic analyst and legal assistant specializing in ICC evidence analysis. Provide detailed, structured analysis in valid JSON format."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content
            
            # Clean up response if it contains markdown code blocks
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            import json
            analysis = json.loads(analysis_text)
            
            # Ensure required fields
            analysis = self._validate_analysis_response(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in Groq analysis: {str(e)}")
            return self._generate_fallback_analysis(file_data, metadata)
    
    def _build_analysis_prompt(self, file_data: Dict[str, Any], metadata: Dict[str, Any],
                              keywords: Optional[str], incident_context: Optional[Dict[str, Any]],
                              shared_context: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt with all available context"""
        
        case_metadata = shared_context.get('case_metadata', {})
        
        prompt = f"""
        FORENSIC EVIDENCE ANALYSIS REQUEST
        
        CASE CONTEXT:
        File Number: {case_metadata.get('file_number', 'Unknown')}
        Incident Location: {case_metadata.get('incident_location', 'CBD, Nairobi, Kenya')}
        Incident Date: {case_metadata.get('incident_date', '2025-06-17')}
        Incident Time: {case_metadata.get('incident_time', '14:00')}
        Incident Description: {case_metadata.get('incident_description', 'Person shot by GSU')}
        
        EVIDENCE CONTEXT:
        Existing Evidence Items: {shared_context.get('evidence_count', 0)}
        Case Strength: {shared_context.get('case_strength', {}).get('overall_score', 'Unknown')}
        Cross-References: {len(shared_context.get('cross_references', {}))}
        
        CURRENT FILE ANALYSIS:
        Filename: {file_data.get('filename', 'unknown')}
        File Type: {file_data.get('type', 'unknown')}
        File Size: {file_data.get('size', 0)} bytes
        
        EXTRACTED METADATA:
        {self._format_metadata_for_prompt(metadata)}
        
        KEYWORDS/FOCUS: {keywords or 'General ICC evidence analysis'}
        
        ANALYSIS REQUEST:
        Provide comprehensive forensic analysis in the following JSON format:
        {{
            "evidence_type": "photograph|video|audio|document|witness_statement|other",
            "evidence_description": "Detailed description of evidence content and significance",
            "incident_relation": "How this evidence relates to the {case_metadata.get('incident_description', 'incident')}",
            "source_description": "Assessment of how evidence was likely obtained",
            "relevance_score": 8.5,
            "legal_significance": "Why this evidence is legally significant for ICC proceedings",
            "forensic_indicators": ["list", "of", "forensic", "elements"],
            "temporal_analysis": "Timeline relevance and temporal indicators",
            "spatial_analysis": "Location relevance and spatial indicators", 
            "technical_quality": "Assessment of technical quality for legal proceedings",
            "recommended_action": "Specific recommendations for this evidence",
            "cross_reference_potential": "How this evidence relates to other case elements",
            "chain_of_custody_notes": "Important chain of custody considerations",
            "icc_relevance": "high|medium|low",
            "evidence_quality": "excellent|good|fair|poor",
            "confidence_score": 8.7,
            "limitations": ["potential", "limitations", "or", "concerns"],
            "supporting_elements": ["elements", "that", "strengthen", "this", "evidence"],
            "entities": {{
                "people": ["identified", "persons"],
                "locations": ["identified", "locations"],
                "organizations": ["identified", "organizations"],
                "weapons": ["identified", "weapons"],
                "vehicles": ["identified", "vehicles"]
            }},
            "metadata_assessment": "Analysis of metadata reliability and forensic value"
        }}
        
        Ensure all scores are between 1-10 and provide specific, actionable insights.
        """
        
        return prompt
    
    def _format_metadata_for_prompt(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for inclusion in analysis prompt"""
        formatted_items = []
        
        for key, value in metadata.items():
            if value and key not in ['content_hash', 'upload_timestamp']:
                formatted_items.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_items) if formatted_items else "  No significant metadata extracted"
    
    def _validate_analysis_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure required fields in analysis response"""
        
        required_fields = {
            'evidence_type': 'other',
            'evidence_description': 'Evidence analysis pending',
            'incident_relation': 'Relation to incident being assessed',
            'relevance_score': 5.0,
            'legal_significance': 'Legal significance being evaluated',
            'icc_relevance': 'medium',
            'evidence_quality': 'fair',
            'confidence_score': 5.0
        }
        
        # Ensure required fields exist
        for field, default_value in required_fields.items():
            if field not in analysis:
                analysis[field] = default_value
        
        # Validate score ranges
        for score_field in ['relevance_score', 'confidence_score']:
            if score_field in analysis:
                try:
                    score = float(analysis[score_field])
                    analysis[score_field] = max(1.0, min(10.0, score))
                except (ValueError, TypeError):
                    analysis[score_field] = 5.0
        
        return analysis
    
    def _generate_fallback_analysis(self, file_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback analysis when Groq fails"""
        
        file_type = file_data.get('type', 'unknown')
        filename = file_data.get('filename', 'unknown')
        
        return {
            'evidence_type': self._infer_evidence_type(file_type),
            'evidence_description': f"File uploaded: {filename} ({file_type})",
            'incident_relation': "Evidence requires manual review for incident relation",
            'relevance_score': 5.0,
            'legal_significance': "Requires manual legal assessment",
            'icc_relevance': 'medium',
            'evidence_quality': 'fair',
            'confidence_score': 3.0,
            'analysis_status': 'fallback_generated',
            'note': 'Automated analysis failed, manual review required'
        }
    
    def _infer_evidence_type(self, file_type: str) -> str:
        """Infer evidence type from file type"""
        if file_type.startswith('image/'):
            return 'photograph'
        elif file_type.startswith('video/'):
            return 'video'
        elif file_type.startswith('audio/'):
            return 'audio'
        elif file_type == 'application/pdf' or 'document' in file_type:
            return 'document'
        else:
            return 'other'
    
    def generate_icc_case_document(self) -> str:
        """Generate professional ICC case document"""
        return self.context_engine.create_icc_case_document()
    
    def get_case_summary(self) -> Dict[str, Any]:
        """Get comprehensive case summary"""
        return self.context_engine.generate_comprehensive_case_summary()
    
    def get_evidence_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all evidence items"""
        return [
            {
                'evidence_id': evidence.file_id,
                'filename': evidence.filename,
                'file_type': evidence.file_type,
                'quality_score': evidence.quality_score,
                'legal_relevance': evidence.legal_relevance,
                'upload_timestamp': evidence.upload_timestamp,
                'analysis_summary': evidence.analysis_results.get('evidence_description', 'No analysis'),
                'cross_references': len(self.context_engine.cross_references.get(evidence.file_id, []))
            }
            for evidence in self.context_engine.evidence_pool
        ]
    
    def get_file_number(self) -> Optional[str]:
        """Get the ICC file number for this case"""
        if self.context_engine.case_metadata:
            return self.context_engine.case_metadata.file_number
        return None
    
    # Metadata extraction methods (extracted from Streamlit app)
    def _extract_image_metadata(self, file_content: bytes) -> Dict[str, Any]:
        """Extract metadata from image files"""
        metadata = {}
        try:
            # Create a file-like object from the content
            image_file = io.BytesIO(file_content)
            tags = exifread.process_file(image_file, details=False)
            
            # Extract GPS coordinates
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = self._convert_gps_to_decimal(tags['GPS GPSLatitude'], tags.get('GPS GPSLatitudeRef'))
                lon = self._convert_gps_to_decimal(tags['GPS GPSLongitude'], tags.get('GPS GPSLongitudeRef'))
                if lat and lon:
                    metadata['gps_coords'] = (lat, lon)
            
            # Extract timestamp
            if 'EXIF DateTimeOriginal' in tags:
                metadata['creation_date'] = str(tags['EXIF DateTimeOriginal'])
            elif 'EXIF DateTime' in tags:
                metadata['creation_date'] = str(tags['EXIF DateTime'])
            
            # Extract camera info
            if 'Image Make' in tags:
                metadata['camera_make'] = str(tags['Image Make'])
            if 'Image Model' in tags:
                metadata['camera_model'] = str(tags['Image Model'])
            
            # Extract image dimensions
            try:
                image = Image.open(io.BytesIO(file_content))
                metadata['width'] = image.width
                metadata['height'] = image.height
                metadata['mode'] = image.mode
            except Exception:
                pass
                
        except Exception as e:
            metadata['extraction_error'] = f"EXIF extraction failed: {str(e)}"
        
        return metadata
    
    def _extract_video_metadata(self, file_content: bytes) -> Dict[str, Any]:
        """Extract metadata from video files"""
        metadata = {}
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Use OpenCV to extract video metadata
            cap = cv2.VideoCapture(temp_path)
            if cap.isOpened():
                metadata['fps'] = cap.get(cv2.CAP_PROP_FPS)
                metadata['frame_count'] = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                metadata['duration'] = metadata['frame_count'] / metadata['fps'] if metadata['fps'] > 0 else 0
                metadata['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            metadata['extraction_error'] = f"Video metadata extraction failed: {str(e)}"
        
        return metadata
    
    def _extract_audio_metadata(self, file_content: bytes) -> Dict[str, Any]:
        """Extract metadata from audio files"""
        metadata = {}
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Use mutagen to extract audio metadata
            audio = MutagenFile(temp_path)
            if audio:
                metadata['duration'] = getattr(audio.info, 'length', 0)
                metadata['bitrate'] = getattr(audio.info, 'bitrate', None)
                
                # Extract tags if available
                if hasattr(audio, 'tags') and audio.tags:
                    for key, value in audio.tags.items():
                        if 'date' in key.lower() or 'year' in key.lower():
                            metadata['creation_date'] = str(value[0]) if isinstance(value, list) else str(value)
                            break
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            metadata['extraction_error'] = f"Audio metadata extraction failed: {str(e)}"
        
        return metadata
    
    def _extract_pdf_metadata(self, file_content: bytes) -> Dict[str, Any]:
        """Extract metadata from PDF files"""
        metadata = {}
        try:
            # Create PDF document from content
            pdf_doc = fitz.open(stream=file_content, filetype="pdf")
            
            # Extract basic info
            metadata['page_count'] = pdf_doc.page_count
            
            # Extract document metadata
            doc_metadata = pdf_doc.metadata
            if doc_metadata:
                metadata['title'] = doc_metadata.get('title', '')
                metadata['author'] = doc_metadata.get('author', '')
                metadata['subject'] = doc_metadata.get('subject', '')
                metadata['creator'] = doc_metadata.get('creator', '')
                metadata['producer'] = doc_metadata.get('producer', '')
                metadata['creation_date'] = doc_metadata.get('creationDate', '')
                metadata['modification_date'] = doc_metadata.get('modDate', '')
            
            pdf_doc.close()
            
        except Exception as e:
            metadata['extraction_error'] = f"PDF metadata extraction failed: {str(e)}"
        
        return metadata
    
    def _extract_document_metadata(self, file_content: bytes) -> Dict[str, Any]:
        """Extract metadata from Word documents"""
        metadata = {}
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Load document
            doc = Document(temp_path)
            
            # Extract core properties
            core_props = doc.core_properties
            metadata['title'] = core_props.title or ''
            metadata['author'] = core_props.author or ''
            metadata['subject'] = core_props.subject or ''
            metadata['creation_date'] = core_props.created.isoformat() if core_props.created else ''
            metadata['modification_date'] = core_props.modified.isoformat() if core_props.modified else ''
            metadata['paragraph_count'] = len(doc.paragraphs)
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            metadata['extraction_error'] = f"Document metadata extraction failed: {str(e)}"
        
        return metadata
    
    def _convert_gps_to_decimal(self, gps_coord, ref):
        """Convert GPS coordinates from EXIF format to decimal degrees"""
        try:
            degrees = float(gps_coord.values[0].num) / float(gps_coord.values[0].den)
            minutes = float(gps_coord.values[1].num) / float(gps_coord.values[1].den)
            seconds = float(gps_coord.values[2].num) / float(gps_coord.values[2].den)
            
            decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if ref and str(ref) in ['S', 'W']:
                decimal_degrees = -decimal_degrees
                
            return decimal_degrees
        except Exception:
            return None
    
    def _get_location_from_coords(self, coords: Tuple[float, float]) -> Optional[str]:
        """Convert GPS coordinates to human-readable location"""
        try:
            geolocator = Nominatim(user_agent="icc_evidence_tool")
            location = geolocator.reverse(f"{coords[0]}, {coords[1]}")
            return location.address if location else None
        except Exception:
            return None
    
    def _generate_content_hash(self, content: Any) -> str:
        """Generate content hash for deduplication"""
        if isinstance(content, str):
            content = content.encode()
        elif not isinstance(content, bytes):
            content = str(content).encode()
        
        return hashlib.sha256(content).hexdigest()
    
    def _calculate_evidence_quality(self, file_data: Dict[str, Any], 
                                   metadata: Dict[str, Any], 
                                   analysis: Dict[str, Any]) -> float:
        """Calculate evidence quality score"""
        base_score = 5.0
        
        # File size bonus (larger files generally higher quality)
        size_bonus = min(file_data.get('size', 0) / (1024 * 1024), 2.0)  # Max 2 points for size
        
        # Analysis confidence bonus
        confidence_bonus = analysis.get('confidence_score', 5.0) * 0.3  # Max 3 points
        
        # Metadata completeness bonus
        metadata_fields = len([k for k, v in metadata.items() if v and k != 'extraction_error'])
        metadata_bonus = min(metadata_fields * 0.2, 2.0)  # Max 2 points
        
        # Error penalty
        error_penalty = 1.0 if metadata.get('extraction_error') else 0.0
        
        total_score = min(base_score + size_bonus + confidence_bonus + metadata_bonus - error_penalty, 10.0)
        return round(max(total_score, 1.0), 2)


# Convenience functions for FastAPI integration
async def analyze_evidence_file(file_data: Dict[str, Any], 
                               keywords: Optional[str] = None,
                               incident_context: Optional[Dict[str, Any]] = None,
                               groq_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze a single evidence file
    
    Args:
        file_data: Dictionary with 'content', 'filename', 'type', 'size'
        keywords: Optional analysis keywords
        incident_context: Optional incident context
        groq_api_key: Optional Groq API key
        
    Returns:
        Analysis results for the file
    """
    orchestrator = ICCEvidenceOrchestrator(groq_api_key)
    results = await orchestrator.process_evidence_pipeline([file_data], keywords, incident_context)
    
    if results['evidence_analyses']:
        return results['evidence_analyses'][0]
    else:
        return {'error': 'Failed to analyze evidence file'}


async def analyze_evidence_batch(files: List[Dict[str, Any]], 
                                keywords: Optional[str] = None,
                                incident_context: Optional[Dict[str, Any]] = None,
                                submitter_info: Optional[Dict[str, Any]] = None,
                                groq_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze batch of evidence files and generate ICC case
    
    Args:
        files: List of file data dictionaries
        keywords: Optional analysis keywords  
        incident_context: Optional incident context
        submitter_info: Optional submitter information
        groq_api_key: Optional Groq API key
        
    Returns:
        Complete case analysis with ICC document
    """
    orchestrator = ICCEvidenceOrchestrator(groq_api_key)
    
    # Initialize case with context
    file_number = orchestrator.initialize_case(incident_context, submitter_info)
    
    # Process all evidence
    results = await orchestrator.process_evidence_pipeline(files, keywords, incident_context)
    
    # Generate ICC document
    icc_document = orchestrator.generate_icc_case_document()
    
    return {
        'file_number': file_number,
        'case_analysis': results,
        'icc_document': icc_document,
        'evidence_summary': orchestrator.get_evidence_summary()
    }
