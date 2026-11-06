"""
🇰🇪 ICC DOCUMENT INTELLIGENCE AGENT
Specialized agent for document analysis and entity extraction

RESPONSIBILITIES:
🔹 Extract key entities (dates, names, locations)
🔹 Legal document classification
🔹 Cross-reference with incident details
🔹 Generate evidence correlation matrix
🔹 Assess document authenticity and relevance
"""

import os
import io
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from groq import Groq
from dotenv import load_dotenv

# Document processing imports (with error handling)
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Load environment variables
load_dotenv()

class DocumentIntelligenceAgent:
    """Specialized agent for comprehensive document analysis"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_client = Groq(api_key=groq_api_key or os.getenv('GROQ_API_KEY'))
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Supported document formats
        self.supported_formats = {
            'pdf': ['.pdf'],
            'word': ['.doc', '.docx'],
            'text': ['.txt', '.rtf'],
            'json': ['.json']
        }
        
        # Entity categories for extraction
        self.entity_categories = {
            'people': ['names', 'individuals', 'witnesses', 'victims', 'perpetrators'],
            'organizations': ['groups', 'institutions', 'agencies', 'units'],
            'locations': ['places', 'addresses', 'coordinates', 'regions'],
            'dates': ['timestamps', 'events', 'incidents'],
            'weapons': ['firearms', 'explosives', 'tools'],
            'vehicles': ['cars', 'trucks', 'aircraft', 'vessels'],
            'legal_terms': ['charges', 'violations', 'statutes', 'procedures']
        }
    
    async def analyze_document_evidence(self, file_data: Dict[str, Any], 
                                      shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive document evidence analysis
        
        Args:
            file_data: File data with content, filename, type, metadata
            shared_context: Shared context from ICC case
            
        Returns:
            Comprehensive document analysis results
        """
        
        try:
            self.logger.info(f"Analyzing document: {file_data.get('filename', 'unknown')}")
            
            content = file_data.get('content', b'')
            filename = file_data.get('filename', 'unknown')
            file_type = file_data.get('type', '')
            metadata = file_data.get('metadata', {})
            
            # Extract text content from document
            text_content = self._extract_text_content(content, filename, file_type)
            
            if not text_content or len(text_content.strip()) < 10:
                return {
                    'agent_type': 'document_intelligence',
                    'error': 'No extractable text content found',
                    'processing_timestamp': datetime.now().isoformat()
                }
            
            # Perform comprehensive analysis
            entity_analysis = await self._extract_entities(text_content, shared_context)
            content_analysis = await self._analyze_content_structure(text_content, shared_context)
            legal_analysis = await self._assess_legal_relevance(text_content, entity_analysis, shared_context)
            authenticity_analysis = self._assess_document_authenticity(text_content, metadata)
            correlation_analysis = self._analyze_cross_references(entity_analysis, shared_context)
            
            # Compile comprehensive results
            analysis_result = {
                'agent_type': 'document_intelligence',
                'processing_timestamp': datetime.now().isoformat(),
                'filename': filename,
                'text_content': text_content,
                'content_length': len(text_content),
                'word_count': len(text_content.split()),
                'entity_analysis': entity_analysis,
                'content_analysis': content_analysis,
                'legal_analysis': legal_analysis,
                'authenticity_analysis': authenticity_analysis,
                'correlation_analysis': correlation_analysis,
                'document_quality': self._calculate_document_quality(text_content, entity_analysis, metadata),
                'recommendations': self._generate_document_recommendations(
                    entity_analysis, content_analysis, legal_analysis
                )
            }
            
            self.logger.info(f"Document analysis completed: {filename}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing document: {str(e)}")
            return {
                'agent_type': 'document_intelligence',
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    def _extract_text_content(self, content: bytes, filename: str, file_type: str) -> str:
        """Extract text content from various document formats"""
        
        file_ext = os.path.splitext(filename)[1].lower()
        
        try:
            # PDF extraction
            if file_type == 'application/pdf' or file_ext == '.pdf':
                if PDF_AVAILABLE:
                    return self._extract_pdf_text(content)
                else:
                    return "PDF processing not available - install PyMuPDF"
            
            # Word document extraction
            elif 'word' in file_type or file_ext in ['.doc', '.docx']:
                if DOCX_AVAILABLE:
                    return self._extract_docx_text(content)
                else:
                    return "Word processing not available - install python-docx"
            
            # Plain text
            elif file_type.startswith('text/') or file_ext in ['.txt', '.rtf']:
                return self._extract_plain_text(content)
            
            # JSON documents
            elif file_type == 'application/json' or file_ext == '.json':
                return self._extract_json_content(content)
            
            else:
                # Try as plain text
                return self._extract_plain_text(content)
                
        except Exception as e:
            self.logger.warning(f"Text extraction failed for {filename}: {str(e)}")
            return f"Text extraction failed: {str(e)}"
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                text += page.get_text() + "\n\n"
            
            pdf_doc.close()
            return text.strip()
            
        except Exception as e:
            return f"PDF extraction error: {str(e)}"
    
    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from Word document"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            doc = DocxDocument(temp_path)
            
            # Extract text from paragraphs
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
            
            # Clean up
            os.unlink(temp_path)
            
            return text.strip()
            
        except Exception as e:
            return f"Word document extraction error: {str(e)}"
    
    def _extract_plain_text(self, content: bytes) -> str:
        """Extract plain text content"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all fail, use error handling
            return content.decode('utf-8', errors='ignore')
            
        except Exception as e:
            return f"Text extraction error: {str(e)}"
    
    def _extract_json_content(self, content: bytes) -> str:
        """Extract content from JSON documents"""
        try:
            json_data = json.loads(content.decode('utf-8'))
            
            # Convert JSON to readable text
            if isinstance(json_data, dict):
                text_parts = []
                for key, value in json_data.items():
                    text_parts.append(f"{key}: {str(value)}")
                return "\n".join(text_parts)
            else:
                return str(json_data)
                
        except Exception as e:
            return f"JSON extraction error: {str(e)}"
    
    async def _extract_entities(self, text_content: str, shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities from document text using Groq"""
        
        case_context = shared_context.get('case_metadata', {})
        
        # Truncate text if too long for analysis
        analysis_text = text_content[:2000] if len(text_content) > 2000 else text_content
        
        prompt = f"""
        DOCUMENT ENTITY EXTRACTION FOR ICC EVIDENCE
        
        CASE CONTEXT:
        Incident: {case_context.get('incident_description', 'Human rights violation')}
        Location: {case_context.get('incident_location', 'Kenya')}
        Date: {case_context.get('incident_date', 'Unknown')}
        
        DOCUMENT TEXT TO ANALYZE:
        "{analysis_text}"
        
        Extract all relevant entities and information in JSON format:
        {{
            "people": {{
                "victims": ["victim", "names"],
                "perpetrators": ["perpetrator", "names"],
                "witnesses": ["witness", "names"],
                "officials": ["official", "names"],
                "other_persons": ["other", "people", "mentioned"]
            }},
            "organizations": {{
                "government_agencies": ["agencies", "mentioned"],
                "military_units": ["military", "groups"],
                "police_units": ["police", "units"],
                "civilian_groups": ["civilian", "organizations"],
                "international_bodies": ["UN", "ICC", "etc"]
            }},
            "locations": {{
                "incident_locations": ["places", "where", "incidents", "occurred"],
                "addresses": ["specific", "addresses"],
                "landmarks": ["notable", "landmarks"],
                "regions": ["broader", "geographic", "areas"],
                "coordinates": ["any", "GPS", "coordinates"]
            }},
            "temporal_information": {{
                "dates": ["2025-06-17", "specific", "dates"],
                "times": ["14:00", "specific", "times"],
                "duration": ["time", "periods"],
                "sequences": ["chronological", "events"]
            }},
            "weapons_equipment": {{
                "firearms": ["guns", "rifles", "pistols"],
                "vehicles": ["cars", "trucks", "aircraft"],
                "equipment": ["tools", "gear", "devices"],
                "ammunition": ["bullets", "explosives"]
            }},
            "legal_elements": {{
                "violations": ["human", "rights", "violations"],
                "laws_cited": ["legal", "statutes", "referenced"],
                "procedures": ["legal", "procedures", "mentioned"],
                "evidence_types": ["types", "of", "evidence", "mentioned"]
            }},
            "incident_details": {{
                "actions_described": ["specific", "actions", "taken"],
                "injuries": ["injuries", "described"],
                "damages": ["property", "damage"],
                "casualties": ["deaths", "or", "casualties"]
            }},
            "document_metadata": {{
                "document_type": "report|statement|testimony|official_document|other",
                "author": "document author if mentioned",
                "creation_date": "document date if mentioned",
                "purpose": "purpose of the document",
                "classification": "confidential|public|restricted|etc"
            }},
            "credibility_indicators": {{
                "specific_details": ["detailed", "specific", "information"],
                "verifiable_facts": ["facts", "that", "can", "be", "verified"],
                "inconsistencies": ["potential", "inconsistencies"],
                "corroborating_info": ["information", "that", "supports", "other", "evidence"]
            }}
        }}
        
        Focus on extracting specific, actionable information relevant to ICC proceedings.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert legal document analyst specializing in ICC evidence processing. Extract entities comprehensively and accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Clean and parse JSON
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            entities = json.loads(analysis_text)
            
            # Add entity counts for quick reference
            entities['entity_counts'] = self._count_entities(entities)
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {str(e)}")
            return {
                'error': f"Entity extraction failed: {str(e)}",
                'entity_counts': {'total': 0}
            }
    
    async def _analyze_content_structure(self, text_content: str, shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document structure and content quality"""
        
        # Basic text analysis
        lines = text_content.split('\n')
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in text_content.replace('\n', ' ').split('.') if s.strip()]
        words = text_content.split()
        
        structure_analysis = {
            'total_lines': len(lines),
            'total_paragraphs': len(paragraphs),
            'total_sentences': len(sentences),
            'total_words': len(words),
            'average_sentence_length': len(words) / len(sentences) if sentences else 0,
            'document_complexity': self._assess_complexity(text_content),
            'readability_score': self._calculate_readability(sentences, words),
            'structure_quality': self._assess_structure_quality(paragraphs, sentences)
        }
        
        # Enhanced content analysis with Groq
        try:
            prompt = f"""
            Analyze this document's content structure and quality:
            
            Text sample: "{text_content[:1000]}..."
            
            Document stats:
            - Words: {len(words)}
            - Sentences: {len(sentences)}
            - Paragraphs: {len(paragraphs)}
            
            Provide structure analysis in JSON format:
            {{
                "document_type": "testimony|report|statement|official_document|correspondence|other",
                "narrative_style": "formal|informal|legal|personal|technical",
                "organization_quality": 8.5,
                "coherence_score": 7.8,
                "detail_level": "high|medium|low",
                "objectivity": "objective|subjective|mixed",
                "emotional_content": "high|medium|low|none",
                "factual_density": 8.2,
                "legal_terminology": "extensive|moderate|minimal|none",
                "completeness": "complete|partial|fragmentary",
                "clarity_score": 8.0,
                "reliability_indicators": ["specific", "reliability", "factors"],
                "potential_issues": ["any", "issues", "identified"]
            }}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            structure_analysis.update(ai_analysis)
            
        except Exception as e:
            self.logger.warning(f"AI structure analysis failed: {str(e)}")
        
        return structure_analysis
    
    async def _assess_legal_relevance(self, text_content: str, entity_analysis: Dict[str, Any], 
                                    shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal relevance and evidentiary value"""
        
        case_context = shared_context.get('case_metadata', {})
        
        # Calculate base relevance score
        relevance_score = 5.0
        relevance_factors = []
        
        # Check entity relevance
        entities = entity_analysis
        
        # People relevance
        people = entities.get('people', {})
        if people.get('victims') or people.get('perpetrators'):
            relevance_score += 2.0
            relevance_factors.append("Key persons identified")
        
        if people.get('witnesses'):
            relevance_score += 1.5
            relevance_factors.append("Witnesses identified")
        
        # Location relevance
        locations = entities.get('locations', {})
        if locations.get('incident_locations'):
            relevance_score += 2.0
            relevance_factors.append("Incident locations documented")
        
        # Temporal relevance
        temporal = entities.get('temporal_information', {})
        if temporal.get('dates') or temporal.get('times'):
            relevance_score += 1.5
            relevance_factors.append("Temporal information provided")
        
        # Legal elements
        legal = entities.get('legal_elements', {})
        if legal.get('violations'):
            relevance_score += 2.5
            relevance_factors.append("Legal violations documented")
        
        # Incident details
        incident = entities.get('incident_details', {})
        if incident.get('injuries') or incident.get('casualties'):
            relevance_score += 2.0
            relevance_factors.append("Harm documented")
        
        # Weapons/equipment
        weapons = entities.get('weapons_equipment', {})
        if weapons.get('firearms') or weapons.get('vehicles'):
            relevance_score += 1.5
            relevance_factors.append("Weapons/equipment documented")
        
        # Normalize score
        relevance_score = max(1.0, min(10.0, relevance_score))
        
        # Enhanced legal analysis with Groq
        try:
            prompt = f"""
            Assess the legal relevance of this document for ICC proceedings:
            
            Document excerpt: "{text_content[:1500]}..."
            
            Case context: {case_context.get('incident_description', 'Human rights violation')}
            
            Provide legal assessment in JSON format:
            {{
                "legal_relevance_score": 8.5,
                "evidence_type": "direct|circumstantial|corroborative|background",
                "admissibility_likelihood": "high|medium|low",
                "legal_weight": "strong|moderate|weak",
                "icc_jurisdiction": "clearly_within|likely_within|questionable|outside",
                "evidence_category": "testimony|documentation|expert_opinion|physical_evidence",
                "procedural_considerations": ["chain", "of", "custody", "issues"],
                "strengths": ["legal", "strengths", "of", "document"],
                "weaknesses": ["potential", "legal", "weaknesses"],
                "corroboration_needed": ["what", "additional", "evidence", "needed"],
                "legal_strategy": ["how", "to", "use", "this", "evidence"]
            }}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000
            )
            
            ai_legal_analysis = json.loads(response.choices[0].message.content)
            
            return {
                'calculated_relevance_score': relevance_score,
                'relevance_factors': relevance_factors,
                'ai_legal_analysis': ai_legal_analysis,
                'final_relevance_score': max(relevance_score, ai_legal_analysis.get('legal_relevance_score', relevance_score)),
                'evidence_strength': 'high' if relevance_score > 7.5 else 'medium' if relevance_score > 5.0 else 'low'
            }
            
        except Exception as e:
            self.logger.warning(f"AI legal analysis failed: {str(e)}")
            return {
                'calculated_relevance_score': relevance_score,
                'relevance_factors': relevance_factors,
                'final_relevance_score': relevance_score,
                'evidence_strength': 'high' if relevance_score > 7.5 else 'medium' if relevance_score > 5.0 else 'low'
            }
    
    def _assess_document_authenticity(self, text_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess document authenticity and integrity"""
        
        authenticity_score = 5.0
        authenticity_factors = []
        concerns = []
        
        # Metadata indicators
        if metadata.get('creation_date'):
            authenticity_score += 1.0
            authenticity_factors.append("Creation date available")
        
        if metadata.get('author'):
            authenticity_score += 1.0
            authenticity_factors.append("Author information available")
        
        # Content analysis
        if len(text_content) > 500:
            authenticity_score += 0.5
            authenticity_factors.append("Substantial content")
        
        # Check for unusual patterns (simple heuristics)
        repeated_phrases = self._find_repeated_phrases(text_content)
        if len(repeated_phrases) > 5:
            authenticity_score -= 1.0
            concerns.append("Excessive repeated phrases detected")
        
        # Check text consistency
        consistency_score = self._assess_text_consistency(text_content)
        authenticity_score += consistency_score * 2.0
        
        if consistency_score > 0.7:
            authenticity_factors.append("High text consistency")
        elif consistency_score < 0.3:
            concerns.append("Low text consistency")
        
        # Normalize score
        authenticity_score = max(1.0, min(10.0, authenticity_score))
        
        return {
            'authenticity_score': round(authenticity_score, 2),
            'authenticity_level': 'high' if authenticity_score > 7.0 else 'medium' if authenticity_score > 4.0 else 'low',
            'authenticity_factors': authenticity_factors,
            'concerns': concerns,
            'integrity_assessment': 'likely_authentic' if authenticity_score > 6.0 else 'requires_verification'
        }
    
    def _analyze_cross_references(self, entity_analysis: Dict[str, Any], shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cross-references with other evidence"""
        
        case_context = shared_context.get('case_metadata', {})
        evidence_summary = shared_context.get('evidence_summary', {})
        
        cross_references = {
            'location_matches': [],
            'temporal_matches': [],
            'person_matches': [],
            'incident_matches': [],
            'correlation_score': 0.0
        }
        
        # Location cross-references
        doc_locations = entity_analysis.get('locations', {}).get('incident_locations', [])
        case_location = case_context.get('incident_location', '')
        
        for location in doc_locations:
            if case_location and case_location.lower() in location.lower():
                cross_references['location_matches'].append(location)
        
        # Temporal cross-references
        doc_dates = entity_analysis.get('temporal_information', {}).get('dates', [])
        case_date = case_context.get('incident_date', '')
        
        for date in doc_dates:
            if case_date and case_date in date:
                cross_references['temporal_matches'].append(date)
        
        # Person cross-references (simplified)
        doc_people = entity_analysis.get('people', {})
        all_doc_people = []
        for category, people_list in doc_people.items():
            if isinstance(people_list, list):
                all_doc_people.extend(people_list)
        
        cross_references['person_matches'] = all_doc_people  # Simplified
        
        # Calculate correlation score
        correlation_score = 0.0
        if cross_references['location_matches']:
            correlation_score += 3.0
        if cross_references['temporal_matches']:
            correlation_score += 3.0
        if cross_references['person_matches']:
            correlation_score += 2.0
        
        # Incident description correlation
        incident_details = entity_analysis.get('incident_details', {})
        if incident_details.get('actions_described') or incident_details.get('injuries'):
            correlation_score += 2.0
            cross_references['incident_matches'] = ['Incident details match case context']
        
        cross_references['correlation_score'] = min(correlation_score, 10.0)
        
        return cross_references
    
    # Helper methods
    def _count_entities(self, entities: Dict[str, Any]) -> Dict[str, int]:
        """Count entities by category"""
        counts = {'total': 0}
        
        for category, data in entities.items():
            if isinstance(data, dict):
                category_count = 0
                for subcategory, items in data.items():
                    if isinstance(items, list):
                        category_count += len(items)
                counts[category] = category_count
                counts['total'] += category_count
        
        return counts
    
    def _assess_complexity(self, text: str) -> float:
        """Assess document complexity"""
        # Simple complexity metrics
        words = text.split()
        unique_words = set(words)
        
        if not words:
            return 0.0
        
        # Vocabulary diversity
        vocabulary_ratio = len(unique_words) / len(words)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence complexity (rough estimate)
        sentences = [s for s in text.split('.') if s.strip()]
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Combine metrics
        complexity = (vocabulary_ratio * 3 + avg_word_length * 0.5 + avg_sentence_length * 0.1)
        return min(complexity, 10.0)
    
    def _calculate_readability(self, sentences: List[str], words: List[str]) -> float:
        """Calculate readability score (simplified)"""
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (approximation)
        syllable_count = sum(max(1, len([c for c in word if c.lower() in 'aeiou'])) for word in words)
        avg_syllables = syllable_count / len(words)
        
        # Simplified Flesch Reading Ease approximation
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        
        # Normalize to 0-10 scale
        return max(0, min(10, readability / 10))
    
    def _assess_structure_quality(self, paragraphs: List[str], sentences: List[str]) -> float:
        """Assess document structure quality"""
        if not paragraphs or not sentences:
            return 0.0
        
        # Check paragraph distribution
        avg_sentences_per_paragraph = len(sentences) / len(paragraphs)
        
        # Ideal range is 3-8 sentences per paragraph
        if 3 <= avg_sentences_per_paragraph <= 8:
            structure_score = 8.0
        elif 2 <= avg_sentences_per_paragraph <= 10:
            structure_score = 6.0
        else:
            structure_score = 4.0
        
        # Check for very short or very long paragraphs
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths)
        
        if 50 <= avg_paragraph_length <= 200:
            structure_score += 1.0
        elif avg_paragraph_length < 20 or avg_paragraph_length > 300:
            structure_score -= 1.0
        
        return max(1.0, min(10.0, structure_score))
    
    def _find_repeated_phrases(self, text: str) -> List[str]:
        """Find repeated phrases in text"""
        words = text.split()
        repeated_phrases = []
        
        # Check for 3-word phrases that repeat
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if text.count(phrase) > 1 and phrase not in repeated_phrases:
                repeated_phrases.append(phrase)
        
        return repeated_phrases
    
    def _assess_text_consistency(self, text: str) -> float:
        """Assess text consistency (simple heuristic)"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 3:
            return 0.5
        
        # Check sentence length consistency
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Calculate coefficient of variation
        if avg_length == 0:
            return 0.0
        
        variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / avg_length
        
        # Lower variation indicates higher consistency
        consistency = max(0, 1 - coefficient_of_variation)
        
        return consistency
    
    def _calculate_document_quality(self, text_content: str, entity_analysis: Dict[str, Any], 
                                   metadata: Dict[str, Any]) -> float:
        """Calculate overall document quality score"""
        base_score = 5.0
        
        # Content length bonus
        word_count = len(text_content.split())
        if word_count > 500:
            base_score += 2.0
        elif word_count > 200:
            base_score += 1.0
        elif word_count < 50:
            base_score -= 1.0
        
        # Entity richness bonus
        entity_counts = entity_analysis.get('entity_counts', {})
        total_entities = entity_counts.get('total', 0)
        if total_entities > 20:
            base_score += 1.5
        elif total_entities > 10:
            base_score += 1.0
        
        # Metadata completeness bonus
        metadata_fields = len([v for v in metadata.values() if v])
        if metadata_fields > 5:
            base_score += 1.0
        elif metadata_fields > 3:
            base_score += 0.5
        
        # Error penalty
        if 'error' in entity_analysis:
            base_score -= 2.0
        
        return round(max(1.0, min(10.0, base_score)), 2)
    
    def _generate_document_recommendations(self, entity_analysis: Dict[str, Any], 
                                         content_analysis: Dict[str, Any],
                                         legal_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for document evidence"""
        recommendations = []
        
        # Legal recommendations
        legal_strength = legal_analysis.get('evidence_strength', 'medium')
        if legal_strength == 'high':
            recommendations.append("High-value document - prioritize for ICC submission")
        elif legal_strength == 'low':
            recommendations.append("Limited legal value - use as supporting documentation")
        
        # Entity-based recommendations
        entity_counts = entity_analysis.get('entity_counts', {})
        if entity_counts.get('people', 0) > 5:
            recommendations.append("Multiple persons identified - cross-reference with witness lists")
        
        if entity_counts.get('locations', 0) > 3:
            recommendations.append("Multiple locations mentioned - verify with geospatial analysis")
        
        # Content quality recommendations
        content_quality = content_analysis.get('organization_quality', 5.0)
        if content_quality < 6.0:
            recommendations.append("Document structure could be improved - consider editing for clarity")
        
        # Authenticity recommendations
        if entity_analysis.get('error'):
            recommendations.append("Entity extraction failed - manual review required")
        
        # Correlation recommendations
        correlation_score = legal_analysis.get('calculated_relevance_score', 5.0)
        if correlation_score > 7.0:
            recommendations.append("Strong correlation with case - include in primary evidence package")
        
        return recommendations
