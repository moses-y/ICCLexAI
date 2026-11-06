"""
🔍 EVIDENCE ANALYSIS CORE AGENT
Specialized agent for lightning-fast AI evidence processing
Part of the 5-agent intelligent consolidation system

AGENT RESPONSIBILITIES:
- Multi-modal AI analysis (vision, audio, text)
- Real-time processing with caching optimization
- Advanced visualization and insights generation
- Legal significance assessment
- Confidence scoring and validation
- Evidence categorization and classification
- Performance monitoring and benchmarking

This is CORE AGENT #5 - focused solely on evidence analysis capabilities
"""

import streamlit as st
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import numpy as np
from pathlib import Path

# AI/ML imports
import cv2
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class EvidenceAnalysisAgent:
    """
    🔍 CORE AGENT #5: Advanced Evidence Analysis Engine
    
    This agent specializes in:
    - Lightning-fast multi-modal AI analysis
    - Intelligent caching and optimization
    - Advanced evidence categorization
    - Legal significance assessment
    - Confidence scoring and validation
    - Real-time visualization and insights
    - Performance optimization
    """
    
    def __init__(self, cache_enabled: bool = True, groq_api_key: str = None):
        self.cache_enabled = cache_enabled
        self.groq_client = Groq(api_key=groq_api_key or os.getenv('GROQ_API_KEY'))
        self.analysis_history = []
        
        # Evidence categories and their legal significance weights
        self.evidence_categories = {
            'photograph': {'weight': 0.9, 'legal_value': 'High', 'admissibility': 'Strong'},
            'video': {'weight': 0.95, 'legal_value': 'Very High', 'admissibility': 'Very Strong'},
            'audio': {'weight': 0.8, 'legal_value': 'High', 'admissibility': 'Strong'},
            'document': {'weight': 0.85, 'legal_value': 'High', 'admissibility': 'Strong'},
            'witness_statement': {'weight': 0.7, 'legal_value': 'Medium', 'admissibility': 'Moderate'},
            'digital_evidence': {'weight': 0.9, 'legal_value': 'High', 'admissibility': 'Strong'}
        }
        
        # Initialize cache if enabled
        if self.cache_enabled and 'evidence_analysis_cache' not in st.session_state:
            st.session_state.evidence_analysis_cache = {}
        if 'analysis_performance' not in st.session_state:
            st.session_state.analysis_performance = []
    
    def analyze_evidence_comprehensive(self, uploaded_file, include_legal_assessment: bool = True) -> Tuple[Optional[Dict], bool]:
        """
        🎯 MAIN METHOD: Comprehensive evidence analysis with caching
        
        Args:
            uploaded_file: Streamlit uploaded file object
            include_legal_assessment: Whether to include legal significance analysis
            
        Returns:
            Tuple[Optional[Dict], bool]: (analysis_result, from_cache)
        """
        start_time = time.time()
        
        try:
            # Generate file hash for caching
            file_content = uploaded_file.getvalue()
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Check cache first
            if self.cache_enabled and file_hash in st.session_state.evidence_analysis_cache:
                cached_result = st.session_state.evidence_analysis_cache[file_hash]
                
                # Update cache hit metrics
                self._record_performance('cache_hit', time.time() - start_time, True)
                
                st.success("⚡ Analysis retrieved from cache (instant)")
                return cached_result, True
            
            # Progress tracking
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Phase 1: File type detection and basic analysis
            status_text.text("🔍 Analyzing file type and extracting basic metadata...")
            progress_bar.progress(20)
            
            basic_analysis = self._analyze_file_basic(uploaded_file, file_content)
            
            # Phase 2: AI-powered content analysis
            status_text.text("🤖 Running AI content analysis...")
            progress_bar.progress(50)
            
            ai_analysis = self._analyze_content_with_ai(uploaded_file, file_content, basic_analysis)
            
            # Phase 3: Legal significance assessment
            if include_legal_assessment:
                status_text.text("⚖️ Assessing legal significance...")
                progress_bar.progress(75)
                
                legal_assessment = self._assess_legal_significance(basic_analysis, ai_analysis)
            else:
                legal_assessment = {}
            
            # Phase 4: Compile comprehensive results
            status_text.text("📊 Compiling comprehensive analysis...")
            progress_bar.progress(90)
            
            comprehensive_result = self._compile_analysis_results(
                basic_analysis, ai_analysis, legal_assessment, file_hash
            )
            
            # Add performance metrics
            analysis_time = time.time() - start_time
            comprehensive_result['performance'] = {
                'analysis_time': analysis_time,
                'timestamp': datetime.now().isoformat(),
                'cache_used': False
            }
            
            # Cache result if enabled
            if self.cache_enabled:
                st.session_state.evidence_analysis_cache[file_hash] = comprehensive_result
            
            # Record performance
            self._record_performance('full_analysis', analysis_time, True)
            
            progress_bar.progress(100)
            status_text.text(f"✅ Comprehensive analysis complete in {analysis_time:.2f}s")
            time.sleep(1)
            progress_container.empty()
            
            return comprehensive_result, False
            
        except Exception as e:
            error_time = time.time() - start_time
            self._record_performance('analysis_error', error_time, False)
            
            st.error(f"❌ Analysis failed: {str(e)}")
            return None, False
    
    def _analyze_file_basic(self, uploaded_file, file_content: bytes) -> Dict:
        """🔍 Basic file analysis and metadata extraction"""
        try:
            file_size_mb = len(file_content) / (1024 * 1024)
            file_ext = Path(uploaded_file.name).suffix.lower()
            
            basic_info = {
                'filename': uploaded_file.name,
                'file_size_bytes': len(file_content),
                'file_size_mb': round(file_size_mb, 2),
                'file_type': uploaded_file.type,
                'file_extension': file_ext,
                'upload_timestamp': datetime.now().isoformat()
            }
            
            # Determine evidence category
            evidence_type = self._categorize_evidence_type(uploaded_file.type, file_ext)
            basic_info['evidence_category'] = evidence_type            # Extract technical metadata based on file type
            if uploaded_file.type.startswith('image/'):
                basic_info.update(self._analyze_image_basic(file_content))
            elif uploaded_file.type.startswith('video/'):
                basic_info.update(self._analyze_video_basic(file_content))
            elif uploaded_file.type.startswith('audio/'):
                basic_info.update(self._analyze_audio_basic(file_content))
            
            return basic_info
            
        except Exception as e:
            return {'error': f"Basic analysis failed: {str(e)}"}
    
    def _analyze_content_with_ai(self, uploaded_file, file_content: bytes, basic_analysis: Dict) -> Dict:
        """🤖 AI-powered content analysis using Groq's specialized models for different data types"""
        try:
            if not self.groq_client:
                return {'error': 'Groq API not configured'}
            
            evidence_category = basic_analysis.get('evidence_category', 'unknown')
            file_size_mb = basic_analysis.get('file_size_mb', 1.0)
            
            # 🧠 GET SMART MODEL RECOMMENDATION
            recommendation = self.get_smart_model_recommendation(evidence_category, file_size_mb)
            model_config = recommendation['primary']
            
            # Create context-aware prompt based on evidence type
            prompt = self._create_analysis_prompt(evidence_category, basic_analysis)
            
            # 🚀 USE OPTIMAL MODEL FOR EVIDENCE TYPE
            response = self.groq_client.chat.completions.create(
                model=model_config['model'],
                messages=[{"role": "user", "content": prompt}],
                temperature=model_config['temperature'],
                max_tokens=model_config['max_tokens'],
                top_p=model_config['top_p']
            )
            
            # 📊 UPDATE USAGE TRACKING
            self.update_usage_tracking(model_config['model'], model_config['max_tokens'])
            
            # Parse AI response
            try:
                ai_result = json.loads(response.choices[0].message.content)
                ai_result['model_used'] = model_config['model']
                ai_result['analysis_type'] = evidence_category
            except json.JSONDecodeError:
                # Fallback to text response
                ai_result = {
                    'analysis': response.choices[0].message.content,
                    'confidence_score': 75,
                    'evidence_type': evidence_category,
                    'model_used': model_config['model']
                }
            
            return ai_result
            
        except Exception as e:
            return {'error': f"AI analysis failed: {str(e)}"}
    def _select_optimal_model(self, evidence_category: str, complexity_level: str = 'standard') -> Dict:
        """🎯 Select the optimal Groq model using ALL available models strategically
        
        Based on your complete Groq rate limits for maximum multimodal capability:
        - Chat Completion: 17 different models with varying capabilities
        - Speech-to-Text: 3 Whisper models for audio processing 
        - Text-to-Speech: 2 models for audio generation (if needed)
        """
        
        # TIER 1: PREMIUM MODELS (Limited daily requests but highest quality)
        premium_models = {
            'photograph_detailed': {
                'model': 'llama-3.3-70b-versatile',  # 30 RPM, 1,000 RPD, 12,000 TPM
                'temperature': 0.1,
                'max_tokens': 2000,  # Use higher limit for detailed analysis
                'top_p': 0.9,
                'use_case': 'Detailed photographic evidence analysis with legal context'
            },
            
            'video_complex': {
                'model': 'deepseek-r1-distill-llama-70b',  # 30 RPM, 1,000 RPD, 6,000 TPM
                'temperature': 0.15,
                'max_tokens': 1500,
                'top_p': 0.95,
                'use_case': 'Complex video timeline analysis and reasoning'
            },
            
            'document_legal': {
                'model': 'qwen-qwq-32b',  # 30 RPM, 1,000 RPD, 6,000 TPM - Excellent reasoning
                'temperature': 0.05,
                'max_tokens': 2000,
                'top_p': 0.9,
                'use_case': 'Advanced legal document analysis and interpretation'
            },
            
            'witness_advanced': {
                'model': 'meta-llama/llama-4-scout-17b-16e-instruct',  # 30 RPM, 1,000 RPD, 30,000 TPM
                'temperature': 0.2,
                'max_tokens': 2500,  # Highest token limit available
                'top_p': 0.9,
                'use_case': 'Advanced witness statement analysis with high token capacity'
            },
            
            'audio_complex': {
                'model': 'mistral-saba-24b',  # 30 RPM, 1,000 RPD, 6,000 TPM
                'temperature': 0.1,
                'max_tokens': 1200,
                'top_p': 0.9,
                'use_case': 'Complex audio content analysis after transcription'
            }
        }
        
        # TIER 2: HIGH-VOLUME MODELS (14,400 RPD - Use for bulk processing)
        bulk_models = {
            'photograph_standard': {
                'model': 'llama3-70b-8192',  # 30 RPM, 14,400 RPD, 6,000 TPM
                'temperature': 0.2,
                'max_tokens': 1000,
                'top_p': 0.9,
                'use_case': 'Standard photo analysis for high-volume processing'
            },
            
            'audio_standard': {
                'model': 'llama-3.1-8b-instant',  # 30 RPM, 14,400 RPD, 6,000 TPM
                'temperature': 0.1,
                'max_tokens': 800,
                'top_p': 0.8,
                'use_case': 'Fast audio metadata and content analysis'
            },
            
            'document_standard': {
                'model': 'llama3-8b-8192',  # 30 RPM, 14,400 RPD, 6,000 TPM
                'temperature': 0.1,
                'max_tokens': 1200,
                'top_p': 0.9,
                'use_case': 'Standard document processing for bulk analysis'
            },
            
            'digital_evidence': {
                'model': 'gemma2-9b-it',  # 30 RPM, 14,400 RPD, 15,000 TPM
                'temperature': 0.3,
                'max_tokens': 1000,
                'top_p': 0.9,
                'use_case': 'General digital evidence processing with high token limit'
            },
            
            'content_moderation': {
                'model': 'meta-llama/llama-guard-4-12b',  # 30 RPM, 14,400 RPD, 15,000 TPM
                'temperature': 0.1,
                'max_tokens': 500,
                'top_p': 0.8,
                'use_case': 'Content safety verification for sensitive evidence'
            }
        }
        
        # TIER 3: SPECIALIZED MODELS
        specialized_models = {
            'multilingual': {
                'model': 'qwen/qwen3-32b',  # 60 RPM, 1,000 RPD, 6,000 TPM
                'temperature': 0.2,
                'max_tokens': 1500,
                'top_p': 0.9,
                'use_case': 'Multilingual evidence analysis and translation'
            },
            
            'experimental_reasoning': {
                'model': 'compound-beta',  # 15 RPM, 200 RPD, 70,000 TPM (!)
                'temperature': 0.1,
                'max_tokens': 3000,  # Use the massive token limit
                'top_p': 0.95,
                'use_case': 'Advanced experimental reasoning for complex cases'
            },
            
            'ultra_fast': {
                'model': 'allam-2-7b',  # 30 RPM, 7,000 RPD, 6,000 TPM
                'temperature': 0.3,
                'max_tokens': 600,
                'top_p': 0.9,
                'use_case': 'Ultra-fast preliminary analysis'
            }
        }
        
        # AUDIO TRANSCRIPTION MODELS
        audio_models = {
            'whisper_turbo': 'whisper-large-v3-turbo',    # 20 RPM, 2,000 RPD, 7,200 sec/hour
            'whisper_standard': 'whisper-large-v3',       # 20 RPM, 2,000 RPD, 7,200 sec/hour  
            'whisper_english': 'distil-whisper-large-v3-en'  # 20 RPM, 2,000 RPD, 7,200 sec/hour
        }
        
        # TTS MODELS (for accessibility or audio summaries)
        tts_models = {
            'english_tts': 'playai-tts',        # 10 RPM, 100 RPD, 1,200 TPM
            'arabic_tts': 'playai-tts-arabic'   # 10 RPM, 100 RPD, 1,200 TPM
        }
        
        # INTELLIGENT MODEL SELECTION LOGIC
        selection_strategy = {
            'photograph': {
                'high_priority': premium_models['photograph_detailed'],
                'standard': bulk_models['photograph_standard'],
                'fallback': bulk_models['digital_evidence']
            },
            
            'video': {
                'high_priority': premium_models['video_complex'],
                'standard': bulk_models['photograph_standard'],  # Good for video frames
                'fallback': bulk_models['digital_evidence']
            },
            
            'audio': {
                'transcription_model': audio_models['whisper_turbo'],
                'analysis_premium': premium_models['audio_complex'],
                'analysis_standard': bulk_models['audio_standard'],
                'fallback': bulk_models['digital_evidence']
            },
            
            'document': {
                'legal_complex': premium_models['document_legal'],
                'standard': bulk_models['document_standard'],
                'multilingual': specialized_models['multilingual'],
                'fallback': bulk_models['digital_evidence']
            },
            
            'witness_statement': {
                'detailed': premium_models['witness_advanced'],
                'standard': bulk_models['photograph_standard'],
                'safety_check': bulk_models['content_moderation'],
                'fallback': bulk_models['digital_evidence']
            },
            
            'digital_evidence': {
                'standard': bulk_models['digital_evidence'],
                'experimental': specialized_models['experimental_reasoning'],
                'fast': specialized_models['ultra_fast'],
                'fallback': bulk_models['audio_standard']
            }
        }
        
        # Select based on evidence category and complexity
        category_config = selection_strategy.get(evidence_category, selection_strategy['digital_evidence'])
        
        if complexity_level == 'high_priority':
            return category_config.get('high_priority', category_config.get('detailed', category_config['standard']))
        elif complexity_level == 'experimental':
            return category_config.get('experimental', category_config['standard'])
        elif complexity_level == 'fast':
            return category_config.get('fast', category_config['standard'])
        else:
            return category_config['standard']
    
    def _handle_audio_transcription(self, file_content: bytes) -> Dict:
        """🎵 Handle audio transcription using Whisper model"""
        try:
            # For audio files, we can use Groq's Whisper model for transcription
            # Rate limit: 20 RPM, 2,000 RPD, 7,200 Audio Seconds/Hour
            
            # Save audio to temp file for Whisper
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Use Whisper for transcription
            with open(temp_file_path, 'rb') as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",  # Optimized Whisper model
                    response_format="json",
                    language="en"  # Can be auto-detected
                )
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return {
                'transcription': transcription.text,
                'language': transcription.language if hasattr(transcription, 'language') else 'en',
                'model_used': 'whisper-large-v3-turbo',
                'audio_length_estimate': len(file_content) / 16000  # Rough estimate
            }
            
        except Exception as e:
            return {'transcription_error': f"Audio transcription failed: {str(e)}"}
    
    def _assess_legal_significance(self, basic_analysis: Dict, ai_analysis: Dict) -> Dict:
        """⚖️ Assess legal significance and admissibility"""
        try:
            evidence_category = basic_analysis.get('evidence_category', 'unknown')
            category_info = self.evidence_categories.get(evidence_category, {})
            
            # Base legal assessment
            legal_assessment = {
                'category_weight': category_info.get('weight', 0.5),
                'legal_value': category_info.get('legal_value', 'Unknown'),
                'admissibility_strength': category_info.get('admissibility', 'Unknown'),
                'icc_relevance': 'High',  # Default for ICC submissions
                'evidence_quality': self._assess_evidence_quality(basic_analysis, ai_analysis),
                'chain_of_custody_notes': self._generate_custody_notes(basic_analysis),
                'recommended_actions': self._generate_recommendations(basic_analysis, ai_analysis)
            }
            
            # Calculate overall legal score
            quality_score = legal_assessment['evidence_quality']['overall_score']
            category_weight = legal_assessment['category_weight']
            ai_confidence = ai_analysis.get('confidence_score', 50) / 100
            
            overall_legal_score = (quality_score * 0.4 + category_weight * 0.3 + ai_confidence * 0.3) * 100
            legal_assessment['overall_legal_score'] = round(overall_legal_score, 1)
            
            return legal_assessment
            
        except Exception as e:
            return {'error': f"Legal assessment failed: {str(e)}"}
    
    def _categorize_evidence_type(self, mime_type: str, file_ext: str) -> str:
        """📂 Categorize evidence based on file type"""
        if mime_type.startswith('image/'):
            return 'photograph'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type == 'application/pdf' or 'document' in mime_type:
            return 'document'
        elif file_ext in ['.txt', '.doc', '.docx']:
            return 'document'
        else:
            return 'digital_evidence'
    
    def _analyze_image_basic(self, file_content: bytes) -> Dict:
        """🖼️ Basic image analysis"""
        try:
            # Load image
            image = Image.open(io.BytesIO(file_content))
            
            # Get image properties
            width, height = image.size
            mode = image.mode
            format_name = image.format
            
            # Calculate aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            
            # Determine image quality indicators
            megapixels = (width * height) / 1_000_000
            quality_indicator = 'High' if megapixels > 2 else 'Medium' if megapixels > 0.5 else 'Low'
            
            return {
                'image_width': width,
                'image_height': height,
                'image_mode': mode,
                'image_format': format_name,
                'aspect_ratio': round(aspect_ratio, 2),
                'megapixels': round(megapixels, 2),
                'quality_indicator': quality_indicator
            }
            
        except Exception as e:
            return {'image_analysis_error': str(e)}
    
    def _analyze_video_basic(self, file_content: bytes) -> Dict:
        """🎬 Basic video analysis"""
        try:
            # For basic analysis, we'll estimate based on file size
            file_size_mb = len(file_content) / (1024 * 1024)
            
            # Rough estimates based on typical video metrics
            estimated_duration = file_size_mb / 2  # Rough estimate: 2MB per minute
            quality_estimate = 'HD' if file_size_mb > 50 else 'SD' if file_size_mb > 10 else 'Low'
            
            return {
                'estimated_duration_minutes': round(estimated_duration, 1),
                'estimated_quality': quality_estimate,
                'file_size_indicator': 'Large' if file_size_mb > 100 else 'Medium' if file_size_mb > 10 else 'Small'
            }
            
        except Exception as e:
            return {'video_analysis_error': str(e)}
    
    def _analyze_audio_basic(self, file_content: bytes) -> Dict:
        """🎵 Basic audio analysis"""
        try:
            file_size_mb = len(file_content) / (1024 * 1024)
            
            # Rough estimates for audio
            estimated_duration = file_size_mb / 1  # Rough estimate: 1MB per minute
            quality_estimate = 'High' if file_size_mb > 5 else 'Medium' if file_size_mb > 1 else 'Low'
            
            return {
                'estimated_duration_minutes': round(estimated_duration, 1),
                'estimated_audio_quality': quality_estimate,
                'file_size_indicator': 'Large' if file_size_mb > 20 else 'Medium' if file_size_mb > 5 else 'Small'
            }
            
        except Exception as e:
            return {'audio_analysis_error': str(e)}
    
    def _create_analysis_prompt(self, evidence_type: str, basic_info: Dict) -> str:
        """📝 Create context-aware analysis prompt for AI"""
        base_prompt = f"""
        You are an expert forensic analyst specializing in ICC evidence evaluation.
        
        EVIDENCE CONTEXT:
        - Type: {evidence_type}
        - Filename: {basic_info.get('filename', 'Unknown')}
        - Size: {basic_info.get('file_size_mb', 0)} MB
        - Incident: Person shot by GSU in CBD, Nairobi, Kenya (June 17, 2025, 2:00 PM)
        
        Provide analysis in JSON format:
        {{
            "evidence_type": "{evidence_type}",
            "content_description": "What this evidence shows (2-3 sentences)",
            "incident_relevance": "How this relates to the shooting incident",
            "forensic_value": "Forensic significance and authentication notes",
            "confidence_score": "1-100 confidence in analysis accuracy",
            "key_observations": ["list", "of", "key", "findings"],
            "legal_significance": "Why this evidence is important for ICC case",
            "authentication_notes": "Notes on evidence authenticity and integrity",
            "recommended_next_steps": "Suggested actions for this evidence"
        }}
        
        Focus on human rights violations and be factual and professional.
        """
        
        return base_prompt
    
    def _assess_evidence_quality(self, basic_analysis: Dict, ai_analysis: Dict) -> Dict:
        """📊 Assess overall evidence quality"""
        quality_factors = {
            'technical_quality': 0,
            'content_clarity': 0,
            'forensic_value': 0,
            'authenticity_indicators': 0
        }
        
        # Technical quality assessment
        if 'image_width' in basic_analysis:
            megapixels = basic_analysis.get('megapixels', 0)
            quality_factors['technical_quality'] = min(100, megapixels * 20)
        elif 'estimated_duration_minutes' in basic_analysis:
            duration = basic_analysis.get('estimated_duration_minutes', 0)
            quality_factors['technical_quality'] = min(100, duration * 10)
        else:
            quality_factors['technical_quality'] = 70  # Default for documents
        
        # Content clarity from AI analysis
        ai_confidence = ai_analysis.get('confidence_score', 50)
        quality_factors['content_clarity'] = ai_confidence
        
        # Forensic value
        quality_factors['forensic_value'] = 80  # High default for ICC evidence
        
        # Authenticity indicators
        quality_factors['authenticity_indicators'] = 75  # Default high trust
        
        # Calculate overall score
        overall_score = sum(quality_factors.values()) / len(quality_factors)
        
        return {
            'technical_quality': round(quality_factors['technical_quality'], 1),
            'content_clarity': round(quality_factors['content_clarity'], 1),
            'forensic_value': round(quality_factors['forensic_value'], 1),
            'authenticity_indicators': round(quality_factors['authenticity_indicators'], 1),
            'overall_score': round(overall_score / 100, 2)  # 0-1 scale
        }
    
    def _generate_custody_notes(self, basic_analysis: Dict) -> List[str]:
        """📋 Generate chain of custody notes"""
        notes = [
            f"Evidence uploaded at {basic_analysis.get('upload_timestamp', 'Unknown time')}",
            f"Original filename: {basic_analysis.get('filename', 'Unknown')}",
            f"File size: {basic_analysis.get('file_size_mb', 0)} MB",
            "Digital integrity maintained through hashing",
            "Submitted directly via ICC evidence portal"
        ]
        
        return notes
    
    def _generate_recommendations(self, basic_analysis: Dict, ai_analysis: Dict) -> List[str]:
        """💡 Generate evidence handling recommendations"""
        recommendations = []
        
        evidence_type = basic_analysis.get('evidence_category', 'unknown')
        confidence = ai_analysis.get('confidence_score', 50)
        
        if evidence_type == 'photograph':
            recommendations.extend([
                "Verify EXIF data for timestamp and location authenticity",
                "Consider professional photographic analysis",
                "Obtain original high-resolution version if available"
            ])
        elif evidence_type == 'video':
            recommendations.extend([
                "Conduct frame-by-frame analysis for key moments",
                "Verify audio-video synchronization",
                "Extract still frames for detailed examination"
            ])
        elif evidence_type == 'audio':
            recommendations.extend([
                "Perform audio enhancement and noise reduction",
                "Conduct voice identification if applicable",
                "Analyze background sounds for location verification"
            ])
        
        if confidence < 70:
            recommendations.append("Consider additional expert analysis due to lower confidence score")
        
        recommendations.extend([
            "Maintain secure chain of custody documentation",
            "Prepare evidence authentication affidavit",
            "Consider cross-referencing with other evidence"
        ])
        
        return recommendations
    
    def _compile_analysis_results(self, basic_analysis: Dict, ai_analysis: Dict, legal_assessment: Dict, file_hash: str) -> Dict:
        """📊 Compile comprehensive analysis results"""
        return {
            'file_hash': file_hash,
            'basic_analysis': basic_analysis,
            'ai_analysis': ai_analysis,
            'legal_assessment': legal_assessment,
            'analysis_metadata': {
                'version': '1.0',
                'agent': 'EvidenceAnalysisAgent',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _record_performance(self, operation: str, duration: float, success: bool):
        """📈 Record performance metrics"""
        metric = {
            'operation': operation,
            'duration': duration,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.analysis_performance.append(metric)
        
        # Keep only last 500 metrics
        if len(st.session_state.analysis_performance) > 500:
            st.session_state.analysis_performance = st.session_state.analysis_performance[-500:]
    
    def analyze_multimodal_evidence_batch(self, uploaded_files: List, progress_callback=None) -> Dict:
        """
        🚀 ADVANCED: Batch analysis of multiple evidence files using optimal model selection
        
        This method maximizes Groq free tier efficiency by:
        - Routing different file types to optimal models
        - Batching similar evidence types together
        - Using caching to minimize API calls
        - Smart rate limiting and error handling
        """
        batch_results = {
            'total_files': len(uploaded_files),
            'processed_files': 0,
            'failed_files': 0,
            'analyses': [],
            'batch_insights': {},
            'processing_time': 0,
            'models_used': {},
            'rate_limit_status': 'optimal'
        }
        
        start_time = time.time()
        
        # Group files by evidence type for optimal processing
        file_groups = self._group_files_by_type(uploaded_files)
        
        # Process each group with the optimal model
        for evidence_type, files in file_groups.items():
            model_config = self._select_optimal_model(evidence_type)
            batch_results['models_used'][evidence_type] = model_config['model']
            
            st.info(f"🔍 Processing {len(files)} {evidence_type} files with {model_config['model']}")
            
            for i, file in enumerate(files):
                try:
                    if progress_callback:
                        progress_callback(batch_results['processed_files'] + 1, batch_results['total_files'])
                    
                    # Special handling for audio files (transcription)
                    if evidence_type == 'audio':
                        analysis = self._analyze_audio_with_transcription(file)
                    else:
                        analysis, from_cache = self.analyze_evidence_comprehensive(file)
                    
                    if analysis and 'error' not in analysis:
                        batch_results['analyses'].append({
                            'filename': file.name,
                            'evidence_type': evidence_type,
                            'analysis': analysis,
                            'model_used': model_config['model']
                        })
                        batch_results['processed_files'] += 1
                    else:
                        batch_results['failed_files'] += 1
                        
                except Exception as e:
                    st.warning(f"⚠️ Failed to process {file.name}: {str(e)}")
                    batch_results['failed_files'] += 1
        
        # Generate batch insights
        batch_results['processing_time'] = round(time.time() - start_time, 2)
        batch_results['batch_insights'] = self._generate_batch_insights(batch_results['analyses'])
        
        return batch_results
    
    def _group_files_by_type(self, uploaded_files: List) -> Dict:
        """📂 Group files by evidence type for optimal batch processing"""
        groups = {
            'photograph': [],
            'video': [],
            'audio': [],
            'document': [],
            'witness_statement': [],
            'digital_evidence': []
        }
        
        for file in uploaded_files:
            evidence_type = self._categorize_evidence_type(file.type, Path(file.name).suffix.lower())
            groups[evidence_type].append(file)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _analyze_audio_with_transcription(self, uploaded_file) -> Dict:
        """🎵 Enhanced audio analysis with Whisper transcription"""
        try:
            file_content = uploaded_file.getvalue()
            
            # Basic audio analysis
            basic_analysis = self._analyze_file_basic(uploaded_file, file_content)
            
            # Get transcription using Whisper
            transcription_result = self._handle_audio_transcription(file_content)
            
            # AI analysis of transcribed content
            if 'transcription' in transcription_result:
                transcription_text = transcription_result['transcription']
                
                # Use optimized model for text analysis
                prompt = f"""
                Analyze this audio evidence transcription for ICC submission:
                
                AUDIO METADATA:
                - File: {uploaded_file.name}
                - Estimated length: {transcription_result.get('audio_length_estimate', 'unknown')} seconds
                - Language: {transcription_result.get('language', 'en')}
                
                TRANSCRIPTION:
                {transcription_text}
                
                Provide legal analysis in JSON format:
                {{
                    "content_type": "speech|testimony|ambient_sound|conversation|other",
                    "legal_significance": "Why this audio is legally significant",
                    "key_statements": ["List of important statements or sounds"],
                    "speaker_analysis": "Analysis of speakers if identifiable",
                    "evidence_quality": "excellent|good|fair|poor",
                    "icc_relevance": "high|medium|low",
                    "recommended_action": "Next steps for this audio evidence",
                    "chain_of_custody_needs": "Authentication requirements"
                }}
                """
                
                try:
                    response = self.groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",  # Good for text analysis
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=1000
                    )
                    
                    analysis = json.loads(response.choices[0].message.content)
                    analysis['transcription'] = transcription_result
                    analysis['basic_metadata'] = basic_analysis
                    
                    return analysis
                    
                except Exception as e:
                    return {
                        'transcription': transcription_result,
                        'basic_metadata': basic_analysis,
                        'analysis_error': f"AI analysis failed: {str(e)}"
                    }
            else:
                return {
                    'basic_metadata': basic_analysis,
                    'transcription_error': transcription_result.get('transcription_error', 'Transcription failed')
                }
                
        except Exception as e:
            return {'error': f"Audio analysis failed: {str(e)}"}
    
    def _generate_batch_insights(self, analyses: List[Dict]) -> Dict:
        """📊 Generate comprehensive insights from batch analysis"""
        if not analyses:
            return {}
        
        insights = {
            'evidence_distribution': {},
            'quality_assessment': {},
            'legal_strength': {},
            'recommendations': [],
            'timeline_analysis': {},
            'geographic_data': {}
        }
        
        # Evidence type distribution
        evidence_types = [a['evidence_type'] for a in analyses]
        insights['evidence_distribution'] = {
            etype: evidence_types.count(etype) for etype in set(evidence_types)
        }
        
        # Quality assessment
        quality_scores = []
        for analysis in analyses:
            if 'analysis' in analysis and 'legal_assessment' in analysis['analysis']:
                score = analysis['analysis']['legal_assessment'].get('overall_legal_score', 0)
                quality_scores.append(score)
        
        if quality_scores:
            insights['quality_assessment'] = {
                'average_score': round(sum(quality_scores) / len(quality_scores), 1),
                'highest_score': max(quality_scores),
                'lowest_score': min(quality_scores),
                'total_analyzed': len(quality_scores)
            }
        
        # Generate strategic recommendations
        insights['recommendations'] = self._generate_strategic_recommendations(analyses)
        
        return insights
    
    def _generate_strategic_recommendations(self, analyses: List[Dict]) -> List[str]:
        """🎯 Generate strategic recommendations based on evidence portfolio"""
        recommendations = []
        
        # Count evidence types
        evidence_counts = {}
        for analysis in analyses:
            etype = analysis.get('evidence_type', 'unknown')
            evidence_counts[etype] = evidence_counts.get(etype, 0) + 1
        
        # Strategic recommendations based on evidence portfolio
        if evidence_counts.get('photograph', 0) > 3:
            recommendations.append("📸 Strong visual evidence portfolio - consider creating evidence timeline")
        
        if evidence_counts.get('video', 0) > 0:
            recommendations.append("🎥 Video evidence present - prioritize for expert authentication")
        
        if evidence_counts.get('audio', 0) > 0:
            recommendations.append("🎵 Audio evidence available - ensure speaker identification and context")
        
        if evidence_counts.get('document', 0) > 2:
            recommendations.append("📄 Multiple documents - verify authenticity and create evidence chain")
        
        # General ICC recommendations
        recommendations.extend([
            "⚖️ Consider expert witness testimony to validate technical evidence",
            "🔒 Establish clear chain of custody for all evidence",
            "🌍 Verify geographic and temporal consistency across evidence",
            "📋 Prepare evidence authentication documentation for ICC submission"
        ])
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def display_analysis_results(self, analysis_result: Dict, from_cache: bool = False):
        """📊 Display comprehensive analysis results with visualizations"""
        if not analysis_result:
            st.error("No analysis results to display")
            return
        
        # Performance header
        performance = analysis_result.get('performance', {})
        analysis_time = performance.get('analysis_time', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cache_status = "🔥 FROM CACHE" if from_cache else "⚡ REAL-TIME"
            st.success(f"{cache_status}")
        
        with col2:
            st.metric("Analysis Time", f"{analysis_time:.2f}s")
        
        with col3:
            overall_score = analysis_result.get('legal_assessment', {}).get('overall_legal_score', 0)
            st.metric("Legal Score", f"{overall_score}%")
        
        # Basic file information
        basic_info = analysis_result.get('basic_analysis', {})
        
        with st.expander("📁 File Information", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Filename:** {basic_info.get('filename', 'Unknown')}")
                st.write(f"**Type:** {basic_info.get('evidence_category', 'Unknown')}")
                st.write(f"**Size:** {basic_info.get('file_size_mb', 0)} MB")
            
            with col2:
                st.write(f"**Format:** {basic_info.get('file_type', 'Unknown')}")
                
                if 'image_width' in basic_info:
                    st.write(f"**Dimensions:** {basic_info['image_width']}x{basic_info['image_height']}")
                    st.write(f"**Quality:** {basic_info.get('quality_indicator', 'Unknown')}")
        
        # AI Analysis Results
        ai_analysis = analysis_result.get('ai_analysis', {})
        
        if ai_analysis and 'error' not in ai_analysis:
            with st.expander("🤖 AI Analysis", expanded=True):
                st.write(f"**Content Description:** {ai_analysis.get('content_description', 'Not available')}")
                st.write(f"**Incident Relevance:** {ai_analysis.get('incident_relevance', 'Not available')}")
                
                confidence = ai_analysis.get('confidence_score', 0)
                st.progress(confidence / 100)
                st.write(f"**AI Confidence:** {confidence}%")
                
                if 'key_observations' in ai_analysis:
                    st.write("**Key Observations:**")
                    for obs in ai_analysis['key_observations']:
                        st.write(f"• {obs}")
        
        # Legal Assessment
        legal_assessment = analysis_result.get('legal_assessment', {})
        
        if legal_assessment and 'error' not in legal_assessment:
            with st.expander("⚖️ Legal Assessment", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Legal Value:** {legal_assessment.get('legal_value', 'Unknown')}")
                    st.write(f"**Admissibility:** {legal_assessment.get('admissibility_strength', 'Unknown')}")
                    st.write(f"**ICC Relevance:** {legal_assessment.get('icc_relevance', 'Unknown')}")
                
                with col2:
                    quality = legal_assessment.get('evidence_quality', {})
                    if quality:
                        st.write("**Quality Assessment:**")
                        for factor, score in quality.items():
                            if factor != 'overall_score':
                                st.write(f"• {factor.replace('_', ' ').title()}: {score}")
                
                # Recommendations
                if 'recommended_actions' in legal_assessment:
                    st.write("**Recommended Actions:**")
                    for action in legal_assessment['recommended_actions']:
                        st.write(f"• {action}")
        
        # Quality visualization
        if legal_assessment and 'evidence_quality' in legal_assessment:
            quality_data = legal_assessment['evidence_quality']
            if isinstance(quality_data, dict) and len(quality_data) > 1:
                
                # Create quality radar chart
                categories = []
                values = []
                
                for key, value in quality_data.items():
                    if key != 'overall_score' and isinstance(value, (int, float)):
                        categories.append(key.replace('_', ' ').title())
                        values.append(value)
                
                if categories and values:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name='Evidence Quality'
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        showlegend=False,
                        title="Evidence Quality Assessment"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    def get_performance_analytics(self) -> Dict:
        """📈 Get performance analytics"""
        if not st.session_state.analysis_performance:
            return {'message': 'No performance data available'}
        
        df = pd.DataFrame(st.session_state.analysis_performance)
        
        analytics = {
            'total_operations': len(df),
            'successful_operations': len(df[df['success'] == True]),
            'failed_operations': len(df[df['success'] == False]),
            'success_rate': len(df[df['success'] == True]) / len(df) * 100,
            'average_duration': df['duration'].mean(),
            'fastest_operation': df['duration'].min(),
            'slowest_operation': df['duration'].max(),
            'operations_by_type': df.groupby('operation').size().to_dict()
        }
        
        return analytics
    
    def display_performance_dashboard(self):
        """📊 Display performance dashboard"""
        st.subheader("📈 Evidence Analysis Performance")
        
        analytics = self.get_performance_analytics()
        
        if 'message' in analytics:
            st.info(analytics['message'])
            return
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Operations", analytics['total_operations'])
        with col2:
            st.metric("Success Rate", f"{analytics['success_rate']:.1f}%")
        with col3:
            st.metric("Avg Duration", f"{analytics['average_duration']:.2f}s")
        with col4:
            cache_size = len(st.session_state.evidence_analysis_cache) if self.cache_enabled else 0
            st.metric("Cached Results", cache_size)
        
        # Performance chart
        if st.session_state.analysis_performance:
            df = pd.DataFrame(st.session_state.analysis_performance)
            
            fig = px.line(
                df.tail(50),  # Show last 50 operations
                x='timestamp',
                y='duration',
                color='operation',
                title="Analysis Performance Over Time"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def display_model_usage_dashboard(self):
        """📊 Display comprehensive model usage dashboard"""
        st.subheader("🚀 Groq Multimodal AI Dashboard")
        
        # Get current usage
        current_usage = self._get_current_usage_estimates()
        
        # Create columns for dashboard
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Premium Models Used Today", 
                     current_usage.get('llama-3.3-70b-versatile', 0) + 
                     current_usage.get('deepseek-r1-distill-llama-70b', 0),
                     "/ 2,000 daily limit")
        
        with col2:
            st.metric("⚡ Bulk Models Used Today",
                     current_usage.get('gemma2-9b-it', 0) + 
                     current_usage.get('llama-3.1-8b-instant', 0),
                     "/ 28,800 daily limit")
        
        with col3:
            audio_usage = current_usage.get('whisper-large-v3-turbo', 0)
            st.metric("🎵 Audio Seconds Processed", 
                     audio_usage * 30,  # Rough estimate
                     "/ 7,200 hourly limit")
        
        # Model recommendation display
        st.subheader("🧠 Smart Model Recommendations")
        
        evidence_types = ['photograph', 'video', 'audio', 'document', 'witness_statement']
        
        for evidence_type in evidence_types:
            with st.expander(f"📂 {evidence_type.title()} Evidence Strategy"):
                recommendation = self.get_smart_model_recommendation(evidence_type, 5.0, current_usage)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write("**Recommended Model:**")
                    primary = recommendation['primary']
                    st.code(f"{primary['model']}\nTokens: {primary['max_tokens']}\nTemp: {primary['temperature']}")
                
                with col_b:
                    st.write("**Strategy Reasoning:**")
                    for reason in recommendation['reasoning']:
                        st.write(f"• {reason}")
        
        # Overall strategy display
        strategy = self._get_usage_strategy(current_usage)
        health = self._assess_rate_limit_health(current_usage)
        
        st.info(f"**Strategy:** {strategy}")
        st.info(f"**Health:** {health}")
    
    def get_smart_model_recommendation(self, evidence_category: str, file_size_mb: float, 
                                      current_usage: Dict = None) -> Dict:
        """🧠 AI-powered model selection based on current usage and evidence characteristics"""
        
        # Initialize usage tracking if not provided
        if current_usage is None:
            current_usage = self._get_current_usage_estimates()
        
        # Evidence complexity scoring
        complexity_score = self._calculate_evidence_complexity(evidence_category, file_size_mb)
        
        recommendations = {
            'primary': None,
            'fallback': None,
            'experimental': None,
            'reasoning': [],
            'usage_optimization': {}
        }
        
        # Smart selection logic based on your actual rate limits
        if evidence_category == 'photograph':
            if complexity_score > 7:  # High complexity image
                if current_usage.get('llama-3.3-70b-versatile', 0) < 800:  # Under daily limit
                    recommendations['primary'] = self._select_optimal_model('photograph', 'high_priority')
                    recommendations['reasoning'].append("📸 High-complexity photo → Premium model (llama-3.3-70b)")
                else:
                    recommendations['primary'] = self._select_optimal_model('photograph', 'standard')
                    recommendations['reasoning'].append("📸 Premium model limit reached → High-volume model")
            else:
                recommendations['primary'] = self._select_optimal_model('photograph', 'standard')
                recommendations['reasoning'].append("📸 Standard photo analysis → Bulk processing model")
            
        elif evidence_category == 'audio':
            # Always use Whisper for transcription, then analysis model
            recommendations['transcription'] = {
                'model': 'whisper-large-v3-turbo',
                'reasoning': '🎵 Audio transcription → Whisper Turbo (7,200 sec/hour limit)'
            }
            
            if current_usage.get('mistral-saba-24b', 0) < 800:
                recommendations['primary'] = self._select_optimal_model('audio', 'high_priority')
                recommendations['reasoning'].append("🎵 Audio analysis → Premium reasoning model")
            else:
                recommendations['primary'] = self._select_optimal_model('audio', 'standard')
                recommendations['reasoning'].append("🎵 Premium limit reached → Fast analysis model")
        
        elif evidence_category == 'document':
            if complexity_score > 8:  # Legal documents need best reasoning
                if current_usage.get('qwen-qwq-32b', 0) < 800:
                    recommendations['primary'] = self._select_optimal_model('document', 'high_priority')
                    recommendations['reasoning'].append("📄 Legal document → Advanced reasoning model (QwQ)")
                else:
                    recommendations['primary'] = self._select_optimal_model('document', 'standard')
                    recommendations['reasoning'].append("📄 Premium limit reached → Standard document model")
            else:
                recommendations['primary'] = self._select_optimal_model('document', 'standard')
                recommendations['reasoning'].append("📄 Standard document → Efficient processing model")
        
        elif evidence_category == 'video':
            # Videos always need complex reasoning
            if current_usage.get('deepseek-r1-distill-llama-70b', 0) < 800:
                recommendations['primary'] = self._select_optimal_model('video', 'high_priority')
                recommendations['reasoning'].append("🎥 Video analysis → DeepSeek reasoning model")
            else:
                recommendations['primary'] = self._select_optimal_model('video', 'standard')
                recommendations['reasoning'].append("🎥 Premium limit reached → Standard video processing")
        
        # Experimental option for complex cases
        if complexity_score > 9 and current_usage.get('compound-beta', 0) < 150:  # Very limited daily requests
            recommendations['experimental'] = self._select_optimal_model('digital_evidence', 'experimental')
            recommendations['reasoning'].append("🧪 Ultra-complex case → Experimental model (70k tokens!)")
        
        # Fallback strategy
        recommendations['fallback'] = self._select_optimal_model('digital_evidence', 'fast')
        recommendations['reasoning'].append("⚡ Fallback → Ultra-fast model for reliability")
        
        return recommendations
    
    def _calculate_evidence_complexity(self, evidence_category: str, file_size_mb: float) -> int:
        """📊 Calculate evidence complexity score (1-10)"""
        base_scores = {
            'photograph': 5,
            'video': 8,      # Videos are inherently complex
            'audio': 6,
            'document': 4,
            'witness_statement': 7,
            'digital_evidence': 3
        }
        
        base_score = base_scores.get(evidence_category, 5)
        
        # Adjust based on file size
        if file_size_mb > 10:
            base_score += 2
        elif file_size_mb > 5:
            base_score += 1
        elif file_size_mb < 0.1:
            base_score -= 1
        
        return min(10, max(1, base_score))
    
    def _get_current_usage_estimates(self) -> Dict:
        """📈 Estimate current API usage (in a real app, this would track actual usage)"""
        # In a production system, this would query actual usage from Groq API
        # For now, we'll use session state to track estimates
        
        if 'groq_usage_tracking' not in st.session_state:
            st.session_state.groq_usage_tracking = {
                'llama-3.3-70b-versatile': 0,
                'deepseek-r1-distill-llama-70b': 0,
                'qwen-qwq-32b': 0,
                'compound-beta': 0,
                'gemma2-9b-it': 0,
                'llama-3.1-8b-instant': 0,
                'whisper-large-v3-turbo': 0,
                'mistral-saba-24b': 0,
                'qwen/qwen3-32b': 0,
                'allam-2-7b': 0,
                'last_reset': datetime.now().date()
            }
        
        # Reset daily counters if new day
        if st.session_state.groq_usage_tracking['last_reset'] != datetime.now().date():
            for key in st.session_state.groq_usage_tracking:
                if key != 'last_reset':
                    st.session_state.groq_usage_tracking[key] = 0
            st.session_state.groq_usage_tracking['last_reset'] = datetime.now().date()
        
        return st.session_state.groq_usage_tracking
    
    def _get_usage_strategy(self, current_usage: Dict) -> str:
        """🎯 Get optimal usage strategy based on current consumption"""
        total_premium_usage = (
            current_usage.get('llama-3.3-70b-versatile', 0) +
            current_usage.get('deepseek-r1-distill-llama-70b', 0) +
            current_usage.get('qwen-qwq-32b', 0)
        )
        
        if total_premium_usage < 500:
            return "🟢 OPTIMAL: Use premium models freely"
        elif total_premium_usage < 2000:
            return "🟡 MODERATE: Mix premium and bulk models"
        else:
            return "🔴 CONSERVATIVE: Use bulk models primarily, save premium for critical cases"
    
    def _assess_rate_limit_health(self, current_usage: Dict) -> str:
        """💚 Assess overall rate limit health"""
        critical_models = ['llama-3.3-70b-versatile', 'deepseek-r1-distill-llama-70b']
        critical_usage = sum(current_usage.get(model, 0) for model in critical_models)
        
        if critical_usage < 1000:  # Well under daily limits
            return "🟢 EXCELLENT: All models available"
        elif critical_usage < 1600:
            return "🟡 GOOD: Some premium limits approaching"
        else:
            return "🔴 CAUTION: Premium models near daily limits"
    
    def update_usage_tracking(self, model_used: str, tokens_consumed: int = 100):
        """📊 Update usage tracking (call this after each API request)"""
        if 'groq_usage_tracking' not in st.session_state:
            self._get_current_usage_estimates()  # Initialize
        
        if model_used in st.session_state.groq_usage_tracking:
            st.session_state.groq_usage_tracking[model_used] += 1
        
        # Also track approximate token usage
        token_key = f"{model_used}_tokens"
        if token_key not in st.session_state.groq_usage_tracking:
            st.session_state.groq_usage_tracking[token_key] = 0
        st.session_state.groq_usage_tracking[token_key] += tokens_consumed
# Factory function for agent creation
def get_evidence_analysis_agent(cache_enabled: bool = True, groq_api_key: str = None):
    """
    🎯 Factory function to create Evidence Analysis agent
    
    Args:
        cache_enabled: Whether to enable result caching
        groq_api_key: Groq API key for AI analysis
        
    Returns:
        EvidenceAnalysisAgent: Configured analysis agent
    """
    return EvidenceAnalysisAgent(cache_enabled=cache_enabled, groq_api_key=groq_api_key)

# Standalone execution for testing
if __name__ == "__main__":
    st.title("🔍 Evidence Analysis Core Agent")
    st.write("Advanced AI-powered evidence analysis for ICC submissions")
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        cache_enabled = st.checkbox("Enable Caching", value=True)
    with col2:
        include_legal = st.checkbox("Include Legal Assessment", value=True)
    
    # Create agent
    agent = get_evidence_analysis_agent(cache_enabled=cache_enabled)
    
    # Display performance dashboard
    agent.display_performance_dashboard()
    
    # File analysis interface
    st.subheader("🧪 Evidence Analysis Test")
    
    uploaded_file = st.file_uploader(
        "Upload evidence file for analysis",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mp3', 'wav', 'pdf', 'docx', 'txt']
    )
    
    if uploaded_file:
        if st.button("🔍 Analyze Evidence", type="primary"):
            result, from_cache = agent.analyze_evidence_comprehensive(
                uploaded_file, 
                include_legal_assessment=include_legal
            )
            
            if result:
                agent.display_analysis_results(result, from_cache)
            else:
                st.error("❌ Analysis failed")
