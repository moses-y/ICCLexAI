#!/usr/bin/env python3
"""
🔍 Human Validation Agent - Critical ICC Evidence Review System
Ensures all AI-generated ICC submissions are human-verified before submission
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ValidationChange:
    """Track human edits during validation"""
    field: str
    original_value: str
    edited_value: str
    timestamp: str
    validation_notes: str = ""

@dataclass
class ValidationResult:
    """Complete validation session result"""
    submission_id: str
    validation_timestamp: str
    human_validator: str
    validation_changes: List[ValidationChange]
    final_approval: bool
    validation_notes: str
    confidence_score: float

class HumanValidationAgent:
    """🔍 ICC Evidence Human Validation System"""
    
    def __init__(self):
        self.validation_history = []
        self.current_session = None
        
    def initialize_validation_session(self, evidence_analyses: List[Dict], 
                                    ai_generated_context: str, 
                                    form_data: Dict) -> str:
        """🚀 Start a new human validation session"""
        
        session_id = f"VAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.current_session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'evidence_count': len(evidence_analyses),
            'original_context': ai_generated_context,
            'original_form_data': form_data,
            'validation_changes': [],
            'status': 'pending_validation'
        }
        
        return session_id
    
    def render_validation_interface(self, evidence_analyses: List[Dict], 
                                  ai_context: str, 
                                  form_data: Dict) -> Tuple[Dict, str, bool]:
        """🎯 Render complete human validation interface"""
        
        st.markdown("""
        <div style="background: linear-gradient(90deg, #006633, #000000); 
                    color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;
                    text-align: center;">
            <h2>🔍 HUMAN VALIDATION REQUIRED</h2>
            <p><strong>⚖️ International Criminal Court Evidence Review</strong></p>
            <p>Please review and edit the AI-generated submission before final approval</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Validation tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Form Data Review", 
            "📝 Context Review", 
            "📁 Evidence Summary", 
            "✅ Final Approval"
        ])
        
        validated_form_data = form_data.copy()
        validated_context = ai_context
        
        with tab1:
            st.subheader("📋 ICC Form Data Validation")
            st.info("Review and edit AI-generated form fields. All changes are tracked.")
            
            validated_form_data = self._render_form_validation(form_data)
        
        with tab2:
            st.subheader("📝 ICC Context Validation")
            st.info("Review and edit the AI-generated 1000+ word ICC submission context.")
            
            validated_context = self._render_context_validation(ai_context)
        
        with tab3:
            st.subheader("📁 Evidence Analysis Review")
            st.info("Review AI analysis of each evidence file.")
            
            self._render_evidence_validation(evidence_analyses)
        
        with tab4:
            st.subheader("✅ Final Approval & Submission")
            
            approval_result = self._render_final_approval()
            
            return validated_form_data, validated_context, approval_result
        
        return validated_form_data, validated_context, False
    
    def _render_form_validation(self, form_data: Dict) -> Dict:
        """📋 Human validation of ICC form fields"""
        
        validated_data = {}
        
        st.markdown("### 🎯 Critical ICC Form Fields")
        
        # Incident details validation
        col1, col2 = st.columns(2)
        
        with col1:
            validated_data['incident_date'] = st.date_input(
                "📅 Incident Date", 
                value=datetime.fromisoformat(form_data.get('incident_date', '2025-06-17')).date(),
                help="Verify the incident date is accurate"
            )
            
            validated_data['incident_location'] = st.text_input(
                "📍 Incident Location", 
                value=form_data.get('incident_location', ''),
                help="Edit location details if needed"
            )
            
            validated_data['urgency_level'] = st.selectbox(
                "🚨 Urgency Level",
                options=["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(form_data.get('urgency_level', 'High')),
                help="Adjust urgency based on evidence severity"
            )
        
        with col2:
            validated_data['incident_time'] = st.time_input(
                "🕐 Incident Time",
                help="Verify incident timing"
            )
            
            validated_data['submitter_role'] = st.selectbox(
                "👤 Submitter Role",
                options=["Witness", "Victim", "Legal Representative", "Human Rights Advocate", "Journalist"],
                index=0,
                help="Your role in relation to this incident"
            )
        
        # Core descriptions
        st.markdown("### 📝 Incident Descriptions")
        
        validated_data['incident_description'] = st.text_area(
            "📝 Incident Description",
            value=form_data.get('incident_description', ''),
            height=150,
            help="Edit and enhance the AI-generated incident description",
            max_chars=2000
        )
        
        validated_data['victim_info'] = st.text_area(
            "👥 Victim Information",
            value=form_data.get('victim_info', ''),
            height=100,
            help="Add or edit victim details (maintain privacy as needed)"
        )
        
        validated_data['perpetrator_info'] = st.text_area(
            "👮 Perpetrator Information",
            value=form_data.get('perpetrator_info', ''),
            height=100,
            help="Add or edit perpetrator details"
        )
        
        validated_data['witness_info'] = st.text_area(
            "👁️ Witness Information",
            value=form_data.get('witness_info', ''),
            height=100,
            help="Add witness details (contact info optional)"
        )
        
        # Evidence summary
        validated_data['evidence_summary'] = st.text_area(
            "📋 Evidence Summary",
            value=form_data.get('evidence_summary', ''),
            height=120,
            help="Edit AI-generated evidence summary"
        )
        
        # Track changes
        if form_data != validated_data:
            st.success("✏️ Form modifications detected and saved")
            self._track_validation_changes(form_data, validated_data, "form_data")
        
        return validated_data
    
    def _render_context_validation(self, ai_context: str) -> str:
        """📝 Human validation of AI-generated context"""
        
        st.markdown("### 🎯 AI-Generated ICC Submission Context")
        st.info(f"Context length: {len(ai_context)} characters (~{len(ai_context.split())} words)")
        
        # Show original AI context in expandable section
        with st.expander("🤖 View Original AI-Generated Context", expanded=False):
            st.text_area("Original AI Context", value=ai_context, height=300, disabled=True)
        
        # Editable version
        st.markdown("#### ✏️ Edit Context (Required for ICC Submission)")
        validated_context = st.text_area(
            "ICC Submission Context",
            value=ai_context,
            height=400,
            help="Review and edit the AI-generated context. Ensure accuracy, completeness, and legal appropriateness.",
            max_chars=5000,
            key="context_editor"
        )
        
        # Context quality metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            word_count = len(validated_context.split())
            st.metric("📊 Word Count", word_count)
            if word_count < 500:
                st.warning("⚠️ Context may be too brief for ICC submission")
            elif word_count > 2000:
                st.warning("⚠️ Context may be too lengthy")
            else:
                st.success("✅ Appropriate length")
        
        with col2:
            changes_made = len(validated_context) != len(ai_context)
            st.metric("✏️ Human Edits", "Yes" if changes_made else "No")
        with col3:
            st.slider("🎯 Context Quality Score", 1, 10, 8, 
                                     help="Rate the overall quality of this context (1=Poor, 10=Excellent)")
        
        # Track context changes
        if validated_context != ai_context:
            st.success("✏️ Context modifications detected and saved")
            self._track_validation_changes(
                {"context": ai_context}, 
                {"context": validated_context}, 
                "context"
            )
        
        return validated_context
    
    def _render_evidence_validation(self, evidence_analyses: List[Dict]):
        """📁 Human validation of evidence analysis"""
        
        st.markdown("### 🔍 Evidence Analysis Review")
        
        for i, evidence in enumerate(evidence_analyses):
            with st.expander(f"📄 Evidence {i+1}: {evidence.get('filename', 'Unknown')}"):
                
                col1, col2 = st.columns([2, 1])                
                with col1:
                    st.markdown(f"**File Type:** {evidence.get('file_type', 'Unknown')}")
                    st.markdown(f"**AI Analysis:** {evidence.get('ai_description', 'No analysis available')}")
                    
                    if evidence.get('metadata'):
                        st.markdown("**Metadata:**")
                        for key, value in evidence['metadata'].items():
                            st.text(f"• {key}: {value}")
                
                with col2:
                    st.selectbox(
                        "Legal Relevance",
                        options=["High", "Medium", "Low"],
                        index=["High", "Medium", "Low"].index(evidence.get('legal_relevance', 'High')),
                        key=f"relevance_{i}"
                    )
                    
                    st.selectbox(
                        "Evidence Quality",
                        options=["Excellent", "Good", "Fair", "Poor"],
                        index=["Excellent", "Good", "Fair", "Poor"].index(evidence.get('evidence_quality', 'Good')),
                        key=f"quality_{i}"
                    )
                    
                    st.checkbox(
                        "Include in Submission",
                        value=True,
                        key=f"include_{i}",
                        help="Uncheck to exclude this evidence"
                    )
                
                # Human notes for this evidence
                st.text_area(
                    f"Validation Notes for Evidence {i+1}",
                    placeholder="Add any notes about this evidence...",
                    height=80,
                    key=f"notes_{i}"
                )
    
    def _render_final_approval(self) -> bool:
        """✅ Final human approval interface"""
        
        st.markdown("### 🎯 Final Validation & Approval")
        
        # Pre-submission checklist
        st.markdown("#### ✅ Pre-Submission Checklist")
        
        checklist_items = [
            "All form fields have been reviewed and are accurate",
            "The ICC submission context has been reviewed and edited as needed",
            "All evidence files have been validated for legal relevance",
            "Sensitive information has been appropriately handled",
            "The submission meets ICC evidence requirements",
            "I confirm this evidence relates to alleged crimes within ICC jurisdiction"
        ]
        
        all_checked = True
        for i, item in enumerate(checklist_items):
            checked = st.checkbox(item, key=f"checklist_{i}")
            if not checked:
                all_checked = False
        
        # Validator information
        st.markdown("#### 👤 Validator Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            validator_name = st.text_input(
                "Your Name/Organization",
                placeholder="Enter your name or organization",
                help="This will be recorded with the validation"
            )
            
        with col2:
            validation_notes = st.text_area(
                "Final Validation Notes",
                placeholder="Any final notes about this submission...",
                height=100
            )
        
        # Final approval buttons
        if all_checked and validator_name:
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ APPROVE & SUBMIT TO ICC", type="primary", use_container_width=True):
                    self._record_validation_approval(validator_name, validation_notes, True)
                    st.success("🎉 Submission approved! Proceeding to ICC...")
                    return True
            
            with col2:
                if st.button("📋 SAVE FOR LATER REVIEW", use_container_width=True):
                    self._record_validation_approval(validator_name, validation_notes, False)
                    st.info("💾 Validation saved. You can continue later.")
                    return False
            
            with col3:
                if st.button("❌ REJECT SUBMISSION", use_container_width=True):
                    st.error("🚫 Submission rejected. Please review and improve evidence.")
                    return False
        
        else:
            st.warning("⚠️ Please complete the checklist and provide validator information before proceeding.")
            return False
        
        return False
    
    def _track_validation_changes(self, original: Dict, validated: Dict, field_type: str):
        """📊 Track all human changes during validation"""
        
        changes = []
        
        if field_type == "form_data":
            for key in original.keys():
                if str(original.get(key, '')) != str(validated.get(key, '')):
                    change = ValidationChange(
                        field=key,
                        original_value=str(original.get(key, '')),
                        edited_value=str(validated.get(key, '')),
                        timestamp=datetime.now().isoformat()
                    )
                    changes.append(change)
        
        elif field_type == "context":
            if original['context'] != validated['context']:
                change = ValidationChange(
                    field="submission_context",
                    original_value=original['context'][:100] + "...",  # Truncated for storage
                    edited_value=validated['context'][:100] + "...",
                    timestamp=datetime.now().isoformat()
                )
                changes.append(change)
        
        if self.current_session:
            self.current_session['validation_changes'].extend(changes)
    
    def _record_validation_approval(self, validator_name: str, notes: str, approved: bool):
        """📋 Record final validation decision"""
        
        if self.current_session:
            self.current_session.update({
                'validator_name': validator_name,
                'validation_notes': notes,
                'final_approval': approved,
                'completion_time': datetime.now().isoformat(),
                'status': 'approved' if approved else 'saved_for_review'
            })
            
            # Store in session state for tracking
            if 'validation_history' not in st.session_state:
                st.session_state.validation_history = []
            
            st.session_state.validation_history.append(self.current_session)
    
    def get_validation_summary(self) -> Dict:
        """📊 Get validation session summary"""
        
        if not self.current_session:
            return {}
        
        return {
            'session_id': self.current_session['session_id'],
            'validation_time': self.current_session.get('completion_time', ''),
            'changes_made': len(self.current_session.get('validation_changes', [])),
            'final_approval': self.current_session.get('final_approval', False),
            'validator': self.current_session.get('validator_name', 'Unknown')
        }

def render_validation_badge(validation_required: bool = True):
    """🔍 Render validation requirement badge"""
    
    if validation_required:
        st.markdown("""
        <div style="background: #ff6b6b; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
            <strong>⚠️ HUMAN VALIDATION REQUIRED</strong><br>
            This AI-generated submission must be reviewed by a human before ICC submission
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #51cf66; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center;">
            <strong>✅ HUMAN VALIDATION COMPLETE</strong><br>
            This submission has been reviewed and approved for ICC submission
        </div>
        """, unsafe_allow_html=True)

def create_validation_workflow_demo():
    """🎯 Demo the human validation workflow"""
    
    st.title("🔍 ICC Human Validation Workflow Demo")
    
    # Sample data for demo
    sample_evidence = [
        {
            'filename': 'protest_photo.jpg',
            'file_type': 'image',
            'ai_description': 'Photograph showing law enforcement officers and civilians in an urban setting',
            'legal_relevance': 'High',
            'evidence_quality': 'Good',
            'metadata': {
                'gps_coords': '(-1.2921, 36.8219)',
                'timestamp': '2025-06-17 14:00:00',
                'device': 'iPhone 12'
            }
        }
    ]
    
    sample_context = """
    EXECUTIVE SUMMARY
    
    This submission documents evidence of alleged excessive use of force by law enforcement officers during a peaceful demonstration in Nairobi CBD on June 17, 2025. The evidence includes photographic documentation, witness statements, and metadata confirming the time and location of the incident.
    
    EVIDENCE ANALYSIS
    
    The submitted photograph shows clear evidence of law enforcement engagement with civilians in an urban setting. GPS metadata confirms the location as Nairobi CBD, with timestamp data indicating the incident occurred at approximately 2:00 PM on the date in question.
    
    LEGAL SIGNIFICANCE
    
    The evidence suggests potential violations of international human rights law relating to the right to peaceful assembly and freedom from excessive force. The documentation meets evidentiary standards for preliminary examination by the International Criminal Court.
    
    RECOMMENDED ACTION
    
    This evidence warrants inclusion in official ICC documentation and should be preserved according to chain of custody requirements for international legal proceedings.
    """
    
    sample_form_data = {
        'incident_date': '2025-06-17',
        'incident_location': 'CBD, Nairobi, Kenya',
        'incident_description': 'Person shot by GSU during peaceful demonstration',
        'victim_info': 'Civilian participant in peaceful demonstration',
        'perpetrator_info': 'GSU (General Service Unit) officers',
        'witness_info': 'Multiple witnesses present at scene',
        'urgency_level': 'High',
        'evidence_summary': 'Photographic evidence with GPS and timestamp metadata'
    }
    
    # Initialize validation agent
    validator = HumanValidationAgent()
    session_id = validator.initialize_validation_session(sample_evidence, sample_context, sample_form_data)
    
    st.info(f"🎯 Validation Session: {session_id}")
    
    # Render validation interface
    validated_form, validated_context, approval = validator.render_validation_interface(
        sample_evidence, sample_context, sample_form_data
    )
    
    if approval:
        st.balloons()
        validation_summary = validator.get_validation_summary()
        st.success(f"🎉 Submission validated and approved! Session: {validation_summary['session_id']}")

if __name__ == "__main__":
    create_validation_workflow_demo()
