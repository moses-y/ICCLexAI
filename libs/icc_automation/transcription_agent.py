"""
🇰🇪 ICC TRANSCRIPTION SPECIALIST AGENT
Specialized agent for audio/video transcription and analysis

RESPONSIBILITIES:
🔹 Audio transcription with timestamps
🔹 Video audio extraction and transcription
🔹 Speaker identification and analysis
🔹 Emotional analysis and urgency detection
🔹 Background noise and context analysis
🔹 Legal relevance assessment for testimony
"""

import os
import io
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TranscriptionAgent:
    """Specialized agent for comprehensive audio/video transcription and analysis"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_client = Groq(api_key=groq_api_key or os.getenv('GROQ_API_KEY'))
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Supported audio/video formats
        self.supported_audio = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
        self.supported_video = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm']
        
        # Language detection and transcription models
        self.transcription_models = {
            'whisper-large-v3': 'Most accurate, slower',
            'whisper-large-v3-turbo': 'Fast and accurate'
        }
    
    async def analyze_audio_evidence(self, file_data: Dict[str, Any], 
                                   shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive audio evidence analysis
        
        Args:
            file_data: File data with content, filename, type, metadata
            shared_context: Shared context from ICC case
            
        Returns:
            Comprehensive transcription and analysis results
        """
        
        try:
            self.logger.info(f"Analyzing audio evidence: {file_data.get('filename', 'unknown')}")
            
            # Extract audio content and metadata
            content = file_data.get('content', b'')
            filename = file_data.get('filename', 'unknown')
            metadata = file_data.get('metadata', {})
            
            # Transcribe audio
            transcription_result = await self._transcribe_audio(content, filename)
            
            # Analyze transcription content
            content_analysis = await self._analyze_transcription_content(
                transcription_result, shared_context
            )
            
            # Perform speaker analysis
            speaker_analysis = await self._analyze_speakers(transcription_result)
            
            # Analyze emotional context and urgency
            emotional_analysis = await self._analyze_emotional_context(transcription_result)
            
            # Assess legal relevance
            legal_assessment = await self._assess_legal_relevance(
                transcription_result, content_analysis, shared_context
            )
            
            # Generate comprehensive analysis
            analysis_result = {
                'agent_type': 'transcription_specialist',
                'processing_timestamp': datetime.now().isoformat(),
                'transcription': transcription_result,
                'content_analysis': content_analysis,
                'speaker_analysis': speaker_analysis,
                'emotional_analysis': emotional_analysis,
                'legal_assessment': legal_assessment,
                'evidence_quality': self._calculate_audio_quality(transcription_result, metadata),
                'recommendations': self._generate_recommendations(
                    transcription_result, content_analysis, legal_assessment
                )
            }
            
            self.logger.info(f"Audio analysis completed: {filename}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing audio evidence: {str(e)}")
            return {
                'agent_type': 'transcription_specialist',
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    async def _transcribe_audio(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Transcribe audio content using Groq Whisper"""
        
        try:
            # Save content to temporary file for processing
            file_extension = os.path.splitext(filename)[1].lower()
            if not file_extension:
                file_extension = '.wav'  # Default extension
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Transcribe using Groq Whisper
            with open(temp_path, 'rb') as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    temperature=0.0
                )
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Process transcription result
            result = {
                'text': transcription.text,
                'language': getattr(transcription, 'language', 'unknown'),
                'duration': getattr(transcription, 'duration', 0),
                'segments': getattr(transcription, 'segments', []),
                'confidence': self._calculate_transcription_confidence(transcription),
                'word_count': len(transcription.text.split()) if transcription.text else 0,
                'processing_model': 'whisper-large-v3-turbo'
            }
            
            # Add timestamp analysis
            if hasattr(transcription, 'segments') and transcription.segments:
                result['timestamps'] = self._extract_timestamps(transcription.segments)
                result['speaking_rate'] = self._calculate_speaking_rate(transcription.segments)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed for {filename}: {str(e)}")
            return {
                'error': f"Transcription failed: {str(e)}",
                'text': '',
                'confidence': 0.0,
                'status': 'failed'
            }
    
    async def _analyze_transcription_content(self, transcription: Dict[str, Any], 
                                           shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transcription content for legal relevance and key information"""
        
        if not transcription.get('text'):
            return {'error': 'No transcription text available'}
        
        case_context = shared_context.get('case_metadata', {})
        
        prompt = f"""
        AUDIO TRANSCRIPTION CONTENT ANALYSIS
        
        CASE CONTEXT:
        Incident: {case_context.get('incident_description', 'ICC human rights violation')}
        Location: {case_context.get('incident_location', 'Kenya')}
        Date: {case_context.get('incident_date', 'Unknown')}
        
        TRANSCRIPTION TO ANALYZE:
        "{transcription['text']}"
        
        TRANSCRIPTION METADATA:
        Language: {transcription.get('language', 'unknown')}
        Duration: {transcription.get('duration', 0)} seconds
        Word Count: {transcription.get('word_count', 0)}
        Confidence: {transcription.get('confidence', 0):.2f}
        
        Provide comprehensive content analysis in JSON format:
        {{
            "key_statements": ["most", "important", "statements"],
            "entities_mentioned": {{
                "people": ["names", "mentioned"],
                "locations": ["places", "mentioned"],
                "organizations": ["groups", "mentioned"],
                "weapons": ["weapons", "mentioned"],
                "vehicles": ["vehicles", "mentioned"],
                "dates_times": ["temporal", "references"]
            }},
            "incident_references": ["direct", "references", "to", "incident"],
            "testimony_type": "witness|victim|perpetrator|bystander|other",
            "narrative_coherence": 8.5,
            "factual_content": ["verifiable", "facts", "mentioned"],
            "emotional_indicators": ["fear", "anger", "trauma", "etc"],
            "credibility_indicators": ["specific", "details", "consistency"],
            "inconsistencies": ["potential", "inconsistencies"],
            "legal_keywords": ["relevant", "legal", "terms"],
            "urgency_indicators": ["emergency", "immediate", "threat"],
            "protective_concerns": ["safety", "concerns", "mentioned"],
            "corroborating_elements": ["elements", "that", "can", "be", "verified"],
            "content_relevance": 8.7,
            "testimony_strength": "strong|moderate|weak",
            "recommended_follow_up": ["specific", "follow", "up", "actions"]
        }}
        
        Provide specific, actionable analysis based on the actual transcription content.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert legal analyst specializing in witness testimony and audio evidence for ICC proceedings. Provide detailed, structured analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Clean and parse JSON response
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            analysis = json.loads(analysis_text)
            
            # Validate and normalize scores
            for score_field in ['narrative_coherence', 'content_relevance']:
                if score_field in analysis:
                    try:
                        score = float(analysis[score_field])
                        analysis[score_field] = max(1.0, min(10.0, score))
                    except (ValueError, TypeError):
                        analysis[score_field] = 5.0
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {
                'error': f"Content analysis failed: {str(e)}",
                'content_relevance': 5.0,
                'testimony_strength': 'unknown'
            }
    
    async def _analyze_speakers(self, transcription: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze speakers in the audio"""
        
        if not transcription.get('text'):
            return {'speaker_count': 0, 'analysis': 'No audio content'}
        
        # Simple speaker analysis based on transcription patterns
        text = transcription['text']
        
        # Look for dialogue patterns
        dialogue_indicators = [
            '"', "'", "said", "says", "asked", "replied", 
            "answered", "told", "mentioned", "stated"
        ]
        
        speaker_analysis = {
            'estimated_speakers': 1,  # Default single speaker
            'dialogue_detected': any(indicator in text.lower() for indicator in dialogue_indicators),
            'speaker_changes': [],
            'dominant_speaker': 'primary',
            'interaction_type': 'monologue'
        }
        
        # Enhanced speaker analysis with Groq
        if len(text) > 50:  # Only analyze substantial content
            try:
                prompt = f"""
                Analyze this audio transcription for speaker information:
                
                "{text}"
                
                Provide speaker analysis in JSON format:
                {{
                    "estimated_speaker_count": 1,
                    "speaker_characteristics": ["male", "female", "child", "elderly"],
                    "interaction_type": "monologue|dialogue|interview|conversation|testimony",
                    "dialogue_patterns": ["question-answer", "interruptions", "overlapping"],
                    "speaker_emotions": ["calm", "distressed", "angry", "fearful"],
                    "language_formality": "formal|informal|mixed",
                    "testimony_style": "narrative|factual|emotional|structured"
                }}
                """
                
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500
                )
                
                ai_analysis = json.loads(response.choices[0].message.content)
                speaker_analysis.update(ai_analysis)
                
            except Exception as e:
                self.logger.warning(f"Speaker AI analysis failed: {str(e)}")
        
        return speaker_analysis
    
    async def _analyze_emotional_context(self, transcription: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emotional context and psychological indicators"""
        
        if not transcription.get('text'):
            return {'emotional_state': 'unknown', 'analysis': 'No content'}
        
        text = transcription['text']
        
        # Basic emotional keyword analysis
        emotional_keywords = {
            'fear': ['afraid', 'scared', 'terrified', 'frightened', 'panic'],
            'trauma': ['traumatic', 'nightmare', 'flashback', 'haunted'],
            'anger': ['angry', 'furious', 'rage', 'mad', 'outraged'],
            'sadness': ['sad', 'depressed', 'crying', 'tears', 'heartbroken'],
            'urgency': ['urgent', 'emergency', 'immediate', 'quickly', 'hurry'],
            'pain': ['hurt', 'pain', 'agony', 'suffering', 'ache']
        }
        
        detected_emotions = {}
        for emotion, keywords in emotional_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text.lower())
            if count > 0:
                detected_emotions[emotion] = count
        
        # Enhanced emotional analysis with Groq
        try:
            prompt = f"""
            Analyze the emotional context and psychological state in this testimony:
            
            "{text[:1000]}..."  
            
            Provide emotional analysis in JSON format:
            {{
                "primary_emotion": "fear|anger|sadness|trauma|calm|distress",
                "emotional_intensity": 7.5,
                "trauma_indicators": ["specific", "trauma", "signs"],
                "stress_level": "high|medium|low",
                "psychological_state": "stable|distressed|traumatized|composed",
                "credibility_emotional": 8.0,
                "protective_needs": ["immediate", "protection", "needs"],
                "support_recommendations": ["counseling", "protection", "medical"],
                "emotional_consistency": "consistent|inconsistent|mixed"
            }}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            
            return {
                'detected_keywords': detected_emotions,
                'ai_analysis': ai_analysis,
                'emotional_summary': f"Primary emotion: {ai_analysis.get('primary_emotion', 'unknown')}, "
                                   f"Intensity: {ai_analysis.get('emotional_intensity', 0)}/10"
            }
            
        except Exception as e:
            self.logger.warning(f"Emotional analysis failed: {str(e)}")
            return {
                'detected_keywords': detected_emotions,
                'emotional_summary': f"Basic analysis: {len(detected_emotions)} emotional indicators detected",
                'analysis_error': str(e)
            }
    
    async def _assess_legal_relevance(self, transcription: Dict[str, Any], 
                                    content_analysis: Dict[str, Any],
                                    shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal relevance and evidentiary value"""
        
        case_context = shared_context.get('case_metadata', {})
        
        # Calculate relevance scores
        relevance_score = 5.0  # Base score
        
        # Boost for specific incident references
        incident_refs = content_analysis.get('incident_references', [])
        if incident_refs:
            relevance_score += min(len(incident_refs) * 1.5, 3.0)
        
        # Boost for entity mentions
        entities = content_analysis.get('entities_mentioned', {})
        entity_count = sum(len(entity_list) for entity_list in entities.values())
        if entity_count > 0:
            relevance_score += min(entity_count * 0.3, 2.0)
        
        # Boost for factual content
        facts = content_analysis.get('factual_content', [])
        if facts:
            relevance_score += min(len(facts) * 0.5, 2.0)
        
        # Penalty for inconsistencies
        inconsistencies = content_analysis.get('inconsistencies', [])
        if inconsistencies:
            relevance_score -= min(len(inconsistencies) * 0.5, 1.5)
        
        # Normalize score
        relevance_score = max(1.0, min(10.0, relevance_score))
        
        return {
            'legal_relevance_score': round(relevance_score, 2),
            'testimony_type': content_analysis.get('testimony_type', 'unknown'),
            'testimony_strength': content_analysis.get('testimony_strength', 'moderate'),
            'evidentiary_value': 'high' if relevance_score > 7.5 else 'medium' if relevance_score > 5.0 else 'low',
            'admissibility_factors': {
                'authenticity': transcription.get('confidence', 0) > 0.8,
                'relevance': relevance_score > 6.0,
                'reliability': content_analysis.get('narrative_coherence', 5.0) > 7.0,
                'completeness': transcription.get('word_count', 0) > 50
            },
            'legal_recommendations': self._generate_legal_recommendations(
                relevance_score, content_analysis, transcription
            )
        }
    
    def _generate_legal_recommendations(self, relevance_score: float, 
                                      content_analysis: Dict[str, Any],
                                      transcription: Dict[str, Any]) -> List[str]:
        """Generate specific legal recommendations for the audio evidence"""
        
        recommendations = []
        
        if relevance_score > 8.0:
            recommendations.append("Strong testimony - prioritize for ICC submission")
        elif relevance_score > 6.0:
            recommendations.append("Good testimony - include in evidence package")
        else:
            recommendations.append("Weak testimony - consider supplementary evidence")
        
        if transcription.get('confidence', 0) < 0.7:
            recommendations.append("Consider professional audio enhancement or re-transcription")
        
        if content_analysis.get('inconsistencies'):
            recommendations.append("Address identified inconsistencies through follow-up interviews")
        
        if content_analysis.get('protective_concerns'):
            recommendations.append("Implement witness protection protocols")
        
        if content_analysis.get('corroborating_elements'):
            recommendations.append("Gather corroborating evidence for mentioned details")
        
        if content_analysis.get('urgency_indicators'):
            recommendations.append("Escalate case due to urgency indicators")
        
        return recommendations
    
    def _calculate_transcription_confidence(self, transcription) -> float:
        """Calculate overall transcription confidence"""
        
        if hasattr(transcription, 'segments') and transcription.segments:
            # Calculate average confidence from segments
            confidences = []
            for segment in transcription.segments:
                if hasattr(segment, 'avg_logprob'):
                    # Convert log probability to confidence score
                    confidence = min(max((segment.avg_logprob + 1.0) * 10, 0), 10)
                    confidences.append(confidence)
            
            if confidences:
                return sum(confidences) / len(confidences) / 10.0  # Normalize to 0-1
        
        # Fallback confidence estimation
        text_length = len(transcription.text) if transcription.text else 0
        if text_length > 100:
            return 0.8
        elif text_length > 50:
            return 0.6
        else:
            return 0.4
    
    def _extract_timestamps(self, segments) -> List[Dict[str, Any]]:
        """Extract timestamps from transcription segments"""
        
        timestamps = []
        for segment in segments:
            if hasattr(segment, 'start') and hasattr(segment, 'end'):
                timestamps.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': getattr(segment, 'text', ''),
                    'duration': segment.end - segment.start
                })
        
        return timestamps
    
    def _calculate_speaking_rate(self, segments) -> Dict[str, float]:
        """Calculate speaking rate metrics"""
        
        total_words = 0
        total_duration = 0
        
        for segment in segments:
            if hasattr(segment, 'text') and hasattr(segment, 'start') and hasattr(segment, 'end'):
                words = len(segment.text.split())
                duration = segment.end - segment.start
                total_words += words
                total_duration += duration
        
        if total_duration > 0:
            words_per_minute = (total_words / total_duration) * 60
            return {
                'words_per_minute': round(words_per_minute, 2),
                'total_words': total_words,
                'total_duration': round(total_duration, 2),
                'speech_rate': 'fast' if words_per_minute > 150 else 'normal' if words_per_minute > 100 else 'slow'
            }
        
        return {'words_per_minute': 0, 'total_words': total_words, 'total_duration': 0}
    
    def _calculate_audio_quality(self, transcription: Dict[str, Any], 
                                metadata: Dict[str, Any]) -> float:
        """Calculate audio evidence quality score"""
        
        base_score = 5.0
        
        # Transcription confidence bonus
        confidence = transcription.get('confidence', 0.5)
        confidence_bonus = confidence * 3.0  # Max 3 points
        
        # Duration bonus (longer audio generally more valuable)
        duration = transcription.get('duration', 0)
        duration_bonus = min(duration / 60, 2.0)  # Max 2 points for duration
        
        # Word count bonus
        word_count = transcription.get('word_count', 0)
        word_bonus = min(word_count / 100, 2.0)  # Max 2 points for word count
        
        # Audio metadata bonus
        metadata_bonus = 0.5 if metadata.get('bitrate') or metadata.get('duration') else 0
        
        # Error penalty
        error_penalty = 1.0 if transcription.get('error') else 0.0
        
        total_score = base_score + confidence_bonus + duration_bonus + word_bonus + metadata_bonus - error_penalty
        return round(max(1.0, min(10.0, total_score)), 2)
    
    def _generate_recommendations(self, transcription: Dict[str, Any], 
                                 content_analysis: Dict[str, Any],
                                 legal_assessment: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations for the audio evidence"""
        
        recommendations = []
        
        # Quality recommendations
        if transcription.get('confidence', 0) < 0.7:
            recommendations.append("Consider audio enhancement or professional re-transcription")
        
        # Content recommendations
        if content_analysis.get('testimony_strength') == 'strong':
            recommendations.append("Prioritize this testimony for ICC submission")
        elif content_analysis.get('testimony_strength') == 'weak':
            recommendations.append("Supplement with additional evidence or clarification")
        
        # Legal recommendations
        legal_recs = legal_assessment.get('legal_recommendations', [])
        recommendations.extend(legal_recs)
        
        # Technical recommendations
        if transcription.get('duration', 0) < 30:
            recommendations.append("Short audio - consider gathering longer testimony")
        
        if transcription.get('word_count', 0) < 50:
            recommendations.append("Brief content - encourage more detailed testimony")
        
        return list(set(recommendations))  # Remove duplicates
