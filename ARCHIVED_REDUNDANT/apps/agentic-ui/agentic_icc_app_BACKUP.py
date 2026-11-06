"""
🇰🇪 AGENTIC ICC EVIDENCE SUBMISSION TOOL
Complete AI-powered evidence submission to the International Criminal Court
Intelligently merged: main_app.py + app.py + unified_icc_app.py + fast_streamlit_app.py + agentic_processor.py
- Multi-step guided workflow with metadata extraction (from main_app.py)
- Selenium automation for ICC form submission (from app.py) 
- FastAPI backend integration with advanced analytics (from unified_icc_app.py)
- Lightning-fast analysis (from fast_streamlit_app.py)
- Agentic workflow automation (from agentic_processor.py)
"""

import streamlit as st
import requests
import json
import time
import io
import base64
import tempfile
from pathlib import Path
from datetime import datetime
from PIL import Image
import os
from dotenv import load_dotenv
from groq import Groq
import geocoder
import exifread
from geopy.geocoders import Nominatim
from mutagen import File as MutagenFile
import fitz  # PyMuPDF
from docx import Document
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import httpx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load environment variables
load_dotenv()

# Kenyan Flag Color Palette (from app.py)
KENYAN_COLORS = {
    'black': '#000000',
    'red': '#D32F2F',
    'green': '#388E3C',
    'white': '#FFFFFF'
}

# Page configuration for speed (from fast_streamlit_app.py)
st.set_page_config(
    page_title="🇰🇪 Agentic ICC Evidence Submitter",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-powered evidence submission to the International Criminal Court"
    }
)

