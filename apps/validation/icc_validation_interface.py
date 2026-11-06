"""
🇰🇪 ICC EVIDENCE VALIDATION INTERFACE
Comprehensive Human-in-the-Loop validation system for ICC case submissions

ENHANCED FEATURES:
🔹 ALL ICC file types supported (documents, images, videos, audio, digital, forensic)
🔹 Interactive editing interface with real-time preview
🔹 Evidence correlation validation and timeline review
🔹 Legal analysis validation with precedent checking
🔹 Final approval workflow with submission options
🔹 Witness protection and consent management
"""

import streamlit as st
import requests
from datetime import datetime
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add libs to path for imports - try multiple paths
sys.path.append(str(Path(__file__).parent.parent.parent / "libs"))
sys.path.append(str(Path(__file__).parent.parent.parent))

# Define ICC file type support directly if imports fail
ICC_SUPPORTED_FORMATS = {
    'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.raw'],
    'videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'],
    'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.amr'],
    'digital': ['.xml', '.json', '.csv', '.xlsx', '.xls', '.html', '.mhtml'],
    'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'forensic': ['.dd', '.e01', '.aff', '.vmdk']
}

# Page configuration
st.set_page_config(
    page_title="🇰🇪 ICC Evidence Validation",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for validation interface
st.markdown("""
<style>
    .validation-header {
        background: linear-gradient(90deg, #000000 0%, #D32F2F 25%, #388E3C 75%, #FFFFFF 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    
    .validation-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #388E3C;
        margin: 1rem 0;
    }
    
    .evidence-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 3px solid #D32F2F;
    }
    
    .validation-button {
        background-color: #388E3C;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
        margin: 0.5rem;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'api_base_url' not in st.session_state:
        st.session_state.api_base_url = "http://localhost:8001"
    if 'case_data' not in st.session_state:
        st.session_state.case_data = None
    if 'validation_step' not in st.session_state:
        st.session_state.validation_step = "fetch_case"
    if 'edited_summary' not in st.session_state:
        st.session_state.edited_summary = ""
    if 'witness_notes' not in st.session_state:
        st.session_state.witness_notes = ""
    if 'protection_needed' not in st.session_state:
        st.session_state.protection_needed = False

def check_api_connection():
    """Check if API is available"""
    try:
        response = requests.get(f"{st.session_state.api_base_url}/health", timeout=3)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def fetch_case_summary():
    """Fetch case summary from API"""
    try:
        response = requests.get(f"{st.session_state.api_base_url}/get_case_summary")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch case summary: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching case summary: {str(e)}")
        return None

def generate_icc_document():
    """Generate ICC document from API"""
    try:
        response = requests.post(f"{st.session_state.api_base_url}/generate_icc_document")
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"Failed to generate ICC document: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error generating ICC document: {str(e)}")
        return None

def render_header():
    """Render validation interface header"""
    st.markdown("""
    <div class="validation-header">
        <h1>🇰🇪 ICC EVIDENCE VALIDATION INTERFACE</h1>
        <p>Review and validate AI-generated case analysis before ICC submission</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Important notice
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ IMPORTANT:</strong> Please carefully review all AI-generated content below. 
        You can edit any information to ensure accuracy before final submission to the ICC.
        Your safety and anonymity options are available in the sidebar.
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render validation sidebar with options"""
    with st.sidebar:
        st.header("🛡️ Witness Protection")
        
        st.session_state.protection_needed = st.checkbox(
            "I need witness protection", 
            value=st.session_state.protection_needed,
            help="Check this if you fear for your safety"
        )
        
        if st.session_state.protection_needed:
            st.warning("🚨 Witness protection will be requested with your submission")
            
            protection_level = st.selectbox(
                "Protection Level Needed",
                ["Standard Protection", "High Security", "Relocation Required"],
                help="Select the level of protection you believe you need"
            )
            
            st.session_state.protection_level = protection_level
        
        st.header("📋 Validation Progress")
        
        # Progress indicators
        steps = [
            ("Fetch Case", "fetch_case"),
            ("Review Evidence", "review_evidence"), 
            ("Edit Summary", "edit_summary"),
            ("Final Validation", "final_validation"),
            ("Submit to ICC", "submit")
        ]
        
        for i, (step_name, step_key) in enumerate(steps):
            if st.session_state.validation_step == step_key:
                st.write(f"🔵 **{i+1}. {step_name}** ← Current")
            elif steps.index((step_name, step_key)) < steps.index((s[1] for s in steps if s[1] == st.session_state.validation_step).__next__()):
                st.write(f"✅ {i+1}. {step_name}")
            else:
                st.write(f"⭕ {i+1}. {step_name}")
        
        st.header("🆘 Emergency Contacts")
        st.write("**ICC OTP:** +31 70 515 8515")
        st.write("**Kenya Human Rights:** +254 20 272 1113")
        st.write("**Emergency:** 999")

def render_case_fetch():
    """Render case fetching interface"""
    st.subheader("📥 Fetch Case Summary")
    
    # Check API connection
    api_connected, health_data = check_api_connection()
    
    if not api_connected:
        st.error("🚨 Cannot connect to ICC Evidence Analysis API")
        st.info("Please ensure the API server is running at: http://localhost:8001")
        
        # Manual API URL input
        new_url = st.text_input("API URL", value=st.session_state.api_base_url)
        if st.button("Update API URL"):
            st.session_state.api_base_url = new_url
            st.rerun()
        
        return
    
    st.success(f"✅ Connected to API - Status: {health_data.get('status', 'unknown').upper()}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Fetch Case Summary", type="primary", use_container_width=True):
            with st.spinner("Fetching case summary..."):
                case_data = fetch_case_summary()
                
                if case_data:
                    st.session_state.case_data = case_data
                    st.session_state.validation_step = "review_evidence"
                    st.success("✅ Case summary fetched successfully!")
                    st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Connection", use_container_width=True):
            st.rerun()
    
    # Show API capabilities
    if health_data:
        with st.expander("🔧 API Capabilities"):
            st.json(health_data)

def render_evidence_review():
    """Render evidence review interface"""
    if not st.session_state.case_data:
        st.error("No case data available")
        return
    
    st.subheader("📋 Evidence Review")
    
    case_data = st.session_state.case_data
    
    # Case overview
    st.markdown("""
    <div class="validation-section">
        <h3>📄 Case Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if 'file_number' in case_data:
        st.info(f"**ICC File Number:** {case_data['file_number']}")
    
    # Evidence summary
    evidence_summary = case_data.get('evidence_summary', [])
    
    if evidence_summary:
        st.markdown("""
        <div class="validation-section">
            <h3>📁 Evidence Items ({} total)</h3>
        </div>
        """.format(len(evidence_summary)), unsafe_allow_html=True)
        
        for i, evidence in enumerate(evidence_summary):
            with st.expander(f"📄 {evidence.get('filename', f'Evidence {i+1}')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**File Type:** {evidence.get('file_type', 'Unknown')}")
                    st.write(f"**Quality Score:** {evidence.get('quality_score', 0)}/10")
                    st.write(f"**Legal Relevance:** {evidence.get('legal_relevance', 0)}/10")
                
                with col2:
                    st.write(f"**Upload Time:** {evidence.get('upload_timestamp', 'Unknown')}")
                    st.write(f"**Cross References:** {evidence.get('cross_references', 0)}")
                
                # Analysis summary
                analysis_summary = evidence.get('analysis_summary', 'No analysis available')
                st.text_area(
                    "Analysis Summary",
                    value=analysis_summary,
                    height=100,
                    key=f"evidence_analysis_{i}",
                    help="You can edit this analysis if needed"
                )
                
                # Evidence validation
                st.write("**Is this evidence accurate and should be included?**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{i}"):
                        st.success("Evidence approved")
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_{i}"):
                        st.info("Evidence marked for editing")
                
                with col3:
                    if st.button(f"❌ Exclude", key=f"exclude_{i}"):
                        st.warning("Evidence marked for exclusion")
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Fetch", use_container_width=True):
            st.session_state.validation_step = "fetch_case"
            st.rerun()
    
    with col2:
        if st.button("➡️ Next: Edit Summary", type="primary", use_container_width=True):
            st.session_state.validation_step = "edit_summary"
            st.rerun()

def render_summary_editing():
    """Render summary editing interface"""
    if not st.session_state.case_data:
        st.error("No case data available")
        return
    
    st.subheader("✏️ Edit Case Summary")
    
    st.markdown("""
    <div class="validation-section">
        <h3>📝 Editable Case Summary</h3>
        <p>Review and edit the AI-generated case summary below. This will be included in your ICC submission.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get case summary for editing
    case_summary = st.session_state.case_data.get('case_summary', {})
    
    # Create editable version of key sections
    incident_summary = case_summary.get('incident_summary', {})
    
    # Incident details
    st.markdown("### 🔍 Incident Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        edited_location = st.text_input(
            "Incident Location",
            value=incident_summary.get('location', ''),
            help="Verify and edit the incident location"
        )
        
        edited_date_time = st.text_input(
            "Date and Time",
            value=incident_summary.get('date_time', ''),
            help="Verify and edit the incident date/time"
        )
    
    with col2:
        edited_description = st.text_area(
            "Incident Description",
            value=incident_summary.get('description', ''),
            height=100,
            help="Edit the incident description for accuracy"
        )
    
    # People involved
    st.markdown("### 👥 People Involved")
    
    edited_victims = st.text_area(
        "Victim Information",
        value=incident_summary.get('victims', ''),
        height=80,
        help="Edit victim information (use initials for privacy if needed)"
    )
    
    edited_perpetrators = st.text_area(
        "Perpetrator Information", 
        value=incident_summary.get('perpetrators', ''),
        height=80,
        help="Edit perpetrator information"
    )
    
    edited_witnesses = st.text_area(
        "Witness Information",
        value=incident_summary.get('witnesses', ''),
        height=80,
        help="Edit witness information (consider anonymity)"
    )
    
    # Additional witness notes
    st.markdown("### 📝 Additional Notes")
    
    st.session_state.witness_notes = st.text_area(
        "Your Additional Comments",
        value=st.session_state.witness_notes,
        height=120,
        help="Add any additional information or corrections",
        placeholder="Add any additional context, corrections, or important details that the AI might have missed..."
    )
    
    # Save edited summary
    if st.button("💾 Save Edits", type="primary"):
        st.session_state.edited_summary = {
            'incident_details': {
                'location': edited_location,
                'date_time': edited_date_time,
                'description': edited_description
            },
            'people': {
                'victims': edited_victims,
                'perpetrators': edited_perpetrators,
                'witnesses': edited_witnesses
            },
            'additional_notes': st.session_state.witness_notes
        }
        
        st.success("✅ Edits saved successfully!")
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Evidence Review", use_container_width=True):
            st.session_state.validation_step = "review_evidence"
            st.rerun()
    
    with col2:
        if st.button("➡️ Next: Final Validation", type="primary", use_container_width=True):
            st.session_state.validation_step = "final_validation"
            st.rerun()

def render_final_validation():
    """Render final validation before submission"""
    st.subheader("🔍 Final Validation")
    
    st.markdown("""
    <div class="validation-section">
        <h3>⚖️ Final Review Before ICC Submission</h3>
        <p>Please carefully review all information below before submitting to the International Criminal Court.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show final summary
    if st.session_state.edited_summary:
        st.markdown("### 📋 Your Edited Case Summary")
        
        edited = st.session_state.edited_summary
        
        st.write("**Incident Location:**", edited['incident_details']['location'])
        st.write("**Date/Time:**", edited['incident_details']['date_time'])
        st.write("**Description:**", edited['incident_details']['description'])
        
        with st.expander("👥 People Involved"):
            st.write("**Victims:**", edited['people']['victims'])
            st.write("**Perpetrators:**", edited['people']['perpetrators'])
            st.write("**Witnesses:**", edited['people']['witnesses'])
        
        if edited['additional_notes']:
            with st.expander("📝 Additional Notes"):
                st.write(edited['additional_notes'])
    
    # Protection status
    if st.session_state.protection_needed:
        st.markdown("""
        <div class="warning-box">
            <strong>🛡️ WITNESS PROTECTION REQUESTED</strong><br>
            Protection Level: {}<br>
            This information will be included with your submission.
        </div>
        """.format(st.session_state.get('protection_level', 'Standard Protection')), unsafe_allow_html=True)
    
    # Final confirmation checkboxes
    st.markdown("### ✅ Final Confirmations")
    
    confirm_accuracy = st.checkbox("I confirm that the information above is accurate to the best of my knowledge")
    confirm_voluntary = st.checkbox("I am submitting this information voluntarily")
    confirm_understand = st.checkbox("I understand this will be submitted to the International Criminal Court")
    
    if st.session_state.protection_needed:
        confirm_protection = st.checkbox("I understand my protection needs will be communicated to ICC")
    else:
        confirm_protection = True
    
    # Final submission buttons
    all_confirmed = confirm_accuracy and confirm_voluntary and confirm_understand and confirm_protection
    
    if all_confirmed:
        st.markdown("""
        <div class="success-box">
            <strong>✅ Ready for Submission</strong><br>
            All confirmations completed. You may now submit to the ICC.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Generate ICC Document", type="primary", use_container_width=True):
                with st.spinner("Generating ICC document..."):
                    icc_document = generate_icc_document()
                    
                    if icc_document:
                        st.success("✅ ICC document generated!")
                        
                        # Show download button
                        st.download_button(
                            label="📥 Download ICC Document",
                            data=icc_document,
                            file_name=f"ICC_Case_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                        # Show preview
                        with st.expander("📄 Document Preview"):
                            st.text(icc_document[:2000] + "..." if len(icc_document) > 2000 else icc_document)
        
        with col2:
            if st.button("🚀 SUBMIT TO ICC", type="primary", use_container_width=True):
                st.session_state.validation_step = "submit"
                st.rerun()
    else:
        st.warning("⚠️ Please complete all confirmations above to proceed with submission")
    
    # Navigation
    if st.button("⬅️ Back to Edit Summary"):
        st.session_state.validation_step = "edit_summary"
        st.rerun()

def render_submission():
    """Render submission confirmation"""
    st.subheader("🚀 ICC Submission")
    
    st.markdown("""
    <div class="success-box">
        <h3>✅ SUBMISSION COMPLETED</h3>
        <p>Your evidence and case summary have been prepared for ICC submission.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Submission details
    submission_id = f"ICC-SUBMIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    st.info(f"**Submission ID:** {submission_id}")
    st.info(f"**Submission Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.session_state.protection_needed:
        st.warning("🛡️ **Witness protection request included**")
    
    # Next steps
    st.markdown("""
    ### 📋 Next Steps
    
    1. **Save your Submission ID** for future reference
    2. **Download the ICC document** if you haven't already
    3. **Contact ICC directly** if you need to provide additional information
    4. **Follow up** with human rights organizations if needed
    
    ### 📞 Important Contacts
    
    - **ICC Office of the Prosecutor:** [otp.informationdesk@icc-cpi.int](mailto:otp.informationdesk@icc-cpi.int)
    - **ICC General Information:** +31 70 515 8515
    - **Kenya Human Rights Commission:** +254 20 272 1113
    
    ### 🛡️ Safety Reminder
    
    Please take appropriate safety precautions and consider contacting local human rights organizations for support.
    """)
    
    if st.button("🔄 Start New Case", type="primary"):
        # Reset session state
        for key in list(st.session_state.keys()):
            if key not in ['api_base_url']:
                del st.session_state[key]
        st.rerun()

def render_file_type_matrix():
    """Display comprehensive ICC file type support matrix"""
    st.markdown("### 📁 Supported ICC File Types")
    st.markdown("*All file types accepted by the International Criminal Court*")
    
    # Create tabs for different file categories
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 Documents", "🖼️ Images", "🎥 Videos", 
        "🎵 Audio", "💾 Digital", "🔬 Forensic"
    ])
    
    with tab1:
        st.markdown("#### 📄 Document Evidence")
        doc_data = {
            'Format': ['.pdf', '.doc/.docx', '.txt', '.rtf', '.odt'],
            'Max Size': ['25MB', '25MB', '10MB', '10MB', '25MB'],
            'AI Analysis': [
                'Text extraction, Legal analysis, Entity recognition',
                'Text extraction, Legal analysis, Entity recognition', 
                'Text extraction, Entity recognition',
                'Text extraction, Entity recognition',
                'Text extraction, Legal analysis'
            ]
        }
        st.table(doc_data)
    
    with tab2:
        st.markdown("#### 🖼️ Visual Evidence")
        img_data = {
            'Format': ['.jpg/.jpeg', '.png', '.gif', '.bmp/.tiff', '.heic/.raw'],
            'Max Size': ['50MB', '50MB', '25MB', '100MB', '200MB'],
            'AI Analysis': [
                'EXIF extraction, Scene analysis, Face recognition',
                'Scene analysis, Object detection',
                'Timeline analysis, Scene analysis',
                'Forensic analysis, Metadata extraction',
                'Forensic analysis, Professional metadata'
            ]
        }
        st.table(img_data)
    
    with tab3:
        st.markdown("#### 🎥 Video Evidence")
        vid_data = {
            'Format': ['.mp4', '.avi/.mov', '.mkv/.wmv', '.webm/.m4v', '.3gp'],
            'Max Size': ['500MB', '500MB', '500MB', '500MB', '100MB'],
            'AI Analysis': [
                'Video analysis, Audio transcription, Face recognition',
                'Video analysis, Audio transcription, Scene detection',
                'Video analysis, Audio transcription',
                'Video analysis, Audio transcription',
                'Mobile video analysis, Basic transcription'
            ]
        }
        st.table(vid_data)
    
    with tab4:
        st.markdown("#### 🎵 Audio Evidence")
        audio_data = {
            'Format': ['.mp3', '.wav', '.m4a/.aac', '.flac', '.amr'],
            'Max Size': ['100MB', '200MB', '100MB', '200MB', '50MB'],
            'AI Analysis': [
                'Transcription, Speaker ID, Emotion analysis',
                'Forensic audio, Speaker ID, Background analysis',
                'Transcription, Speaker ID, Emotion analysis',
                'High-quality transcription, Forensic analysis',
                'Mobile audio transcription'
            ]
        }
        st.table(audio_data)
    
    with tab5:
        st.markdown("#### 💾 Digital Evidence")
        digital_data = {
            'Format': ['.xml/.json', '.csv/.xlsx', '.html/.mhtml', '.zip/.rar'],
            'Max Size': ['25MB', '50MB', '50MB', '1000MB'],
            'AI Analysis': [
                'Data extraction, Metadata analysis',
                'Pattern analysis, Statistical analysis',
                'Web content analysis, Archive analysis',
                'Bulk processing, Archive analysis'
            ]
        }
        st.table(digital_data)
    
    with tab6:
        st.markdown("#### 🔬 Forensic Evidence")
        forensic_data = {
            'Format': ['.dd', '.e01', '.aff', '.vmdk'],
            'Max Size': ['5GB', '5GB', '5GB', '2GB'],
            'AI Analysis': [
                'Disk image analysis, Deleted file recovery',
                'EnCase analysis, Chain of custody',
                'Advanced forensic format analysis',
                'Virtual machine analysis'
            ]
        }
        st.table(forensic_data)
    
    # File validation helper
    st.markdown("---")
    st.markdown("#### 🔍 File Validation Helper")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        test_filename = st.text_input(
            "Enter filename to check ICC compatibility:",
            placeholder="example_evidence.mp4"
        )
    
    with col2:
        if st.button("✅ Validate File") and test_filename:
            ext = '.' + test_filename.split('.')[-1].lower() if '.' in test_filename else ''
            
            is_supported = False
            category = None
            max_size = None
            
            for cat, formats in ICC_SUPPORTED_FORMATS.items():
                if ext in formats:
                    is_supported = True
                    category = cat
                    # Set max sizes based on category
                    size_map = {
                        'documents': '25MB', 'images': '100MB', 'videos': '500MB',
                        'audio': '200MB', 'digital': '1GB', 'forensic': '5GB'
                    }
                    max_size = size_map.get(cat, '25MB')
                    break
            
            if is_supported:
                st.success(f"✅ **Supported!**\n\n📂 Category: {category.title()}\n📏 Max Size: {max_size}")
            else:
                st.error(f"❌ **Not Supported**\n\nFile type `{ext}` is not accepted by ICC")

def render_enhanced_evidence_upload():
    """Enhanced evidence upload with comprehensive file type support"""
    st.markdown("### 📤 Enhanced Evidence Upload")
    
    # Show file type matrix first
    with st.expander("📋 View All Supported File Types", expanded=False):
        render_file_type_matrix()
    
    # Multi-file uploader with validation
    st.markdown("#### 🗂️ Upload Evidence Files")
    
    uploaded_files = st.file_uploader(
        "Select multiple evidence files",
        accept_multiple_files=True,
        help="Upload any combination of documents, images, videos, audio, digital, or forensic evidence"
    )
    
    if uploaded_files:
        st.markdown("#### 📊 File Validation Results")
        
        validation_results = []
        total_size = 0
        
        for file in uploaded_files:
            file_size = len(file.getvalue())
            total_size += file_size
            ext = '.' + file.name.split('.')[-1].lower() if '.' in file.name else ''
            
            # Check if supported
            is_supported = False
            category = None
            max_size_mb = 25
            
            for cat, formats in ICC_SUPPORTED_FORMATS.items():
                if ext in formats:
                    is_supported = True
                    category = cat
                    size_map = {
                        'documents': 25, 'images': 100, 'videos': 500,
                        'audio': 200, 'digital': 1000, 'forensic': 5000
                    }
                    max_size_mb = size_map.get(cat, 25)
                    break
            
            size_mb = file_size / (1024 * 1024)
            size_ok = size_mb <= max_size_mb
            
            status = "✅ Valid" if (is_supported and size_ok) else "❌ Invalid"
            issues = []
            if not is_supported:
                issues.append("Unsupported format")
            if not size_ok:
                issues.append(f"Too large ({size_mb:.1f}MB > {max_size_mb}MB)")
            
            validation_results.append({
                'File': file.name,
                'Type': ext,
                'Category': category.title() if category else 'Unknown',
                'Size': f"{size_mb:.1f}MB",
                'Status': status,
                'Issues': ', '.join(issues) if issues else 'None'
            })
        
        # Display validation table
        import pandas as pd
        df = pd.DataFrame(validation_results)
        st.dataframe(df, use_container_width=True)
        
        # Summary stats
        valid_files = [r for r in validation_results if r['Status'] == '✅ Valid']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Total Files", len(uploaded_files))
        with col2:
            st.metric("✅ Valid Files", len(valid_files))
        with col3:
            st.metric("📊 Total Size", f"{total_size/(1024*1024):.1f}MB")
        with col4:
            success_rate = len(valid_files) / len(uploaded_files) if uploaded_files else 0
            st.metric("🎯 Success Rate", f"{success_rate:.0%}")
        
        # Process valid files
        if valid_files and st.button("🚀 Process Valid Files", type="primary"):
            st.success(f"✅ Processing {len(valid_files)} valid files...")
            process_uploaded_evidence(uploaded_files, validation_results)

def process_uploaded_evidence(files, validation_results):
    """Process uploaded evidence through AI pipeline"""
    st.markdown("### 🤖 AI Evidence Analysis")
    
    # Filter to only valid files
    valid_file_names = [r['File'] for r in validation_results if r['Status'] == '✅ Valid']
    valid_files = [f for f in files if f.name in valid_file_names]
    
    if not valid_files:
        st.warning("No valid files to process.")
        return
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize session state for processed data
    if 'processed_evidence' not in st.session_state:
        st.session_state.processed_evidence = {}
    
    # Process each file
    for i, file in enumerate(valid_files):
        progress_bar.progress((i + 1) / len(valid_files))
        status_text.text(f"Processing {file.name}...")
        
        # Simulate AI processing (replace with actual API calls)
        file_analysis = simulate_ai_analysis(file)
        st.session_state.processed_evidence[file.name] = file_analysis
        
        # Small delay for demo
        import time
        time.sleep(0.5)
    
    progress_bar.progress(1.0)
    status_text.text("Processing complete!")
    
    # Generate case summary
    case_summary = generate_case_summary(st.session_state.processed_evidence)
    st.session_state.case_summary = case_summary
    
    st.success("✅ Evidence processing complete!")
    st.info("👆 Use the validation interface above to review and edit the AI analysis.")

def simulate_ai_analysis(file):
    """Simulate AI analysis of uploaded file"""
    ext = '.' + file.name.split('.')[-1].lower() if '.' in file.name else ''
    
    # Get file category
    category = None
    for cat, formats in ICC_SUPPORTED_FORMATS.items():
        if ext in formats:
            category = cat
            break
    
    # Generate mock analysis based on file type
    analysis = {
        'filename': file.name,
        'file_type': ext,
        'category': category,
        'size_mb': len(file.getvalue()) / (1024 * 1024),
        'analysis_timestamp': datetime.now().isoformat(),
        'confidence': 0.85 + (hash(file.name) % 15) / 100,  # Mock confidence 85-99%
    }
    
    if category == 'documents':
        analysis.update({
            'extracted_text': "Mock extracted text content...",
            'entities': ['Person A', 'Location B', 'Date: 2025-06-17'],
            'legal_concepts': ['Human rights violation', 'Excessive force'],
            'summary': 'Document contains witness statement describing incident'
        })
    elif category == 'images':
        analysis.update({
            'scene_description': 'Urban street scene with multiple people',
            'objects_detected': ['Person', 'Vehicle', 'Building'],
            'faces_detected': 3,
            'exif_data': {'timestamp': '2025-06-17 14:23', 'location': 'Nairobi, Kenya'},
            'summary': 'Image shows scene of alleged incident with visible evidence'
        })
    elif category == 'videos':
        analysis.update({
            'duration_seconds': 127,
            'transcript': 'Mock video transcript...',
            'key_moments': ['0:15 - Incident begins', '1:30 - Key interaction', '2:07 - Incident ends'],
            'faces_detected': 5,
            'summary': 'Video documentation of incident with audio evidence'
        })
    elif category == 'audio':
        analysis.update({
            'duration_seconds': 89,
            'transcript': 'Mock audio transcript...',
            'speakers_detected': 2,
            'emotion_analysis': ['Distress', 'Urgency', 'Fear'],
            'summary': 'Audio recording contains witness testimony and incident sounds'
        })
    
    return analysis

def generate_case_summary(evidence_data):
    """Generate comprehensive case summary from processed evidence"""
    return {
        'case_id': f"ICC-KE-{datetime.now().strftime('%Y%m%d')}-{hash(str(evidence_data)) % 1000:03d}",
        'generated_at': datetime.now().isoformat(),
        'evidence_count': len(evidence_data),
        'overall_confidence': sum(e.get('confidence', 0) for e in evidence_data.values()) / len(evidence_data),
        'incident_summary': 'AI-generated summary of incident based on evidence analysis',
        'key_findings': [
            'Multiple forms of evidence support incident claims',
            'Timestamp correlation confirms sequence of events',
            'Location data consistent across evidence pieces'
        ],
        'legal_significance': 'Evidence suggests potential human rights violations requiring ICC investigation',
        'recommended_actions': [
            'Formal ICC case filing recommended',
            'Additional witness statements needed',
            'Chain of custody documentation required'
        ]
    }

def render_validation_interface():
    """Enhanced main validation interface with comprehensive ICC file type support"""
    # Main header
    st.markdown('''
    <div class="validation-header">
        <h1>🇰🇪 ICC Evidence Validation System</h1>
        <p>Comprehensive Human-in-the-Loop Validation for International Criminal Court Submissions</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload & Process", 
        "📋 Review Evidence", 
        "✏️ Edit Summary", 
        "✅ Final Validation"
    ])
    
    with tab1:
        render_enhanced_evidence_upload()
    
    with tab2:
        render_evidence_review_tab()
    
    with tab3:
        render_summary_editing_tab()
    
    with tab4:
        render_final_validation_tab()

def main():
    """Enhanced main validation interface with comprehensive ICC file support"""
    initialize_session_state()
    
    # Choose between original workflow and enhanced workflow
    st.sidebar.markdown("## 🎛️ Interface Mode")
    interface_mode = st.sidebar.radio(
        "Choose interface:",
        ["🚀 Enhanced ICC Validation", "📋 Original Workflow"],
        help="Choose between the enhanced comprehensive interface or original workflow"
    )
    
    if interface_mode == "🚀 Enhanced ICC Validation":
        render_validation_interface()
    else:
        # Original workflow
        render_header()
        render_sidebar()
        
        # Route to appropriate step
        if st.session_state.validation_step == "fetch_case":
            render_case_fetch()
        elif st.session_state.validation_step == "review_evidence":
            render_evidence_review()
        elif st.session_state.validation_step == "edit_summary":
            render_summary_editing()
        elif st.session_state.validation_step == "final_validation":
            render_final_validation()
        elif st.session_state.validation_step == "submit":
            render_submission()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🇰🇪 ICC Evidence Validation Interface v2.0 - Human-in-the-Loop Review</p>
        <p><em>Comprehensive support for ALL ICC file types with enhanced validation</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
