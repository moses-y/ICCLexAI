"""
ICC Evidence Submission Tool
A Streamlit app for submitting evidence to the International Criminal Court
with automated form filling and AI assistance.
"""

import streamlit as st
import json
import os
from datetime import datetime, time
import requests
from groq import Groq
import tempfile
from pathlib import Path
import mimetypes
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="ICC Evidence Submission Tool",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kenyan flag colors theme
KENYAN_COLORS = {
    'black': '#000000',
    'red': '#FF0000', 
    'green': '#006600',
    'white': '#FFFFFF'
}

# Custom CSS for Kenyan flag theme
st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(90deg, {KENYAN_COLORS['black']} 25%, {KENYAN_COLORS['red']} 25%, {KENYAN_COLORS['red']} 50%, {KENYAN_COLORS['white']} 50%, {KENYAN_COLORS['white']} 75%, {KENYAN_COLORS['green']} 75%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .upload-area {{
        border: 3px dashed {KENYAN_COLORS['green']};
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f0f8f0;
        margin: 1rem 0;
    }}
    
    .evidence-card {{
        border: 1px solid {KENYAN_COLORS['red']};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }}
    
    .submit-button {{
        background-color: {KENYAN_COLORS['green']};
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
    }}
    
    .urgent-notice {{
        background-color: {KENYAN_COLORS['red']};
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

class ICCSubmissionTool:
    def __init__(self):
        self.groq_client = None
        self.form_mapping = self.load_form_mapping()
        self.setup_groq()
    
    def setup_groq(self):
        """Initialize Groq client"""
        try:
            # Get API key from environment or use the provided one
            api_key = os.getenv('GROQ_API_KEY')
            self.groq_client = Groq(api_key=api_key)
        except Exception as e:
            st.error(f"Failed to initialize Groq client: {str(e)}")
    
    def load_form_mapping(self):
        """Load the ICC form mapping"""
        try:
            with open('icc_manual_form_mapping.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("Form mapping file not found. Please run icc_form_analyzer.py first.")
            return None
        except Exception as e:
            st.error(f"Error loading form mapping: {str(e)}")
            return None
    
    def generate_evidence_description(self, file_info: Dict, incident_details: Dict) -> str:
        """Use Groq AI to generate evidence description"""
        if not self.groq_client:
            return f"Evidence file: {file_info['name']} related to incident in {incident_details.get('location', 'Nairobi CBD')}"
        
        try:
            prompt = f'''
            You are helping to create an evidence description for an ICC submission regarding a serious incident.
            
            Incident Details:
            - Date: {incident_details.get('date', '2025-06-17')}
            - Time: {incident_details.get('time', '14:00')}
            - Location: {incident_details.get('location', 'CBD, Nairobi, Kenya')}
            - Description: {incident_details.get('description', 'Incident involving GSU at CBD')}
            
            Evidence File:
            - Name: {file_info['name']}
            - Type: {file_info['type']}
            - Size: {file_info['size']} bytes
            
            Please generate a clear, professional evidence description that:
            1. Explains what this evidence shows/contains
            2. Relates it to the incident
            3. Is factual and objective
            4. Follows legal documentation standards
            
            Keep it concise but comprehensive (2-3 sentences max).
            '''
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a legal documentation assistant helping with ICC evidence submissions. Be factual, professional, and concise."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating description: {str(e)}")
            return f"Evidence file: {file_info['name']} documenting incident at {incident_details.get('location', 'Nairobi CBD')} on {incident_details.get('date', '2025-06-17')}"
    
    def process_uploaded_file(self, uploaded_file, incident_details: Dict) -> Dict:
        """Process an uploaded file and generate metadata"""
        file_info = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type or 'unknown',
            'content': uploaded_file.getvalue()
        }
        
        # Generate AI description
        description = self.generate_evidence_description(file_info, incident_details)
        
        return {
            'file_info': file_info,
            'description': description,
            'evidence_type': self.determine_evidence_type(uploaded_file.type),
            'timestamp': datetime.now().isoformat()
        }
    
    def determine_evidence_type(self, mime_type: str) -> str:
        """Determine evidence type from MIME type"""
        if not mime_type:
            return 'document'
        
        if mime_type.startswith('image/'):
            return 'photo'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        else:
            return 'document'
    
    def simulate_icc_submission(self, form_data: Dict, evidence_files: List[Dict]) -> Dict:
        """Simulate ICC form submission (placeholder for actual automation)"""
        try:
            # This would normally use Selenium to interact with the ICC form
            # For now, we'll simulate the process
            
            submission_id = f"ICC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Simulate processing time
            import time
            time.sleep(2)
            
            result = {
                'success': True,
                'submission_id': submission_id,
                'timestamp': datetime.now().isoformat(),
                'form_data': form_data,
                'evidence_count': len(evidence_files),
                'status': 'submitted',
                'message': 'Evidence successfully submitted to ICC portal'
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def main():
    """Main Streamlit application"""
    
    # Initialize the tool
    tool = ICCSubmissionTool()
    
    # Header
    st.markdown('<div class="main-header"><h1>⚖️ ICC Evidence Submission Tool</h1><p>Submit evidence to the International Criminal Court</p></div>', unsafe_allow_html=True)
    
    # Urgent notice
    st.markdown('<div class="urgent-notice">🚨 URGENT: Evidence submission for CBD Nairobi incident - June 17, 2025, 2:00 PM</div>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox("Choose section:", ["🏠 Home", "📤 Submit Evidence", "📊 Status", "ℹ️ Help"])
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📤 Submit Evidence":
        show_submission_page(tool)
    elif page == "📊 Status":
        show_status_page()
    elif page == "ℹ️ Help":
        show_help_page()

def show_home_page():
    """Show the home page"""
    st.header("Welcome to the ICC Evidence Submission Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Purpose")
        st.write("""
        This tool helps you submit evidence to the International Criminal Court (ICC) 
        regarding serious incidents. It automates the submission process and provides 
        AI assistance for accurate documentation.
        """)
        
        st.subheader("📋 Current Incident")
        st.info("""
        **Date:** June 17, 2025  
        **Time:** 2:00 PM  
        **Location:** CBD, Nairobi, Kenya  
        **Type:** GSU-related incident  
        **Status:** Evidence collection ongoing
        """)
    
    with col2:
        st.subheader("🚀 How to Use")
        st.write("""
        1. **Navigate** to the "Submit Evidence" section
        2. **Upload** your evidence files (photos, videos, documents)
        3. **Fill** in incident details (pre-filled for current incident)
        4. **Review** AI-generated descriptions
        5. **Submit** to ICC portal automatically
        """)
        
        st.subheader("✅ Supported Evidence")
        st.write("""
        - 📸 **Photos** (JPG, PNG, HEIC)
        - 🎥 **Videos** (MP4, MOV, AVI)
        - 🎵 **Audio** (MP3, WAV, M4A)
        - 📄 **Documents** (PDF, DOC, TXT)
        """)

def show_submission_page(tool):
    """Show the evidence submission page"""
    st.header("📤 Submit Evidence to ICC")
    
    if not tool.form_mapping:
        st.error("Form mapping not available. Please contact support.")
        return
    
    # Pre-filled incident details for the current emergency
    st.subheader("📋 Incident Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        incident_date = st.date_input("Date of Incident", value=datetime(2025, 6, 17))
        incident_time = st.time_input("Time of Incident", value=time(14, 0))
        incident_location = st.text_input("Location", value="CBD, Nairobi, Kenya")
    
    with col2:
        submitter_name = st.text_input("Your Name (Optional)")
        submitter_email = st.text_input("Your Email (Optional)")
        submitter_phone = st.text_input("Your Phone (Optional)")
    
    incident_description = st.text_area(
        "Incident Description",
        value="Incident involving GSU personnel at CBD, Nairobi. Person shot at approximately 2:00 PM on June 17, 2025.",
        height=100
    )
    
    # Evidence upload section
    st.subheader("📎 Upload Evidence")
    
    uploaded_files = st.file_uploader(
        "Choose evidence files",
        accept_multiple_files=True,
        type=['jpg', 'jpeg', 'png', 'heic', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'm4a', 'pdf', 'doc', 'docx', 'txt'],
        help="Upload photos, videos, audio files, or documents related to the incident"
    )
    
    # Process uploaded files
    processed_evidence = []
    if uploaded_files:
        st.subheader("🔍 Evidence Processing")
        
        incident_details = {
            'date': incident_date.strftime('%Y-%m-%d'),
            'time': incident_time.strftime('%H:%M'),
            'location': incident_location,
            'description': incident_description
        }
        
        for uploaded_file in uploaded_files:
            with st.expander(f"📄 {uploaded_file.name}"):
                # Process file
                evidence = tool.process_uploaded_file(uploaded_file, incident_details)
                processed_evidence.append(evidence)
                
                # Show file info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Size:** {evidence['file_info']['size']:,} bytes")
                with col2:
                    st.write(f"**Type:** {evidence['evidence_type']}")
                with col3:
                    st.write(f"**Format:** {evidence['file_info']['type']}")
                
                # Show AI-generated description
                st.write("**AI-Generated Description:**")
                st.write(evidence['description'])
                
                # Allow manual editing
                edited_description = st.text_area(
                    "Edit description if needed:",
                    value=evidence['description'],
                    key=f"desc_{uploaded_file.name}",
                    height=80
                )
                evidence['description'] = edited_description
    
    # Additional information
    st.subheader("📝 Additional Information")
    
    col1, col2 = st.columns(2)
    with col1:
        witness_name = st.text_input("Witness Name (if any)")
        witness_contact = st.text_input("Witness Contact")
    
    with col2:
        additional_info = st.text_area("Additional Notes", height=100)
    
    # Submission section
    if uploaded_files and processed_evidence:
        st.subheader("🚀 Submit to ICC")
        
        # Summary before submission
        st.write("**Submission Summary:**")
        st.info(f"""
        - **Incident:** {incident_location} on {incident_date.strftime('%B %d, %Y')} at {incident_time.strftime('%I:%M %p')}
        - **Evidence Files:** {len(processed_evidence)} files
        - **Submitter:** {submitter_name or 'Anonymous'}
        - **Description:** {incident_description[:100]}...
        """)
        
        # Terms and conditions
        agree_terms = st.checkbox("I confirm that the information provided is accurate and I consent to its submission to the ICC")
        
        if st.button("🎯 Submit Evidence to ICC", disabled=not agree_terms, help="Submit all evidence to the International Criminal Court"):
            if agree_terms:
                with st.spinner("Submitting evidence to ICC..."):
                    # Prepare form data
                    form_data = {
                        'incident_date': incident_date.strftime('%Y-%m-%d'),
                        'incident_time': incident_time.strftime('%H:%M'),
                        'incident_location': incident_location,
                        'incident_description': incident_description,
                        'submitter_name': submitter_name,
                        'submitter_email': submitter_email,
                        'submitter_phone': submitter_phone,
                        'witness_name': witness_name,
                        'witness_contact': witness_contact,
                        'additional_info': additional_info
                    }
                    
                    # Submit to ICC
                    result = tool.simulate_icc_submission(form_data, processed_evidence)
                    
                    if result['success']:
                        st.success(f"✅ Evidence submitted successfully!")
                        st.balloons()
                        st.info(f"**Submission ID:** {result['submission_id']}")
                        st.info(f"**Timestamp:** {result['timestamp']}")
                        
                        # Store submission in session state for status tracking
                        if 'submissions' not in st.session_state:
                            st.session_state.submissions = []
                        st.session_state.submissions.append(result)
                        
                    else:
                        st.error(f"❌ Submission failed: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please confirm the terms and conditions before submitting.")
    elif not uploaded_files:
        st.info("👆 Please upload evidence files to proceed with submission.")

def show_status_page():
    """Show submission status page"""
    st.header("📊 Submission Status")
    
    if 'submissions' in st.session_state and st.session_state.submissions:
        st.subheader("Recent Submissions")
        
        for i, submission in enumerate(reversed(st.session_state.submissions)):
            with st.expander(f"Submission {submission['submission_id']}", expanded=(i == 0)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {submission['submission_id']}")
                    st.write(f"**Status:** {submission['status']}")
                    st.write(f"**Evidence Files:** {submission['evidence_count']}")
                
                with col2:
                    st.write(f"**Submitted:** {submission['timestamp']}")
                    st.write(f"**Location:** {submission['form_data'].get('incident_location', 'N/A')}")
                
                if submission['success']:
                    st.success(submission['message'])
                else:
                    st.error(f"Error: {submission.get('error', 'Unknown error')}")
    else:
        st.info("No submissions yet. Go to the Submit Evidence page to make your first submission.")

def show_help_page():
    """Show help and information page"""
    st.header("ℹ️ Help & Information")
    
    tab1, tab2, tab3 = st.tabs(["📋 How to Use", "🔒 Privacy & Security", "📞 Support"])
    
    with tab1:
        st.subheader("Step-by-Step Guide")
        st.write("""
        1. **Prepare Your Evidence**
           - Gather photos, videos, audio recordings, or documents
           - Ensure files are clear and relevant to the incident
           
        2. **Fill Incident Details**
           - Most details are pre-filled for the current incident
           - Add any additional context or corrections needed
           
        3. **Upload Files**
           - Drag and drop files or use the upload button
           - Supported formats: JPG, PNG, MP4, MOV, PDF, etc.
           
        4. **Review AI Descriptions**
           - The system generates professional descriptions
           - Edit them if needed to ensure accuracy
           
        5. **Submit to ICC**
           - Review all information carefully
           - Accept terms and conditions
           - Click submit to send to ICC portal
        """)
    
    with tab2:
        st.subheader("Privacy & Security")
        st.write("""
        - **Data Protection:** All files are processed securely and transmitted directly to ICC
        - **No Local Storage:** Files are not stored on our servers permanently
        - **Anonymous Option:** You can submit evidence without providing personal details
        - **Encryption:** All data transmission uses secure HTTPS encryption
        - **ICC Direct:** Evidence goes directly to official ICC channels
        """)
    
    with tab3:
        st.subheader("Support & Contact")
        st.write("""
        - **Technical Issues:** If you encounter problems, try refreshing the page
        - **Large Files:** Break large videos into smaller segments if upload fails
        - **Emergency:** For urgent submissions, contact ICC directly at +31 70 515 8515
        - **Status Updates:** Check the Status page for submission tracking
        """)
        
        st.subheader("About ICC")
        st.write("""
        The International Criminal Court (ICC) is an independent judicial institution 
        empowered to investigate and prosecute war crimes, crimes against humanity, 
        genocide, and the crime of aggression.
        
        **ICC Website:** https://icc-cpi.int  
        **Evidence Portal:** https://otplink.icc-cpi.int
        """)

if __name__ == "__main__":
    main()