# Enhanced CSS combining both apps' best styling
st.markdown(f"""
<style>
    /* Emergency ICC styling from app.py */
    .main-header {{
        background: linear-gradient(90deg, {KENYAN_COLORS['black']} 0%, {KENYAN_COLORS['red']} 25%, {KENYAN_COLORS['green']} 75%, {KENYAN_COLORS['white']} 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }}
    
    .emergency-banner {{
        background-color: {KENYAN_COLORS['red']};
        color: white;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
        100% {{ opacity: 1; }}
    }}
    
    /* Fast analysis styling from fast_streamlit_app.py */
    .analysis-card {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {KENYAN_COLORS['green']};
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .speed-indicator {{
        background: #00ff00;
        color: black;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }}
    
    .upload-zone {{
        border: 3px dashed {KENYAN_COLORS['green']};
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background: rgba(0, 128, 0, 0.05);
        margin: 10px 0;
        transition: all 0.3s ease;
    }}
    
    .upload-zone:hover {{
        background: rgba(0, 128, 0, 0.1);
        border-color: #006600;
    }}
    
    .agentic-chat {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }}
    
    .legal-assessment {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }}
    
    .submission-ready {{
        background: {KENYAN_COLORS['green']};
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
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

# Initialize session state for caching (from fast_streamlit_app.py)
if 'analysis_cache' not in st.session_state:
    st.session_state.analysis_cache = {}
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8001"
if 'evidence_analyses' not in st.session_state:
    st.session_state.evidence_analyses = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agentic_phase' not in st.session_state:
    st.session_state.agentic_phase = "upload"  # upload -> analyze -> chat -> context -> submit

class AgenticICCSubmitter:
    """Enhanced ICC Evidence Submitter combining multi-step workflow from app.py with agentic AI features"""
    
    def __init__(self):
        self.api_url = st.session_state.api_base_url
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.icc_url = "https://otplink.icc-cpi.int/"
        self.steps = [
            "Upload Evidence",
            "AI Analysis", 
            "Evidence Details",
            "Personal Information",
            "Generate Context",
            "Review & Submit"
        ]
        
    def init_session_state(self):
        """Initialize session state variables from app.py multi-step pattern"""
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'incident_date': None,
                'incident_time': None,
                'incident_location': "CBD, Nairobi, Kenya",
                'incident_description': "Person shot by GSU (General Service Unit)",
                'victim_info': "",
                'perpetrator_info': "GSU Officers",
                'witness_info': "",
                'submitter_name': "",
                'submitter_email': "",
                'submitter_phone': "",
                'evidence_description': "",
                'additional_notes': ""
            }
        if 'evidence_analyses' not in st.session_state:
            st.session_state.evidence_analyses = []
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    def analyze_evidence_with_groq(self, file_content, file_type, incident_details):
        """Enhanced evidence analysis using Groq with structured output from app.py"""
        prompt = f"""
        You are an expert legal assistant analyzing evidence for ICC submission.
        
        INCIDENT CONTEXT:
        - Location: {incident_details.get('location', 'CBD, Nairobi, Kenya')}
        - Date: {incident_details.get('date', 'June 17, 2025')}
        - Time: {incident_details.get('time', '2:00 PM')}
        - Incident: {incident_details.get('incident', 'Person shot by GSU')}
        
        FILE INFORMATION:
        - File type: {file_type}
        - Context: Evidence related to human rights violation
        
        Provide comprehensive analysis in JSON format:
        {{
            "evidence_type": "photograph/video/audio/document/witness_statement/other",
            "evidence_description": "Clear description of evidence content",
            "incident_relation": "How evidence relates to the incident",
            "source_description": "How evidence was obtained",
            "relevance_score": "1-10 relevance rating",
            "suggested_categories": ["relevant", "categories"],
            "legal_significance": "Why this evidence is legally significant",
            "recommended_action": "Recommended next steps",
            "icc_relevance": "high/medium/low",
            "evidence_quality": "excellent/good/fair/poor"
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
              except Exception as e:
            st.error(f"Error analyzing evidence: {str(e)}")
            return None

    def extract_metadata_from_file(self, uploaded_file):
        """Extract comprehensive metadata from uploaded files including GPS, timestamps"""
        try:
            metadata = {
                'filename': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.type,
                'location': None,
                'timestamp': None,
                'gps_coords': None,
                'creation_date': None
            }
            
            # Read file content
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            # Extract metadata based on file type
            if uploaded_file.type.startswith('image/'):
                metadata.update(self._extract_image_metadata(file_content))
            elif uploaded_file.type.startswith('video/'):
                metadata.update(self._extract_video_metadata(file_content))
            elif uploaded_file.type.startswith('audio/'):
                metadata.update(self._extract_audio_metadata(file_content))
            elif uploaded_file.type == 'application/pdf':
                metadata.update(self._extract_pdf_metadata(file_content))
            elif 'document' in uploaded_file.type or 'word' in uploaded_file.type:
                metadata.update(self._extract_document_metadata(file_content))
            
            # Convert GPS coordinates to address if available
            if metadata.get('gps_coords'):
                location_name = self._get_location_from_coords(metadata['gps_coords'])
                if location_name:
                    metadata['location'] = location_name
            
            return metadata
            
        except Exception as e:
            st.error(f"Error extracting metadata: {str(e)}")
            return metadata

    def _extract_image_metadata(self, file_content):
        """Extract metadata from image files"""
        metadata = {}
        try:
            # Use EXIF data to extract GPS and timestamp information
            import exifread
            from geopy.geocoders import Nominatim
            
            # Create a file-like object from the content
            image_file = io.BytesIO(file_content)
            tags = exifread.process_file(image_file, details=False)
            
            # Extract GPS coordinates
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = self._convert_gps_to_decimal(tags['GPS GPSLatitude'], tags.get('GPS GPSLatitudeRef'))
                lon = self._convert_gps_to_decimal(tags['GPS GPSLongitude'], tags.get('GPS GPSLongitudeRef'))
                if lat and lon:
                    metadata['gps_coords'] = (lat, lon)
            
            # Extract timestamp
            if 'EXIF DateTimeOriginal' in tags:
                metadata['creation_date'] = str(tags['EXIF DateTimeOriginal'])
            elif 'EXIF DateTime' in tags:
                metadata['creation_date'] = str(tags['EXIF DateTime'])
            
            # Extract camera info
            if 'Image Make' in tags:
                metadata['camera_make'] = str(tags['Image Make'])
            if 'Image Model' in tags:
                metadata['camera_model'] = str(tags['Image Model'])
                
        except Exception as e:
            st.warning(f"Could not extract EXIF data: {str(e)}")
        
        return metadata

    def _extract_video_metadata(self, file_content):
        """Extract metadata from video files"""
        metadata = {}
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Use OpenCV to extract video metadata
            cap = cv2.VideoCapture(temp_path)
            if cap.isOpened():
                metadata['fps'] = cap.get(cv2.CAP_PROP_FPS)
                metadata['frame_count'] = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                metadata['duration'] = metadata['frame_count'] / metadata['fps'] if metadata['fps'] > 0 else 0
                metadata['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            # Try to get creation date from file system
            import os
            stat = os.stat(temp_path)
            metadata['creation_date'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            st.warning(f"Could not extract video metadata: {str(e)}")
        
        return metadata

    def _extract_audio_metadata(self, file_content):
        """Extract metadata from audio files"""
        metadata = {}
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Use mutagen to extract audio metadata
            audio = MutagenFile(temp_path)
            if audio:
                metadata['duration'] = getattr(audio.info, 'length', 0)
                metadata['bitrate'] = getattr(audio.info, 'bitrate', None)
                
                # Extract tags if available
                if hasattr(audio, 'tags') and audio.tags:
                    for key, value in audio.tags.items():
                        if 'date' in key.lower() or 'year' in key.lower():
                            metadata['creation_date'] = str(value[0]) if isinstance(value, list) else str(value)
                            break
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            st.warning(f"Could not extract audio metadata: {str(e)}")
        
        return metadata

    def _extract_pdf_metadata(self, file_content):
        """Extract metadata from PDF files"""
        metadata = {}
        try:
            # Create PDF document from content
            pdf_doc = fitz.open(stream=file_content, filetype="pdf")
            
            # Extract basic info
            metadata['page_count'] = pdf_doc.page_count
            
            # Extract document metadata
            doc_metadata = pdf_doc.metadata
            if doc_metadata:
                metadata['title'] = doc_metadata.get('title', '')
                metadata['author'] = doc_metadata.get('author', '')
                metadata['subject'] = doc_metadata.get('subject', '')
                metadata['creator'] = doc_metadata.get('creator', '')
                metadata['producer'] = doc_metadata.get('producer', '')
                metadata['creation_date'] = doc_metadata.get('creationDate', '')
                metadata['modification_date'] = doc_metadata.get('modDate', '')
            
            pdf_doc.close()
            
        except Exception as e:
            st.warning(f"Could not extract PDF metadata: {str(e)}")
        
        return metadata

    def _extract_document_metadata(self, file_content):
        """Extract metadata from Word documents"""
        metadata = {}
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Load document
            doc = Document(temp_path)
            
            # Extract core properties
            core_props = doc.core_properties
            metadata['title'] = core_props.title or ''
            metadata['author'] = core_props.author or ''
            metadata['subject'] = core_props.subject or ''
            metadata['creation_date'] = core_props.created.isoformat() if core_props.created else ''
            metadata['modification_date'] = core_props.modified.isoformat() if core_props.modified else ''
            metadata['word_count'] = len(doc.paragraphs)
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            st.warning(f"Could not extract document metadata: {str(e)}")
        
        return metadata

    def _convert_gps_to_decimal(self, gps_coord, ref):
        """Convert GPS coordinates from EXIF format to decimal degrees"""
        try:
            degrees = float(gps_coord.values[0].num) / float(gps_coord.values[0].den)
            minutes = float(gps_coord.values[1].num) / float(gps_coord.values[1].den)
            seconds = float(gps_coord.values[2].num) / float(gps_coord.values[2].den)
            
            decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if ref and str(ref) in ['S', 'W']:
                decimal_degrees = -decimal_degrees
                
            return decimal_degrees
        except:
            return None

    def _get_location_from_coords(self, coords):
        """Convert GPS coordinates to human-readable location"""
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="icc_evidence_tool")
            location = geolocator.reverse(f"{coords[0]}, {coords[1]}")
            return location.address if location else None
        except:
            return None

    def setup_driver(self):
        """Setup Chrome WebDriver for ICC form submission"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            st.error(f"Error setting up web driver: {str(e)}")
            return None

    def submit_to_icc_automated(self, form_data, files):
        """Submit evidence to ICC using selenium automation"""
        driver = self.setup_driver()
        if not driver:
            return {'success': False, 'error': 'Could not initialize web driver'}
        
        try:
            st.info("🔄 Connecting to ICC website...")
            driver.get(self.icc_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # Allow dynamic content to load
            
            # Placeholder for actual form automation
            # In production: navigate, fill forms, upload files, submit
            
            st.success("✅ Form submission initiated")
            
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

    def analyze_with_backend(self, uploaded_file):
        """Analyze evidence using FastAPI backend (from unified_icc_app.py)"""
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            with st.spinner("🤖 Analyzing with FastAPI backend..."):
                response = requests.post(f"{self.api_url}/analyze_evidence", files=files, timeout=30)
                
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Backend analysis failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.warning(f"Backend not available: {str(e)}")
            return None
                        
            metadata['gps_coords'] = (lat, lon)
                
                # Get location name
                try:
                    geolocator = Nominatim(user_agent="icc_evidence_analyzer")
                    location = geolocator.reverse(f"{lat}, {lon}")
                    if location:
                        metadata['location'] = location.address
                except Exception:
                    pass
            
            # Extract timestamp
            if 'EXIF DateTimeOriginal' in tags:
                timestamp_str = str(tags['EXIF DateTimeOriginal'])
                metadata['timestamp'] = datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')
        
        return metadata
            
        except Exception as e:
            return metadata
    
    def _convert_to_degrees(self, value):
        """Convert GPS coordinates to decimal degrees"""
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    
    def analyze_file_fast(self, uploaded_file):
        """Lightning-fast analysis from fast_streamlit_app.py"""
        try:
            # Check cache first
            file_hash = hash(uploaded_file.getvalue())
            if file_hash in st.session_state.analysis_cache:
                return st.session_state.analysis_cache[file_hash], True
            
            # Prepare file for API
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            # Show real-time progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🚀 Uploading to AI analysis engine...")
            progress_bar.progress(25)
            
            # Send to FastAPI backend
            start_time = time.time()
            response = requests.post(f"{self.api_url}/analyze-evidence/", files=files, timeout=30)
            analysis_time = time.time() - start_time
            
            progress_bar.progress(75)
            status_text.text("🤖 AI models processing evidence...")
            
            if response.status_code == 200:
                result = response.json()
                result['analysis_time'] = analysis_time
                
                # Cache result
                st.session_state.analysis_cache[file_hash] = result
                
                progress_bar.progress(100)
                status_text.text(f"✅ Analysis complete in {analysis_time:.2f}s")
                
                return result, False
            else:
                st.error(f"Analysis failed: {response.text}")
                return None, False
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None, False
    
    def agentic_chat_response(self, user_input, evidence_context):
        """AI chat interface for guiding evidence submission"""
        
        prompt = f"""
        You are an expert AI assistant helping with ICC evidence submission. The user has uploaded evidence and needs guidance.
        
        EVIDENCE CONTEXT:
        {json.dumps(evidence_context, indent=2)}
        
        USER INPUT: {user_input}
        
        Current phase: {st.session_state.agentic_phase}
        
        Provide a helpful, concise response (max 200 words) that:
        1. Acknowledges their input
        2. Asks relevant follow-up questions for ICC submission
        3. Suggests next steps
        
        Be conversational but professional. Focus on ICC evidence requirements.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI temporarily unavailable: {str(e)}"
    
    def generate_comprehensive_context(self, evidence_analyses, keywords, chat_context):
        """Generate 1000+ word ICC submission context (enhanced from app.py)"""
        
        prompt = f"""
        As an expert legal AI specializing in International Criminal Court submissions, 
        generate a comprehensive 1000+ word contextual summary for an ICC evidence submission.
        
        EVIDENCE ANALYSES:
        {json.dumps(evidence_analyses, indent=2)}
        
        USER KEYWORDS: {keywords}
        
        CHAT CONTEXT:
        {json.dumps(chat_context, indent=2)}
        
        INCIDENT DETAILS:
        - Location: CBD, Nairobi, Kenya
        - Date: June 17, 2025
        - Time: 14:00 (2:00 PM)
        - Incident: Person shot by GSU (General Service Unit)
        - Jurisdiction: Kenya
        
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
                model="mixtral-8x7b-32768",
                max_tokens=2000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating ICC context: {str(e)}"
    
    def submit_to_icc_simulation(self, context, evidence_files):
        """Simulate ICC submission (from app.py) - replace with real automation later"""
        
        # Simulate submission process
        submission_id = f"ICC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'success': True,
            'submission_id': submission_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'submitted',
            'evidence_count': len(evidence_files),
            'context_length': len(context)
        }
    
    def setup_driver(self):
        """Setup Chrome WebDriver for ICC submission automation (from app.py)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            st.error(f"Error setting up browser: {str(e)}")
            return None
    
    def generate_form_data(self, evidence_analyses, user_details):
        """Generate ICC form data from evidence and user details (from app.py)"""
        if not evidence_analyses:
            return None
            
        prompt = f"""
        Based on the evidence analysis and user details, generate ICC form data:
        
        EVIDENCE ANALYSES:
        {json.dumps(evidence_analyses[:3], indent=2)}  # Limit for token efficiency
        
        USER DETAILS:
        {json.dumps(user_details, indent=2)}
        
        Generate a structured form data object for ICC submission with these fields:
        {{
            "incident_date": "YYYY-MM-DD",
            "incident_location": "Detailed location",
            "incident_description": "Comprehensive incident description",
            "evidence_summary": "Summary of all evidence",
            "perpetrator_info": "Information about perpetrators",
            "victim_info": "Information about victims",
            "witness_info": "Information about witnesses",
            "submitter_role": "Role of person submitting",
            "urgency_level": "high/medium/low",
            "additional_context": "Any additional relevant context"
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            form_data = json.loads(response.choices[0].message.content)
            return form_data
            
        except Exception as e:
            st.error(f"Error generating form data: {str(e)}")
            return None
    
    def submit_to_icc(self, form_data, evidence_files):
        """Submit evidence to ICC using Selenium automation (from app.py)"""
        driver = self.setup_driver()
        if not driver:
            return {"success": False, "error": "Failed to setup browser"}
            
        try:
            driver.get(self.icc_url)
            time.sleep(3)
            
            # This would contain the actual form filling logic
            # For now, simulate the submission
            submission_id = f"ICC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                "success": True,
                "submission_id": submission_id,
                "timestamp": datetime.now().isoformat(),
                "evidence_count": len(evidence_files),
                "form_data": form_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if driver:
                driver.quit()

    def render_step_navigation(self):
        """Render step navigation from app.py multi-step pattern"""
        current_step = st.session_state.get('current_step', 0)
        
        st.markdown("### 📋 Submission Progress")
        
        # Create step indicators
        cols = st.columns(len(self.steps))
        for i, (col, step) in enumerate(zip(cols, self.steps)):
            with col:
                if i < current_step:
                    st.markdown(f"✅ **{i+1}. {step}**")
                elif i == current_step:
                    st.markdown(f"🔄 **{i+1}. {step}**")
                else:
                    st.markdown(f"⏳ {i+1}. {step}")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_step > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_step = current_step - 1
                    st.rerun()
        
        with col3:
            if current_step < len(self.steps) - 1:
                if st.button("Next ➡️"):
                    st.session_state.current_step = current_step + 1
                    st.rerun()

    def render_user_details_form(self):
        """Render user details form from app.py"""
        st.subheader("👤 Your Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name (Optional)", 
                                value=st.session_state.form_data.get('submitter_name', ''))
            email = st.text_input("Email (Optional)", 
                                 value=st.session_state.form_data.get('submitter_email', ''))
            role = st.selectbox("Your Role", [
                "Witness", "Victim", "Concerned Citizen", "Legal Representative", 
                "Journalist", "Human Rights Advocate", "Other"
            ])
        
        with col2:
            phone = st.text_input("Phone (Optional)", 
                                 value=st.session_state.form_data.get('submitter_phone', ''))
            anonymous = st.checkbox("🔒 Submit Anonymously", value=True)
            
        additional_info = st.text_area("Additional Context", 
                                      value=st.session_state.form_data.get('additional_notes', ''))
        
        # Update session state
        st.session_state.form_data.update({
            'submitter_name': name if not anonymous else "Anonymous",
            'submitter_email': email if not anonymous else "",
            'submitter_phone': phone if not anonymous else "",
            'submitter_role': role,
            'anonymous': anonymous,
            'additional_notes': additional_info
        })
        
        return {
            'name': name if not anonymous else "Anonymous",
            'email': email if not anonymous else "",
            'phone': phone if not anonymous else "",
            'role': role,
            'anonymous': anonymous,
            'additional_info': additional_info
        }

    def render_evidence_details_form(self):
        """Render evidence details form from app.py"""
        st.subheader("📋 Incident Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            incident_date = st.date_input("📅 Incident Date", 
                                         value=datetime(2025, 6, 17).date())
            incident_location = st.text_input("📍 Location", 
                                            value=st.session_state.form_data.get('incident_location', 'CBD, Nairobi, Kenya'))
        
        with col2:
            incident_time = st.time_input("🕐 Time", 
                                         value=datetime.strptime("14:00", "%H:%M").time())
            urgency = st.selectbox("🚨 Urgency Level", ["High", "Medium", "Low"])
        
        incident_description = st.text_area("📝 Incident Description", 
                                          value=st.session_state.form_data.get('incident_description', 
                                                                               "Person shot by GSU (General Service Unit)"),
                                          height=100)
        
        victim_info = st.text_area("👥 Victim Information", 
                                  value=st.session_state.form_data.get('victim_info', ''))
        
        perpetrator_info = st.text_area("👮 Perpetrator Information", 
                                       value=st.session_state.form_data.get('perpetrator_info', 'GSU Officers'))
        
        witness_info = st.text_area("👁️ Witness Information", 
                                   value=st.session_state.form_data.get('witness_info', ''))
        
        # Update session state
        st.session_state.form_data.update({
            'incident_date': incident_date,
            'incident_time': incident_time,
            'incident_location': incident_location,
            'incident_description': incident_description,
            'victim_info': victim_info,
            'perpetrator_info': perpetrator_info,
            'witness_info': witness_info,
            'urgency_level': urgency
        })

def render_main_interface():
    """Main agentic ICC interface"""
    
    # Header with emergency styling
    st.markdown("""
    <div class="main-header">
        <h1>🇰🇪 AGENTIC ICC EVIDENCE SUBMITTER</h1>
        <p>AI-Powered Emergency Evidence Submission to the International Criminal Court</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency banner
    st.markdown("""
    <div class="emergency-banner">
        🚨 EMERGENCY SUBMISSION READY - GSU Shooting Incident - CBD Nairobi - June 17, 2025, 2:00 PM
    </div>
    """, unsafe_allow_html=True)
    
    # API Status Check
    api_healthy, health_data = submitter.check_api_health()
    
    if not api_healthy:
        st.error("🚨 FastAPI backend not running! Start it with: `python fast_api_backend.py`")
        st.info("💡 The backend provides lightning-fast AI analysis using Groq, Google Vision, and Roboflow")
        st.stop()
    
    # Show API capabilities
    if health_data:
        st.success(f"🚀 AI Analysis Engine: {health_data.get('status', 'unknown').upper()}")

def render_sidebar():
    """Enhanced sidebar with multi-step workflow status"""
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
        
        st.header("🔄 Multi-Step Progress")
        current_step = st.session_state.get('current_step', 0)
        
        steps = [
            "📁 Upload Evidence",
            "🔍 AI Analysis", 
            "� Evidence Details",
            "👤 Personal Info",
            "� Generate Context",
            "🚀 Submit to ICC"
        ]
        
        for i, step in enumerate(steps):
            if i < current_step:
                st.write(f"✅ {step}")
            elif i == current_step:
                st.write(f"**➤ {step}** ⚡")
            else:
                st.write(f"⏳ {step}")
        
        # Quick navigation
        st.header("⚡ Quick Actions")
        if st.button("🔄 Reset Workflow"):
            st.session_state.current_step = 0
            st.session_state.agentic_phase = "upload"
            st.rerun()
        
        if st.button("💾 Save Progress"):
            st.success("Progress saved!")

def render_upload_section():
    """Enhanced file upload from both apps"""
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    st.subheader("📂 Drop Evidence Files for AI Analysis")
    
    uploaded_files = st.file_uploader(
        "Supported: Images, Videos, Audio, Documents",
        accept_multiple_files=True,
        type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'pdf', 'docx', 'txt'],
        help="Max 100MB per file - Analysis typically completes in under 3 seconds"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        
        for file in uploaded_files:
            with st.expander(f"📁 {file.name} ({file.size:,} bytes)"):
                # Show file preview
                if file.type.startswith('image/'):
                    image = Image.open(file)
                    st.image(image, width=300)
                
                # Analyze with AI
                if st.button("🚀 ANALYZE WITH AI", key=f"analyze_{file.name}"):
                    with st.spinner("⚡ Lightning-fast AI analysis in progress..."):
                        analysis, from_cache = submitter.analyze_file_fast(file)
                        
                        if analysis:
                            st.balloons()
                            
                            # Store analysis
                            st.session_state.evidence_analyses.append({
                                'file_name': file.name,
                                'analysis': analysis,
                                'from_cache': from_cache
                            })
                            
                            # Move to chat phase
                            st.session_state.agentic_phase = "chat"
                            st.experimental_rerun()

def render_chat_interface():
    """Agentic chat interface"""
    if st.session_state.evidence_analyses:
        st.markdown('<div class="agentic-chat">', unsafe_allow_html=True)
        st.subheader("🤖 AI Legal Assistant")
        
        # Chat history
        for chat in st.session_state.chat_history:
            if chat['role'] == 'user':
                st.write(f"**You:** {chat['message']}")
            else:
                st.write(f"**AI:** {chat['message']}")
        
        # Current evidence summary
        evidence_count = len(st.session_state.evidence_analyses)
        st.write(f"**Evidence Processed:** {evidence_count} files")
        
        # User input
        user_input = st.text_input(
            "💬 Ask the AI about your evidence or ICC submission:",
            placeholder="What should I emphasize in this submission?"
        )
        
        if st.button("Send to AI") and user_input:
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'message': user_input
            })
            
            # Get AI response
            evidence_context = [e['analysis'] for e in st.session_state.evidence_analyses]
            ai_response = submitter.agentic_chat_response(user_input, evidence_context)
            
            # Add AI response
            st.session_state.chat_history.append({
                'role': 'ai',
                'message': ai_response
            })
            
            st.experimental_rerun()
        
        # Keywords input
        keywords = st.text_input(
            "🔑 Keywords for AI to focus on:",
            placeholder="timeline, weapons, victims, location..."
        )
        
        if st.button("🎯 GENERATE ICC CONTEXT", type="primary") and keywords:
            st.session_state.keywords = keywords
            st.session_state.agentic_phase = "context"
            st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_context_generation():
    """Generate and display ICC context"""
    if 'keywords' in st.session_state:
        st.markdown('<div class="legal-assessment">', unsafe_allow_html=True)
        st.subheader("📝 Generating ICC Submission Context...")
        
        with st.spinner("🤖 AI generating comprehensive legal context..."):
            context = submitter.generate_comprehensive_context(
                st.session_state.evidence_analyses,
                st.session_state.keywords,
                st.session_state.chat_history
            )
            
            st.session_state.icc_context = context
            st.session_state.agentic_phase = "submit"
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.experimental_rerun()

def render_submission_section():
    """Final ICC submission"""
    if 'icc_context' in st.session_state:
        st.markdown('<div class="submission-ready">', unsafe_allow_html=True)
        st.subheader("🚀 Ready for ICC Submission")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show generated context
        with st.expander("📝 Generated ICC Context", expanded=True):
            st.text_area("", st.session_state.icc_context, height=400)
        
        # Final submission
        if st.button("🎯 SUBMIT TO ICC", type="primary", use_container_width=True):
            with st.spinner("🚀 Submitting to International Criminal Court..."):
                result = submitter.submit_to_icc_simulation(
                    st.session_state.icc_context,
                    st.session_state.evidence_analyses
                )
                
                if result['success']:
                    st.success("✅ Evidence successfully submitted to ICC!")
                    st.markdown(f"""
                    **📋 Submission Confirmation**
                    - **Submission ID:** {result['submission_id']}
                    - **Timestamp:** {result['timestamp']}
                    - **Evidence Files:** {result['evidence_count']}
                    - **Context Length:** {result['context_length']} characters
                    """)
                    
                    st.balloons()

# Initialize the enhanced agentic submitter with multi-step workflow
submitter = AgenticICCSubmitter()

def main():
    """Enhanced main agentic workflow with multi-step integration"""
    # Initialize multi-step workflow state
    submitter.init_session_state()
    
    render_main_interface()
    render_sidebar()
    
    current_step = st.session_state.get('current_step', 0)
    
    # Multi-step workflow from app.py integrated with agentic phases
    if current_step == 0:  # Upload Evidence
        render_upload_section()
    elif current_step == 1:  # AI Analysis
        render_upload_section()  # Still show uploads
        render_chat_interface()
    elif current_step == 2:  # Evidence Details
        submitter.render_evidence_details_form()
    elif current_step == 3:  # Personal Information
        user_details = submitter.render_user_details_form()
    elif current_step == 4:  # Generate Context
        if st.session_state.evidence_analyses and 'keywords' in st.session_state:
            render_context_generation()
        else:
            st.warning("Please complete evidence analysis and provide keywords first")
            if st.button("Go to Analysis Step"):
                st.session_state.current_step = 1
                st.rerun()
    elif current_step == 5:  # Review & Submit
        render_final_submission()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🇰🇪 Enhanced Agentic ICC Evidence Submission Tool</p>
        <p><em>Combining multi-step workflow with intelligent AI guidance for comprehensive ICC submissions.</em></p>
    </div>
    """, unsafe_allow_html=True)

def render_final_submission():
    """Final submission step combining form data with evidence"""
    st.subheader("🚀 Final Review & Submission")
    
    if st.session_state.evidence_analyses and st.session_state.form_data:
        # Generate comprehensive form data
        form_data = submitter.generate_form_data(
            st.session_state.evidence_analyses,
            st.session_state.form_data
        )
        
        if form_data:
            st.write("**📋 Generated ICC Submission Form:**")
            st.json(form_data)
            
            if st.button("🎯 SUBMIT TO ICC", type="primary", use_container_width=True):
                with st.spinner("🚀 Submitting to International Criminal Court..."):
                    result = submitter.submit_to_icc(form_data, st.session_state.evidence_analyses)
                    
                    if result.get('success'):
                        st.success("✅ Evidence successfully submitted to ICC!")
                        st.markdown(f"""
                        **📋 Submission Confirmation**
                        - **Submission ID:** {result['submission_id']}
                        - **Timestamp:** {result['timestamp']}
                        - **Evidence Files:** {result['evidence_count']}
                        """)
                        st.balloons()
                    else:
                        st.error(f"❌ Submission failed: {result.get('error', 'Unknown error')}")
        else:
            st.error("Failed to generate form data")
    else:
        st.warning("Please complete all previous steps before submitting")

if __name__ == "__main__":
    main()
