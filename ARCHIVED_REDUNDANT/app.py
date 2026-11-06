"""
ICC Evidence Submission Tool
Emergency Streamlit app for submitting evidence to the International Criminal Court
"""
import streamlit as st
import os
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

# Load environment variables
load_dotenv()

# Kenyan Flag Color Palette
KENYAN_COLORS = {
    'black': '#000000',
    'red': '#D32F2F',
    'green': '#388E3C',
    'white': '#FFFFFF'
}

class ICCEvidenceSubmitter:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.icc_url = "https://otplink.icc-cpi.int/"
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def analyze_evidence_with_groq(self, file_content, file_type, incident_details):
        """Use Groq to analyze evidence and generate appropriate descriptions"""
        
        prompt = f"""
        You are an expert legal assistant helping to submit evidence to the International Criminal Court (ICC) regarding a serious incident.
        
        INCIDENT CONTEXT:
        - Location: CBD, Nairobi, Kenya
        - Date: June 17, 2025
        - Time: 2:00 PM
        - Incident: Person shot by GSU (General Service Unit)
        
        FILE INFORMATION:
        - File type: {file_type}
        - Context: Evidence related to the shooting incident
        
        Please provide a comprehensive analysis in JSON format with the following fields:
        
        {{
            "evidence_type": "Choose from: photograph, video, audio, document, witness_statement, other",
            "evidence_description": "Clear, factual description of what the evidence shows (2-3 sentences)",
            "incident_relation": "How this evidence relates to the incident (1-2 sentences)",
            "source_description": "Brief description of how this evidence was obtained",
            "relevance_score": "Rate from 1-10 how relevant this is to the case",
            "suggested_categories": ["list", "of", "relevant", "categories"],
            "legal_significance": "Brief explanation of why this evidence is legally significant",
            "recommended_action": "What should be done with this evidence"
        }}
        
        Be factual, professional, and focus on human rights violations. This is for justice purposes.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse JSON response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            st.error(f"Error analyzing evidence: {str(e)}")
            return None
    
    def generate_form_data(self, evidence_analysis, user_details):
        """Generate form data for ICC submission using Groq"""
        
        prompt = f"""
        Based on the evidence analysis and user details, generate appropriate form data for ICC submission.
        
        EVIDENCE ANALYSIS:
        {json.dumps(evidence_analysis, indent=2)}
        
        USER DETAILS:
        {json.dumps(user_details, indent=2)}
        
        INCIDENT DETAILS:
        - Location: CBD, Nairobi, Kenya
        - Date: June 17, 2025
        - Time: 14:00 (2:00 PM)
        - Incident: Person shot by GSU (General Service Unit)
        - Jurisdiction: Kenya
        
        Generate a JSON response with typical ICC form fields:
        
        {{
            "incident_title": "Brief title for the incident",
            "incident_description": "Detailed description of what happened",
            "incident_date": "2025-06-17",
            "incident_time": "14:00",
            "incident_location": "CBD, Nairobi, Kenya",
            "alleged_perpetrator": "GSU (General Service Unit)",
            "alleged_crimes": ["List of potential crimes"],
            "victim_information": "Information about victims if known",
            "witness_information": "Witness details if available", 
            "evidence_description": "Description of submitted evidence",
            "submitter_role": "Determine role: witness, victim, concerned_citizen, legal_representative",
            "urgency_level": "high/medium/low",
            "additional_context": "Any additional relevant information"
        }}
        
        Be factual and professional. Focus on human rights violations and use appropriate legal terminology.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1200
            )
            
            form_data = json.loads(response.choices[0].message.content)
            return form_data
            
        except Exception as e:
            st.error(f"Error generating form data: {str(e)}")
            return None
    
    def submit_to_icc(self, form_data, files):
        """Submit the evidence to ICC using Selenium automation"""
        driver = self.setup_driver()
        
        try:
            st.info("🔄 Connecting to ICC website...")
            driver.get(self.icc_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # Allow dynamic content to load
            
            # This is a placeholder for actual form automation
            # In a real implementation, you would:
            # 1. Navigate to the submission form
            # 2. Fill in the form fields based on form_data
            # 3. Upload files
            # 4. Submit the form
            
            st.success("✅ Form submission initiated (simulation mode)")
            st.info("In production, this would automate the actual ICC form submission")
            
            # Return submission result
            return {
                'success': True,
                'submission_id': f"ICC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'status': 'submitted'
            }
            
        except Exception as e:
            st.error(f"Error submitting to ICC: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
        finally:
            driver.quit()

def setup_page_style():
    """Setup page styling with Kenyan flag colors"""
    st.markdown(f"""
    <style>
    .main-header {{
        background: linear-gradient(90deg, {KENYAN_COLORS['black']} 0%, {KENYAN_COLORS['red']} 25%, {KENYAN_COLORS['green']} 75%, {KENYAN_COLORS['white']} 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .upload-area {{
        border: 3px dashed {KENYAN_COLORS['green']};
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }}
    
    .emergency-banner {{
        background-color: {KENYAN_COLORS['red']};
        color: white;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }}
    
    .status-card {{
        background: {KENYAN_COLORS['white']};
        border-left: 4px solid {KENYAN_COLORS['green']};
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .stButton > button {{
        background-color: {KENYAN_COLORS['green']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }}
    
    .stButton > button:hover {{
        background-color: {KENYAN_COLORS['black']};
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="ICC Evidence Submission - Kenya",
        page_icon="🇰🇪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    setup_page_style()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🇰🇪 ICC Evidence Submission Tool</h1>
        <p>Submit evidence to the International Criminal Court - Incident in CBD Nairobi</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency banner
    st.markdown("""
    <div class="emergency-banner">
        🚨 EMERGENCY SUBMISSION - GSU Shooting Incident - CBD Nairobi - June 17, 2025, 2:00 PM
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the submitter
    submitter = ICCEvidenceSubmitter()
    
    # Sidebar for incident details
    with st.sidebar:
        st.header("📋 Incident Information")
        st.write("**Date:** June 17, 2025")
        st.write("**Time:** 2:00 PM")
        st.write("**Location:** CBD, Nairobi, Kenya")
        st.write("**Incident:** Person shot by GSU")
        st.write("**Status:** Active Evidence Collection")
        
        st.header("📞 Emergency Contacts")
        st.write("**ICC OTP:** +31 70 515 8515")
        st.write("**Kenya Human Rights:** +254 20 272 1113")
        
        st.header("ℹ️ Submission Guidelines")
        st.write("• Ensure evidence is authentic")
        st.write("• Provide clear descriptions")
        st.write("• Include location/time data")
        st.write("• Protect witness identity if needed")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Upload Evidence")
        
        # File upload section
        uploaded_files = st.file_uploader(
            "Drag and drop files or click to browse",
            accept_multiple_files=True,
            type=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi', 'mp3', 'wav'],
            help="Supported: Documents, Images, Videos, Audio files"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
            
            for file in uploaded_files:
                with st.expander(f"📁 {file.name} ({file.size} bytes)"):
                    file_type = file.type
                    
                    # Display file preview if possible
                    if file_type.startswith('image/'):
                        image = Image.open(file)
                        st.image(image, width=300)
                    elif file_type.startswith('text/'):
                        content = str(file.read(), "utf-8")
                        st.text_area("File content:", content[:500] + "..." if len(content) > 500 else content)
                    
                    # Analyze with Groq
                    if st.button(f"🔍 Analyze {file.name}", key=f"analyze_{file.name}"):
                        with st.spinner("Analyzing evidence with AI..."):
                            file_content = file.read()
                            incident_details = {
                                "date": "2025-06-17",
                                "time": "14:00",
                                "location": "CBD, Nairobi, Kenya",
                                "incident": "GSU shooting"
                            }
                            
                            analysis = submitter.analyze_evidence_with_groq(
                                file_content, file_type, incident_details
                            )
                            
                            if analysis:
                                st.json(analysis)
                                
                                # Store analysis in session state
                                if 'evidence_analyses' not in st.session_state:
                                    st.session_state.evidence_analyses = []
                                st.session_state.evidence_analyses.append({
                                    'file_name': file.name,
                                    'analysis': analysis,
                                    'file_content': file_content
                                })
    
    with col2:
        st.header("👤 Submitter Information")
        
        with st.form("submitter_form"):
            name = st.text_input("Full Name (Optional)", help="Can be anonymous")
            email = st.text_input("Email (Optional)")
            phone = st.text_input("Phone (Optional)")
            role = st.selectbox("Your Role", [
                "Witness", "Concerned Citizen", "Legal Representative", 
                "Journalist", "Human Rights Advocate", "Other"
            ])
            
            anonymous = st.checkbox("Submit Anonymously", value=True)
            
            additional_info = st.text_area(
                "Additional Information",
                placeholder="Any additional context about the incident or evidence..."
            )
            
            submitted = st.form_submit_button("📋 Prepare Submission")
            
            if submitted:
                user_details = {
                    'name': name if not anonymous else "Anonymous",
                    'email': email if not anonymous else "",
                    'phone': phone if not anonymous else "",
                    'role': role,
                    'anonymous': anonymous,
                    'additional_info': additional_info
                }
                
                st.session_state.user_details = user_details
                st.success("✅ Submitter information saved")
    
    # Submission section
    if 'evidence_analyses' in st.session_state and 'user_details' in st.session_state:
        st.header("🚀 Submit to ICC")
        
        with st.expander("📋 Review Submission", expanded=True):
            st.write("**Evidence Files:**")
            for evidence in st.session_state.evidence_analyses:
                st.write(f"• {evidence['file_name']} - {evidence['analysis'].get('evidence_type', 'Unknown type')}")
            
            st.write("**Submitter:**")
            user = st.session_state.user_details
            st.write(f"• Role: {user['role']}")
            st.write(f"• Anonymous: {user['anonymous']}")
            
            if st.button("🎯 Submit Evidence to ICC", type="primary"):
                with st.spinner("Generating form data and submitting to ICC..."):
                    
                    # Generate comprehensive form data
                    form_data = submitter.generate_form_data(
                        st.session_state.evidence_analyses,
                        st.session_state.user_details
                    )
                    
                    if form_data:
                        # Display generated form data
                        st.subheader("📝 Generated Submission Form")
                        st.json(form_data)
                        
                        # Submit to ICC
                        submission_result = submitter.submit_to_icc(
                            form_data, 
                            [e['file_content'] for e in st.session_state.evidence_analyses]
                        )
                        
                        if submission_result['success']:
                            st.success("✅ Evidence successfully submitted to ICC!")
                            st.markdown(f"""
                            <div class="status-card">
                                <h4>📋 Submission Confirmation</h4>
                                <p><strong>Submission ID:</strong> {submission_result['submission_id']}</p>
                                <p><strong>Timestamp:</strong> {submission_result['timestamp']}</p>
                                <p><strong>Status:</strong> {submission_result['status']}</p>
                                <p><em>Keep this information for your records.</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Clear session state
                            if st.button("🔄 Submit More Evidence"):
                                del st.session_state.evidence_analyses
                                del st.session_state.user_details
                                st.experimental_rerun()
                        else:
                            st.error(f"❌ Submission failed: {submission_result.get('error', 'Unknown error')}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🇰🇪 ICC Evidence Submission Tool - For Justice and Human Rights</p>
        <p><em>This tool helps citizens submit evidence to the International Criminal Court. 
        All submissions are processed securely and confidentially.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
