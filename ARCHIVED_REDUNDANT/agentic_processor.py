"""
ICCLexAI Agentic Evidence Processor
Intelligent AI workflow for automated ICC submission generation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class AgenticEvidenceProcessor:
    """AI-powered evidence analysis and ICC form generation"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.processing_cache = {}
        
    async def analyze_evidence_package(self, files: List[Dict], user_keywords: str) -> Dict[str, Any]:
        """
        Process all evidence and generate ICC submission context
        This is the core agentic workflow
        """
        print(f"🤖 Starting agentic analysis for {len(files)} evidence files...")
        
        # Step 1: Extract and analyze all evidence
        evidence_analysis = await self._extract_multimodal_evidence(files)
        
        # Step 2: Generate legal relevance scores
        legal_scoring = await self._score_legal_relevance(evidence_analysis, user_keywords)
        
        # Step 3: Identify evidence relationships and timeline
        evidence_timeline = await self._build_evidence_timeline(evidence_analysis)
        
        # Step 4: Generate comprehensive context
        contextual_summary = await self._generate_comprehensive_context(
            evidence_analysis, legal_scoring, evidence_timeline, user_keywords
        )
        
        return {
            "analysis_id": self._generate_analysis_id(files, user_keywords),
            "evidence_analysis": evidence_analysis,
            "legal_scoring": legal_scoring,
            "evidence_timeline": evidence_timeline,
            "contextual_summary": contextual_summary,
            "user_keywords": user_keywords,
            "processing_timestamp": datetime.now().isoformat(),
            "confidence_score": self._calculate_confidence_score(legal_scoring),
            "recommended_actions": await self._generate_recommendations(evidence_analysis)
        }
    
    async def generate_icc_context(self, analysis_results: Dict, additional_user_input: str = "") -> str:
        """Create 1000+ word contextual summary for ICC submission"""
        
        prompt = f"""
        As an expert legal AI specializing in International Criminal Court submissions, 
        generate a comprehensive 1000+ word contextual summary for an ICC evidence submission.
        
        EVIDENCE ANALYSIS:
        {json.dumps(analysis_results['evidence_analysis'], indent=2)}
        
        LEGAL SCORING:
        {json.dumps(analysis_results['legal_scoring'], indent=2)}
        
        EVIDENCE TIMELINE:
        {json.dumps(analysis_results['evidence_timeline'], indent=2)}
        
        USER KEYWORDS: {analysis_results['user_keywords']}
        ADDITIONAL INPUT: {additional_user_input}
        
        Generate a detailed, professional ICC submission context that includes:
        1. Executive Summary (200 words)
        2. Evidence Analysis and Legal Relevance (400 words)
        3. Timeline of Events (200 words)
        4. Technical Metadata Summary (100 words)
        5. Recommended Next Steps (100 words)
        
        Write in formal legal language appropriate for ICC submissions.
        Focus on factual analysis and legal significance.
        Include specific references to evidence file names and metadata.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                max_tokens=2000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating ICC context: {str(e)}"
    
    async def auto_populate_icc_form(self, context: str, evidence_metadata: Dict) -> Dict[str, Any]:
        """Map analysis to ICC form fields automatically"""
        
        # Extract ICC form mapping from our scraped data
        icc_form_structure = await self._load_icc_form_structure()
        
        prompt = f"""
        Based on the evidence analysis and ICC context, automatically populate ICC form fields.
        
        ICC CONTEXT:
        {context}
        
        EVIDENCE METADATA:
        {json.dumps(evidence_metadata, indent=2)}
        
        ICC FORM STRUCTURE:
        {json.dumps(icc_form_structure, indent=2)}
        
        Generate a JSON object mapping ICC form fields to appropriate values based on the evidence.
        For fields that cannot be determined from evidence, mark as "AI_ANALYSIS_NEEDED" or "USER_INPUT_REQUIRED".
        Include confidence scores for each field population (0-100).
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                max_tokens=1500,
                temperature=0.1
            )
            
            # Parse and structure the response
            icc_form_data = json.loads(response.choices[0].message.content)
            return {
                "form_data": icc_form_data,
                "auto_population_confidence": self._calculate_form_confidence(icc_form_data),
                "fields_requiring_user_input": self._identify_user_input_fields(icc_form_data),
                "generation_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error auto-populating ICC form: {str(e)}"}
    
    async def generate_chat_response(self, user_message: str, case_context: Dict) -> str:
        """Generate contextual AI assistant responses for the chat interface"""
        
        prompt = f"""
        You are an AI assistant specializing in ICC evidence submissions for the ICCLexAI platform.
        You have a Kenyan perspective on international justice and are helping users build strong cases.
        
        CURRENT CASE CONTEXT:
        {json.dumps(case_context, indent=2)}
        
        USER MESSAGE: {user_message}
        
        Provide helpful, contextual guidance that:
        1. References the specific evidence they've uploaded
        2. Suggests improvements or additional evidence needed
        3. Explains legal relevance of their evidence
        4. Maintains a professional but friendly Kenyan tone
        5. Keeps responses concise (2-3 sentences max)
        
        If appropriate, ask follow-up questions to gather missing information.
        Always include 🇰🇪 emoji when appropriate to show Kenyan context.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                max_tokens=300,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I'm having trouble processing your request right now 🇰🇪. Please try again. (Error: {str(e)})"

    async def _extract_multimodal_evidence(self, files: List[Dict]) -> Dict[str, Any]:
        """Extract evidence from all uploaded files using existing functions"""
        # Integrate with existing multimodal processing functions
        evidence_data = {}
        
        for file_info in files:
            file_type = file_info.get('type', '')
            file_name = file_info.get('name', '')
            
            if file_type.startswith('image/'):
                # Use existing image analysis functions
                evidence_data[file_name] = {
                    "type": "image",
                    "analysis": "Image analysis results",  # Replace with actual function call
                    "metadata": "Extracted metadata"
                }
            elif file_type.startswith('video/'):
                evidence_data[file_name] = {
                    "type": "video", 
                    "analysis": "Video analysis results",
                    "metadata": "Extracted metadata"
                }
            # Add more file types as needed
            
        return evidence_data
    
    async def _score_legal_relevance(self, evidence_analysis: Dict, keywords: str) -> Dict[str, int]:
        """Score legal relevance of evidence (0-100)"""
        relevance_scores = {}
        
        for file_name, analysis in evidence_analysis.items():
            # Simple scoring based on keywords and content
            score = 75  # Base score
            if keywords.lower() in str(analysis).lower():
                score += 20
            relevance_scores[file_name] = min(score, 100)
            
        return relevance_scores
    
    async def _build_evidence_timeline(self, evidence_analysis: Dict) -> List[Dict]:
        """Build chronological timeline of evidence"""
        timeline = []
        
        for file_name, analysis in evidence_analysis.items():
            timeline.append({
                "timestamp": datetime.now().isoformat(),  # Extract from metadata
                "file": file_name,
                "event_type": "evidence_collected",
                "description": f"Evidence file {file_name} collected"
            })
        
        return sorted(timeline, key=lambda x: x['timestamp'])
    
    async def _generate_comprehensive_context(self, evidence_analysis: Dict, legal_scoring: Dict, 
                                            timeline: List, keywords: str) -> str:
        """Generate comprehensive context using AI"""
        
        context_prompt = f"""
        Generate a comprehensive evidence summary for ICC submission:
        
        EVIDENCE: {json.dumps(evidence_analysis, indent=2)}
        LEGAL SCORES: {json.dumps(legal_scoring, indent=2)}
        TIMELINE: {json.dumps(timeline, indent=2)}
        KEYWORDS: {keywords}
        
        Create a 500-word professional summary highlighting:
        - Key evidence findings
        - Legal significance
        - Timeline of events
        - Recommendations for case building
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": context_prompt}],
                model="llama3-8b-8192",
                max_tokens=800,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating context: {str(e)}"
    
    async def _generate_recommendations(self, evidence_analysis: Dict) -> List[str]:
        """Generate AI recommendations for improving the case"""
        recommendations = [
            "Consider adding witness statements to strengthen the case",
            "Location data from evidence suggests additional geographic evidence may be available",
            "Timeline analysis indicates potential gaps that could be filled with additional documentation"
        ]
        return recommendations
    
    async def _load_icc_form_structure(self) -> Dict:
        """Load ICC form structure from our scraped data"""
        try:
            with open('icc_manual_form_mapping.json', 'r') as f:
                return json.load(f)
        except Exception:
            # Fallback form structure
            return {
                "incident_date": {"type": "date", "required": True},
                "incident_location": {"type": "text", "required": True},
                "incident_description": {"type": "textarea", "required": True},
                "evidence_type": {"type": "select", "required": True},
                "submitter_role": {"type": "select", "required": True}
            }
    
    def _generate_analysis_id(self, files: List[Dict], keywords: str) -> str:
        """Generate unique analysis ID"""
        content = f"{len(files)}-{keywords}-{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_confidence_score(self, legal_scoring: Dict) -> int:
        """Calculate overall confidence score"""
        if not legal_scoring:
            return 50
        return int(sum(legal_scoring.values()) / len(legal_scoring))
    
    def _calculate_form_confidence(self, form_data: Dict) -> int:
        """Calculate confidence score for auto-populated form"""
        populated_fields = sum(1 for value in form_data.values() 
                             if value and "REQUIRED" not in str(value).upper())
        total_fields = len(form_data)
        return int((populated_fields / total_fields) * 100) if total_fields > 0 else 0
    
    def _identify_user_input_fields(self, form_data: Dict) -> List[str]:
        """Identify fields that need user input"""
        return [field for field, value in form_data.items() 
                if "USER_INPUT_REQUIRED" in str(value).upper()]
