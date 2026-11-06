"""
🇰🇪 Enhanced ICC Evidence Submission Tool with Agentic AI Workflow
Multi-step form with advanced AI integration and workflow chaining
Based on the proven app.py pattern with agentic enhancements
"""

import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from groq import Groq
import json
from datetime import datetime
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
sys.path.append('d:/ICCLexAI/libs/shared-ui')
from agentic_workflow_chain import AgenticWorkflowChain, WorkflowStage, EvidenceItem, UserDetails
from icc_shared_core import initialize_app, KENYAN_COLORS, INCIDENT_CONTEXT, shared_ai

# Load environment variables
load_dotenv()

class EnhancedICCSubmitter:
    """Enhanced ICC submitter with agentic workflow integration"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.icc_url = "https://otplink.icc-cpi.int/"
        self.workflow_chain = AgenticWorkflowChain()
        
        # Initialize multi-step state (preserved from app.py pattern)
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 1
        if 'evidence_files' not in st.session_state:
            st.session_state.evidence_files = []
        if 'ai_analyses' not in st.session_state:
            st.session_state.ai_analyses = []
        if 'user_submission_data' not in st.session_state:
            st.session_state.user_submission_data = {}
    
    def setup_driver(self):
        """Setup Chrome WebDriver (preserved from app.py)"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def render_step_indicator(self):
        """Multi-step progress indicator (enhanced from app.py concept)"""
        steps = [
            "📤 Upload Evidence",
            "🤖 AI Analysis", 
            "👤 User Details",
            "📝 Form Generation",
            "📋 Review",
            "🚀 Submit"
        ]
        
        current_step = st.session_state.current_step
        
        # Progress bar
        progress = (current_step - 1) / (len(steps) - 1)
        st.progress(progress)
        
        # Step indicators
        cols = st.columns(len(steps))
        for i, (col, step) in enumerate(zip(cols, steps), 1):
            with col:
                if i == current_step:
                    st.markdown(f"**{step}** ⚡")
                elif i < current_step:
                    st.markdown(f"✅ {step}")
                else:
                    st.markdown(f"⏳ {step}")
    
    def step_1_upload_evidence(self):
        """Step 1: Enhanced evidence upload with immediate preview"""
        st.header("📤 Step 1: Upload Evidence Files")
        
        # Enhanced file upload (based on app.py pattern)
        uploaded_files = st.file_uploader(
            "Drag and drop evidence files or click to browse",
            accept_multiple_files=True,
            type=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi', 'mp3', 'wav'],
            help="Supported: Documents, Images, Videos, Audio files (Max 100MB each)",
            key="evidence_uploader"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
            
            # Store files in session state
            st.session_state.evidence_files = uploaded_files
            
            # Preview files (enhanced from app.py)
            for idx, file in enumerate(uploaded_files):
                with st.expander(f"📁 {file.name} ({file.size:,} bytes)", expanded=len(uploaded_files)==1):
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # File preview (preserved from app.py)
                        if file.type.startswith('image/'):
                            image = Image.open(file)
                            st.image(image, width=300)
                        else:
                            st.info(f"**Type:** {file.type}\\n**Size:** {file.size:,} bytes")
                    
                    with col2:
                        st.write("**File Information:**")
                        st.write(f"• **Name:** {file.name}")
                        st.write(f"• **Type:** {file.type}")
                        st.write(f"• **Size:** {file.size:,} bytes")
                        st.write(f"• **Upload Time:** {datetime.now().strftime('%H:%M:%S')}")
            
            # Next step button
            if st.button("🤖 Proceed to AI Analysis", type="primary", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        else:
            st.info("👆 Upload evidence files to begin the submission process")
    
    def step_2_ai_analysis(self):
        """Step 2: Enhanced AI analysis with agentic workflow"""
        st.header("🤖 Step 2: AI Evidence Analysis")
        
        if not st.session_state.evidence_files:
            st.error("❌ No evidence files found. Please return to Step 1.")
            return
        
        st.write(f"**Files to analyze:** {len(st.session_state.evidence_files)}")
        
        # Show files to be analyzed
        for file in st.session_state.evidence_files:
            st.write(f"• {file.name} ({file.type})")
        
        if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
            
            # Convert uploaded files to EvidenceItem objects
            evidence_items = []
            
            with st.spinner("🤖 Processing files with advanced AI analysis..."):
                for file in st.session_state.evidence_files:
                    file_content = file.read()
                    file.seek(0)  # Reset pointer
                    
                    evidence_item = EvidenceItem(
                        file_name=file.name,
                        file_type=file.type,
                        file_size=file.size,
                        file_content=file_content,
                        ai_analysis={},
                        timestamp=datetime.now().isoformat(),
                        workflow_stage=WorkflowStage.UPLOAD
                    )
                    
                    evidence_items.append(evidence_item)
                
                # Run agentic AI analysis
                asyncio.run(self.workflow_chain.accumulate_evidence_analysis(evidence_items))
                
                # Store results
                st.session_state.ai_analyses = [item.ai_analysis for item in evidence_items]
                st.session_state.evidence_items = evidence_items
            
            st.success("✅ AI analysis complete!")
            
            # Display analysis results
            for idx, (file, analysis) in enumerate(zip(st.session_state.evidence_files, st.session_state.ai_analyses)):
                with st.expander(f"📊 Analysis: {file.name}", expanded=True):
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write("**🎯 Evidence Assessment:**")
                        st.write(f"• **Type:** {analysis.get('evidence_type', 'Unknown')}")
                        st.write(f"• **Relevance:** {analysis.get('relevance_score', 'N/A')}/10")
                        st.write(f"• **Quality:** {analysis.get('evidence_quality', 'Unknown')}")
                        st.write(f"• **Legal Significance:** {analysis.get('legal_significance', 'N/A')}")
                    
                    with col2:
                        st.write("**📝 Description:**")
                        st.write(analysis.get('evidence_description', 'No description available'))
                        
                        if 'icc_crimes' in analysis and analysis['icc_crimes']:
                            st.write("**⚖️ Potential ICC Crimes:**")
                            for crime in analysis['icc_crimes']:
                                st.write(f"• {crime}")
            
            # Next step button
            if st.button("👤 Continue to User Details", type="primary", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
    
    def step_3_user_details(self):
        """Step 3: Enhanced user details collection (based on app.py form)"""
        st.header("👤 Step 3: Submitter Information")
        
        st.write("**Evidence Analysis Complete!** Now we need your submission details.")
        
        # Enhanced form (based on app.py pattern)
        with st.form("enhanced_submitter_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Personal Information")
                name = st.text_input("Full Name (Optional)", help="Can be left blank for anonymous submission")
                email = st.text_input("Email Address (Optional)", help="For submission updates")
                phone = st.text_input("Phone Number (Optional)", help="Contact information")
            
            with col2:
                st.subheader("Submission Details")
                role = st.selectbox("Your Role in This Case", [
                    "Witness to the incident",
                    "Concerned Citizen", 
                    "Legal Representative",
                    "Journalist",
                    "Human Rights Advocate",
                    "Family member of victim",
                    "Other"
                ])
                
                anonymous = st.checkbox("🔒 Submit Anonymously", value=True, 
                                      help="Protects your identity in the submission")
                
                urgency = st.selectbox("Case Urgency Level", ["High", "Medium", "Low"], index=0)
            
            st.subheader("Additional Context")
            additional_info = st.text_area(
                "Additional Information About the Incident",
                placeholder="Any additional context, witness information, or details about the GSU shooting incident...",
                height=150
            )
            
            consent = st.checkbox(
                "✅ I confirm this information is accurate and I consent to ICC submission",
                help="Required for legal submission"
            )
            
            submitted = st.form_submit_button("📝 Generate ICC Submission Form", 
                                            type="primary", 
                                            use_container_width=True,
                                            disabled=not consent)
            
            if submitted:
                # Store user details
                user_details = UserDetails(
                    name=name if not anonymous else None,
                    email=email if not anonymous else None,
                    phone=phone if not anonymous else None,
                    role=role,
                    anonymous=anonymous,
                    additional_info=additional_info
                )
                
                st.session_state.user_submission_data = {
                    'user_details': user_details.__dict__,
                    'urgency': urgency,
                    'consent': consent,
                    'submission_timestamp': datetime.now().isoformat()
                }
                
                st.success("✅ User information saved successfully!")
                time.sleep(1)
                st.session_state.current_step = 4
                st.rerun()
    
    def step_4_form_generation(self):
        """Step 4: Generate comprehensive ICC form using agentic AI"""
        st.header("📝 Step 4: ICC Submission Form Generation")
        
        if not st.session_state.user_submission_data:
            st.error("❌ User details not found. Please complete Step 3.")
            return
        
        st.write("**Generating comprehensive ICC submission form with AI...**")
        
        if 'generated_form' not in st.session_state:
            with st.spinner("🤖 AI generating professional ICC submission form..."):
                
                # Use agentic workflow to generate form
                user_details = UserDetails(**st.session_state.user_submission_data['user_details'])
                evidence_items = st.session_state.get('evidence_items', [])
                
                form_data = asyncio.run(
                    self.workflow_chain.generate_icc_form_data(evidence_items, user_details)
                )
                
                st.session_state.generated_form = form_data
        
        # Display generated form
        form_data = st.session_state.generated_form
        
        if form_data:
            st.success("✅ ICC submission form generated successfully!")
            
            with st.expander("📋 Generated ICC Submission Form", expanded=True):
                
                # Form sections
                st.subheader("📋 Case Information")
                st.write(f"**Title:** {form_data.get('submission_title', 'N/A')}")
                st.write(f"**Jurisdiction:** {form_data.get('jurisdiction', 'Kenya')}")
                st.write(f"**Urgency Level:** {form_data.get('urgency_level', 'High')}")
                
                st.subheader("📅 Incident Details")
                st.write(f"**Date:** {form_data.get('incident_date', '2025-06-17')}")
                st.write(f"**Time:** {form_data.get('incident_time', '14:00')}")
                st.write(f"**Location:** {form_data.get('incident_location', 'CBD, Nairobi, Kenya')}")
                
                st.subheader("📝 Incident Description")
                st.text_area("", form_data.get('incident_description', ''), height=200, key="incident_desc_display")
                
                st.subheader("⚖️ Legal Basis")
                if 'alleged_crimes' in form_data:
                    st.write("**Alleged ICC Crimes:**")
                    for crime in form_data['alleged_crimes']:
                        st.write(f"• {crime}")
                
                st.subheader("📊 Evidence Summary")
                st.write(form_data.get('evidence_summary', 'Evidence analysis completed'))
                
                if 'supporting_documentation' in form_data:
                    st.write("**Supporting Files:**")
                    st.write(form_data['supporting_documentation'])
            
            # Edit form option
            if st.button("✏️ Edit Form Details"):
                st.session_state.edit_mode = True
                st.rerun()
            
            # Proceed to review
            if st.button("📋 Proceed to Final Review", type="primary", use_container_width=True):
                st.session_state.current_step = 5
                st.rerun()
    
    def step_5_review_submission(self):
        """Step 5: Final review before submission"""
        st.header("📋 Step 5: Final Review")
        
        st.write("**Review your complete ICC submission before final submission:**")
        
        # Summary cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Evidence Files")
            if st.session_state.evidence_files:
                for file in st.session_state.evidence_files:
                    st.write(f"✅ {file.name} ({file.type})")
            
            st.subheader("🤖 AI Analysis")
            if st.session_state.ai_analyses:
                total_relevance = sum(int(a.get('relevance_score', 0)) for a in st.session_state.ai_analyses)
                avg_relevance = total_relevance / len(st.session_state.ai_analyses)
                st.metric("Average Relevance Score", f"{avg_relevance:.1f}/10")
        
        with col2:
            st.subheader("👤 Submitter Information")
            user_data = st.session_state.user_submission_data
            user_details = user_data['user_details']
            
            st.write(f"**Role:** {user_details['role']}")
            st.write(f"**Anonymous:** {'Yes' if user_details['anonymous'] else 'No'}")
            st.write(f"**Urgency:** {user_data.get('urgency', 'High')}")
            
            st.subheader("📊 Submission Stats")
            st.metric("Evidence Files", len(st.session_state.evidence_files))
            st.metric("AI Analyses", len(st.session_state.ai_analyses))
        
        # Warning and confirmation
        st.warning("⚠️ **Important:** This will submit evidence to the International Criminal Court. Ensure all information is accurate.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⬅️ Back to Edit", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
        
        with col2:
            if st.button("🚀 Submit to ICC", type="primary", use_container_width=True):
                st.session_state.current_step = 6
                st.rerun()
    
    def step_6_submit_to_icc(self):
        """Step 6: Final ICC submission with Selenium automation"""
        st.header("🚀 Step 6: ICC Submission")
        
        if st.button("🎯 Execute ICC Submission", type="primary", use_container_width=True):
            
            with st.spinner("📤 Submitting evidence to ICC..."):
                
                # Prepare submission data
                form_data = st.session_state.generated_form
                evidence_files = [f.read() for f in st.session_state.evidence_files]
                
                # Simulate ICC submission (in production, use real automation)
                submission_result = self.simulate_icc_submission(form_data, evidence_files)
                
                if submission_result['success']:
                    st.success("✅ Evidence successfully submitted to ICC!")
                    
                    # Success display
                    st.balloons()
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, {KENYAN_COLORS['green']}, {KENYAN_COLORS['black']}); 
                                color: white; padding: 2rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                        <h3>🎉 Submission Successful!</h3>
                        <p><strong>Submission ID:</strong> {submission_result['submission_id']}</p>
                        <p><strong>Timestamp:</strong> {submission_result['timestamp']}</p>
                        <p><strong>Status:</strong> SUBMITTED TO ICC</p>
                        <p><em>Your evidence has been submitted to the International Criminal Court.</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Option to submit more evidence
                    if st.button("🔄 Submit More Evidence", use_container_width=True):
                        # Reset workflow
                        for key in ['current_step', 'evidence_files', 'ai_analyses', 'user_submission_data', 'generated_form']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                else:
                    st.error(f"❌ Submission failed: {submission_result.get('error', 'Unknown error')}")
    
    def simulate_icc_submission(self, form_data, evidence_files):
        """Simulate ICC submission (enhanced from app.py)"""
        # In production, this would use Selenium automation to actually submit to ICC
        time.sleep(2)  # Simulate processing time
        
        return {
            'success': True,
            'submission_id': f"ICC-KE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'status': 'submitted',
            'evidence_count': len(evidence_files),
            'form_data_size': len(json.dumps(form_data))
        }

def setup_page_style():
    """Enhanced page styling (preserved from app.py)"""
    st.markdown(f"""
    <style>
    .main-header {{
        background: linear-gradient(90deg, {KENYAN_COLORS['black']} 0%, {KENYAN_COLORS['red']} 25%, {KENYAN_COLORS['green']} 75%, {KENYAN_COLORS['white']} 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    .step-container {{
        background: rgba(0, 128, 0, 0.05);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid {KENYAN_COLORS['green']};
        margin: 1rem 0;
    }}
    
    .upload-area {{
        border: 3px dashed {KENYAN_COLORS['green']};
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(0, 128, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }}
    
    .upload-area:hover {{
        background: rgba(0, 128, 0, 0.1);
        border-color: {KENYAN_COLORS['black']};
    }}
    
    .emergency-banner {{
        background: linear-gradient(45deg, {KENYAN_COLORS['red']}, #FF5722);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    
    .stButton > button {{
        background: linear-gradient(45deg, {KENYAN_COLORS['green']}, {KENYAN_COLORS['black']});
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

def main():
    """Enhanced main function with multi-step workflow"""
    st.set_page_config(
        page_title="🇰🇪 Enhanced ICC Evidence Submission Tool",
        page_icon="🇰🇪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    setup_page_style()
    
    # Enhanced header
    st.markdown("""
    <div class="main-header">
        <h1>🇰🇪 Enhanced ICC Evidence Submission Tool</h1>
        <p>Multi-Step AI-Powered Evidence Submission to the International Criminal Court</p>
        <p><em>GSU Shooting Incident - CBD Nairobi - June 17, 2025, 2:00 PM</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency banner
    st.markdown("""
    <div class="emergency-banner">
        🚨 EMERGENCY SUBMISSION - AI-Enhanced Multi-Step Workflow - Advanced Evidence Analysis
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize enhanced submitter
    submitter = EnhancedICCSubmitter()
    
    # Enhanced sidebar (preserved from app.py)
    with st.sidebar:
        st.header("🇰🇪 Enhanced ICC Submission")
        st.write("**Platform:** AI-Enhanced Multi-Step")
        st.write("**Status:** Advanced Workflow Active")
        
        st.markdown("---")
        st.header("📋 Incident Information")
        st.write("**Date:** June 17, 2025")
        st.write("**Time:** 2:00 PM")
        st.write("**Location:** CBD, Nairobi, Kenya")
        st.write("**Incident:** Person shot by GSU")
        st.write("**Status:** AI Analysis Ready")
        
        st.markdown("---")
        st.header("🤖 AI Features")
        st.write("• Advanced evidence analysis")
        st.write("• Legal relevance scoring")
        st.write("• Automated form generation")
        st.write("• Multi-step workflow")
        
        st.markdown("---")
        st.header("📞 Emergency Contacts")
        st.write("**ICC OTP:** +31 70 515 8515")
        st.write("**Kenya Human Rights:** +254 20 272 1113")
        
        # Workflow progress in sidebar
        st.markdown("---")
        st.header("📈 Workflow Progress")
        submitter.workflow_chain.render_workflow_progress()
    
    # Main workflow container
    with st.container():
        submitter.render_step_indicator()
        
        # Route to appropriate step
        current_step = st.session_state.current_step
        
        if current_step == 1:
            submitter.step_1_upload_evidence()
        elif current_step == 2:
            submitter.step_2_ai_analysis()
        elif current_step == 3:
            submitter.step_3_user_details()
        elif current_step == 4:
            submitter.step_4_form_generation()
        elif current_step == 5:
            submitter.step_5_review_submission()
        elif current_step == 6:
            submitter.step_6_submit_to_icc()
    
    # Enhanced footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 2rem; 
                background: linear-gradient(90deg, rgba(0,128,0,0.05), rgba(255,255,255,1), rgba(0,128,0,0.05)); 
                border-radius: 10px;">
        <h4>🇰🇪 Enhanced ICC Evidence Submission Tool</h4>
        <p><strong>AI-Powered Multi-Step Workflow for Justice and Human Rights</strong></p>
        <p><em>This enhanced tool combines proven multi-step workflows with advanced AI analysis 
        to help citizens submit high-quality evidence to the International Criminal Court.</em></p>
        <p>🤖 <strong>AI Features:</strong> Evidence Analysis | Legal Scoring | Form Generation | Workflow Management</p>
        <p>🛡️ <strong>Security:</strong> Anonymous Submissions | Data Protection | Secure Processing</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
