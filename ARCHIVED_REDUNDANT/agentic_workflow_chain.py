"""
🇰🇪 ICCLexAI Agentic Workflow Chain
Specialized multi-step AI workflow for ICC evidence submission
Combines the best of app.py's multi-step approach with advanced AI chaining
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class WorkflowStage(Enum):
    """Workflow stages for agentic processing"""
    UPLOAD = "upload"
    ANALYZE = "analyze" 
    ACCUMULATE = "accumulate"
    USER_DETAILS = "user_details"
    FORM_GENERATION = "form_generation"
    REVIEW = "review"
    SUBMISSION = "submission"
    COMPLETE = "complete"

@dataclass
class EvidenceItem:
    """Structured evidence item with analysis"""
    file_name: str
    file_type: str
    file_size: int
    file_content: bytes
    ai_analysis: Dict[str, Any]
    timestamp: str
    workflow_stage: WorkflowStage

@dataclass 
class UserDetails:
    """User submission details"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "Concerned Citizen"
    anonymous: bool = True
    additional_info: str = ""

@dataclass
class IncidentContext:
    """Fixed incident context for the shooting"""
    date: str = "2025-06-17"
    time: str = "14:00"
    location: str = "CBD, Nairobi, Kenya"
    incident: str = "Person shot by GSU (General Service Unit)"
    jurisdiction: str = "Kenya"
    urgency: str = "high"

class AgenticWorkflowChain:
    """
    Multi-step agentic workflow for ICC evidence submission
    Based on app.py's proven workflow pattern with AI enhancements
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.evidence_items: List[EvidenceItem] = []
        self.user_details: Optional[UserDetails] = None
        self.incident_context = IncidentContext()
        self.current_stage = WorkflowStage.UPLOAD
        
        # Initialize session state
        if 'agentic_workflow' not in st.session_state:
            st.session_state.agentic_workflow = {
                'evidence_items': [],
                'user_details': None,
                'current_stage': WorkflowStage.UPLOAD.value,
                'form_data': None,
                'submission_result': None
            }
    
    async def process_evidence_upload(self, uploaded_files: List) -> List[EvidenceItem]:
        """
        STEP 1: Process uploaded files (from app.py pattern)
        Enhanced with async processing and structured data
        """
        evidence_items = []
        
        for file in uploaded_files:
            # Create structured evidence item
            evidence_item = EvidenceItem(
                file_name=file.name,
                file_type=file.type,
                file_size=file.size,
                file_content=file.read(),
                ai_analysis={},  # Will be filled in next step
                timestamp=datetime.now().isoformat(),
                workflow_stage=WorkflowStage.UPLOAD
            )
            
            evidence_items.append(evidence_item)
            
            # Reset file pointer for preview
            file.seek(0)
        
        # Update session state
        st.session_state.agentic_workflow['evidence_items'] = evidence_items
        st.session_state.agentic_workflow['current_stage'] = WorkflowStage.ANALYZE.value
        
        return evidence_items
    
    async def analyze_evidence_with_ai(self, evidence_item: EvidenceItem) -> Dict[str, Any]:
        """
        STEP 2: AI Analysis (Enhanced from app.py's analyze_evidence_with_groq)
        More sophisticated prompting and error handling
        """
        
        # Enhanced prompt based on app.py but with more legal specificity
        prompt = f"""
        You are an expert legal AI assistant specializing in International Criminal Court submissions.
        Analyze this evidence for the confirmed incident in CBD, Nairobi, Kenya.
        
        CONFIRMED INCIDENT DETAILS:
        - Date: {self.incident_context.date}
        - Time: {self.incident_context.time} 
        - Location: {self.incident_context.location}
        - Incident: {self.incident_context.incident}
        - Jurisdiction: {self.incident_context.jurisdiction}
        - Urgency: {self.incident_context.urgency}
        
        EVIDENCE FILE:
        - Name: {evidence_item.file_name}
        - Type: {evidence_item.file_type}
        - Size: {evidence_item.file_size} bytes
        
        Provide comprehensive analysis in this EXACT JSON format:
        {{
            "evidence_type": "Choose: photograph|video|audio|document|witness_statement|other",
            "evidence_description": "Clear, factual 2-3 sentence description",
            "incident_relation": "How this evidence relates to GSU shooting incident",
            "source_description": "How this evidence was likely obtained",
            "relevance_score": "1-10 rating for ICC case relevance",
            "legal_significance": "Why this evidence is legally significant for ICC",
            "suggested_categories": ["human_rights_violation", "excessive_force", "witness_evidence"],
            "recommended_action": "Next steps for this evidence",
            "icc_crimes": ["List potential ICC crimes this evidences"],
            "evidence_quality": "excellent|good|fair|poor",
            "authentication_needs": "What authentication steps are needed",
            "chain_of_custody": "Recommended chain of custody procedures",
            "witness_protection": "Are there witness protection concerns?"
        }}
        
        Focus on human rights violations, excessive use of force, and ICC jurisdiction.
        Be factual and professional for legal proceedings.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",  # Best model for legal reasoning
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert legal AI specializing in ICC evidence analysis. Provide detailed, accurate JSON responses for legal proceedings."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for factual analysis
                max_tokens=1500
            )
            
            # Parse and validate JSON
            analysis = json.loads(response.choices[0].message.content)
            
            # Add AI metadata
            analysis['ai_model'] = "deepseek-r1-distill-llama-70b"
            analysis['analysis_timestamp'] = datetime.now().isoformat()
            analysis['incident_context'] = self.incident_context.__dict__
            
            return analysis
            
        except json.JSONDecodeError as e:
            st.error(f"❌ AI response parsing error: {e}")
            return self._get_fallback_analysis(evidence_item)
        except Exception as e:
            st.error(f"❌ AI analysis error: {e}")
            return self._get_fallback_analysis(evidence_item)
    
    def _get_fallback_analysis(self, evidence_item: EvidenceItem) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        return {
            "evidence_type": "other",
            "evidence_description": f"Evidence file: {evidence_item.file_name}",
            "incident_relation": "Related to GSU shooting incident in CBD, Nairobi",
            "relevance_score": "7",
            "legal_significance": "Potential evidence for human rights violation case",
            "evidence_quality": "good",
            "error": "AI analysis failed - manual review required"
        }
    
    async def accumulate_evidence_analysis(self, evidence_items: List[EvidenceItem]) -> None:
        """
        STEP 3: Accumulate all evidence analyses (Enhanced from app.py pattern)
        Process all evidence items and build comprehensive case
        """
        
        for evidence_item in evidence_items:
            if not evidence_item.ai_analysis:  # Only analyze if not already done
                st.info(f"🤖 Analyzing {evidence_item.file_name} with AI...")
                
                analysis = await self.analyze_evidence_with_ai(evidence_item)
                evidence_item.ai_analysis = analysis
                evidence_item.workflow_stage = WorkflowStage.ACCUMULATE
        
        # Update session state with analyzed evidence
        st.session_state.agentic_workflow['evidence_items'] = evidence_items
        st.session_state.agentic_workflow['current_stage'] = WorkflowStage.USER_DETAILS.value
        
        # Generate case summary
        case_summary = await self._generate_case_summary(evidence_items)
        st.session_state.agentic_workflow['case_summary'] = case_summary
    
    async def _generate_case_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate overall case summary from all evidence"""
        
        all_analyses = [item.ai_analysis for item in evidence_items]
        
        prompt = f"""
        Generate a comprehensive case summary for ICC submission:
        
        INCIDENT: {self.incident_context.incident}
        LOCATION: {self.incident_context.location}
        DATE/TIME: {self.incident_context.date} {self.incident_context.time}
        
        EVIDENCE ANALYSES:
        {json.dumps(all_analyses, indent=2)}
        
        Provide case summary in JSON format:
        {{
            "case_strength": "strong|moderate|weak",
            "primary_crimes": ["List main ICC crimes evidenced"],
            "evidence_overview": "Summary of evidence types and quality",
            "legal_theory": "Legal theory for ICC prosecution",
            "recommended_charges": ["Specific charges to consider"],
            "case_timeline": "Chronological summary of events",
            "witness_considerations": "Witness protection and testimony needs",
            "evidence_gaps": "What additional evidence would strengthen case",
            "urgency_assessment": "Why this case requires urgent attention"
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"Case summary generation failed: {e}"}
    
    def collect_user_details(self, name: str, email: str, phone: str, role: str, 
                           anonymous: bool, additional_info: str) -> UserDetails:
        """
        STEP 4: Collect user details (Enhanced from app.py's submitter_form)
        """
        
        user_details = UserDetails(
            name=name if not anonymous else None,
            email=email if not anonymous else None,
            phone=phone if not anonymous else None,
            role=role,
            anonymous=anonymous,
            additional_info=additional_info
        )
        
        # Store in session state
        st.session_state.agentic_workflow['user_details'] = user_details.__dict__
        st.session_state.agentic_workflow['current_stage'] = WorkflowStage.FORM_GENERATION.value
        
        return user_details
    
    async def generate_icc_form_data(self, evidence_items: List[EvidenceItem], 
                                   user_details: UserDetails) -> Dict[str, Any]:
        """
        STEP 5: Generate ICC form data (Enhanced from app.py's generate_form_data)
        More comprehensive and ICC-specific
        """
        
        # Prepare comprehensive context
        evidence_summaries = []
        for item in evidence_items:
            evidence_summaries.append({
                'file_name': item.file_name,
                'analysis': item.ai_analysis
            })
        
        case_summary = st.session_state.agentic_workflow.get('case_summary', {})
        
        prompt = f"""
        Generate comprehensive ICC submission form data for this critical human rights case:
        
        INCIDENT DETAILS:
        - Date: {self.incident_context.date}
        - Time: {self.incident_context.time}
        - Location: {self.incident_context.location}
        - Incident: {self.incident_context.incident}
        - Jurisdiction: {self.incident_context.jurisdiction}
        
        EVIDENCE SUMMARIES:
        {json.dumps(evidence_summaries, indent=2)}
        
        CASE SUMMARY:
        {json.dumps(case_summary, indent=2)}
        
        USER DETAILS:
        {json.dumps(user_details.__dict__, indent=2)}
        
        Generate complete ICC submission form in JSON format:
        {{
            "submission_title": "Professional title for ICC case",
            "incident_description": "Detailed 300+ word description of incident",
            "incident_date": "{self.incident_context.date}",
            "incident_time": "{self.incident_context.time}",
            "incident_location": "{self.incident_context.location}",
            "jurisdiction": "{self.incident_context.jurisdiction}",
            "alleged_perpetrator": "GSU (General Service Unit) officers",
            "alleged_crimes": ["Specific ICC crimes with legal basis"],
            "victim_information": "Information about victims",
            "witness_information": "Witness details and protection needs",
            "evidence_summary": "Comprehensive evidence description",
            "submitter_role": "{user_details.role}",
            "submitter_protection": "Anonymity and protection needs",
            "urgency_level": "high",
            "legal_basis": "Legal basis for ICC jurisdiction",
            "previous_remedies": "Previous attempts at domestic justice",
            "additional_context": "All additional relevant information",
            "requested_action": "Specific action requested from ICC",
            "supporting_documentation": "List of evidence files and descriptions"
        }}
        
        Make this professional, comprehensive, and legally sound for ICC prosecutors.
        Focus on human rights violations and excessive use of force by state agents.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert legal assistant preparing ICC submissions. Generate comprehensive, professional legal documents."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            form_data = json.loads(response.choices[0].message.content)
            
            # Add metadata
            form_data['generation_timestamp'] = datetime.now().isoformat()
            form_data['ai_model'] = "deepseek-r1-distill-llama-70b"
            form_data['evidence_count'] = len(evidence_items)
            
            # Store in session state
            st.session_state.agentic_workflow['form_data'] = form_data
            st.session_state.agentic_workflow['current_stage'] = WorkflowStage.REVIEW.value
            
            return form_data
            
        except Exception as e:
            st.error(f"❌ Form generation error: {e}")
            return {}
    
    def get_workflow_progress(self) -> Dict[str, Any]:
        """Get current workflow progress for UI display"""
        current_stage = WorkflowStage(st.session_state.agentic_workflow['current_stage'])
        
        stages = list(WorkflowStage)
        current_index = stages.index(current_stage)
        progress = (current_index + 1) / len(stages)
        
        return {
            'current_stage': current_stage.value,
            'current_stage_name': current_stage.value.replace('_', ' ').title(),
            'progress_percent': int(progress * 100),
            'completed_stages': [stage.value for stage in stages[:current_index+1]],
            'next_stage': stages[current_index + 1].value if current_index < len(stages) - 1 else None
        }
    
    def render_workflow_progress(self) -> None:
        """Render workflow progress indicator"""
        progress = self.get_workflow_progress()
        
        st.progress(progress['progress_percent'] / 100)
        st.write(f"**Current Stage:** {progress['current_stage_name']} ({progress['progress_percent']}%)")
        
        # Show completed stages
        completed_stages = " → ".join([stage.replace('_', ' ').title() for stage in progress['completed_stages']])
        st.info(f"**Completed:** {completed_stages}")
        
        if progress['next_stage']:
            st.write(f"**Next:** {progress['next_stage'].replace('_', ' ').title()}")

# Example usage in Streamlit app
def demo_workflow():
    """Demo of the agentic workflow chain"""
    st.title("🇰🇪 Agentic ICC Workflow Chain Demo")
    
    workflow = AgenticWorkflowChain()
    workflow.render_workflow_progress()
    
    current_stage = WorkflowStage(st.session_state.agentic_workflow['current_stage'])
    
    if current_stage == WorkflowStage.UPLOAD:
        st.header("📤 Step 1: Upload Evidence")
        uploaded_files = st.file_uploader("Upload evidence files", accept_multiple_files=True)
        
        if uploaded_files and st.button("Process Uploaded Files"):
            with st.spinner("Processing uploads..."):
                evidence_items = asyncio.run(workflow.process_evidence_upload(uploaded_files))
                st.success(f"✅ {len(evidence_items)} files processed")
                st.rerun()
    
    elif current_stage == WorkflowStage.ANALYZE:
        st.header("🤖 Step 2: AI Evidence Analysis")
        evidence_items = st.session_state.agentic_workflow['evidence_items']
        
        if st.button("Start AI Analysis"):
            with st.spinner("AI analyzing all evidence..."):
                asyncio.run(workflow.accumulate_evidence_analysis(evidence_items))
                st.success("✅ AI analysis complete")
                st.rerun()
    
    # Continue with other stages...

if __name__ == "__main__":
    demo_workflow()
