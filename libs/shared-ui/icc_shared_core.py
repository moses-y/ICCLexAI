"""
🇰🇪 ICCLexAI Shared Core Functions
Consolidates common functionality from all ICC apps to eliminate duplication
Environment variables and deployment-ready configurations
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from pathlib import Path
import requests

# Load environment variables
load_dotenv()

# Kenyan Flag Color Palette (Standardized across all apps)
KENYAN_COLORS = {
    'black': '#000000',
    'red': '#D32F2F',
    'green': '#388E3C',
    'white': '#FFFFFF',
    'dark_green': '#006600',
    'light_green': 'rgba(0, 128, 0, 0.05)'
}

# Environment Variables (Centralized)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "yPJeGngSi2zDs1ligb0I")

# Service URLs (Deployment ready)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
ICC_URL = "https://otplink.icc-cpi.int/"

# Fixed incident context for all apps
INCIDENT_CONTEXT = {
    "date": "2025-06-17",
    "time": "14:00",
    "location": "CBD, Nairobi, Kenya",
    "incident": "Person shot by GSU (General Service Unit)",
    "jurisdiction": "Kenya",
    "urgency": "high"
}

class SharedComponents:
    """Shared UI components used across all ICC apps"""
    
    @staticmethod
    def setup_page_config(title: str = "ICC Evidence Submission", icon: str = "🇰🇪"):
        """Standardized page configuration"""
        st.set_page_config(            page_title=f"🇰🇪 {title}",
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    @staticmethod
    def setup_kenyan_css():
        """Optimized CSS loading from external file"""
        try:
            # Load external CSS file for better maintainability
            css_path = Path(__file__).parent / "kenyan_theme.css"
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            else:
                # Fallback to inline CSS if file not found
                st.markdown(f"""
                <style>
                .main-header {{
                    background: linear-gradient(90deg, {KENYAN_COLORS['black']} 20%, {KENYAN_COLORS['white']} 20% 22%, {KENYAN_COLORS['red']} 22% 78%, {KENYAN_COLORS['white']} 78% 80%, {KENYAN_COLORS['green']} 80%);
                    padding: 1.5rem;
                    text-align: center;
                    color: {KENYAN_COLORS['black']};
                    font-weight: bold;
                    font-size: 2rem;
                    margin: 10px 0;
                    text-shadow: 2px 2px 4px rgba(255,255,255,0.9);
                    border-radius: 12px;
                }}
                .stButton > button {{
                    background: linear-gradient(45deg, {KENYAN_COLORS['green']} 0%, {KENYAN_COLORS['black']} 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-weight: bold;
                }}
                </style>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"CSS loading failed: {e}. Using minimal styling.")
    
    @staticmethod
    def render_header(title: str, subtitle: str = "AI-Powered Evidence Submission"):
        """Standardized header across all apps"""
        st.markdown(f"""
        <div class="main-header">
            <h1>🇰🇪 {title}</h1>
            <p>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_emergency_banner():
        """Standardized emergency banner"""
        st.markdown("""
        <div class="emergency-banner">
            🚨 EMERGENCY SUBMISSION - GSU Shooting Incident - CBD Nairobi - June 17, 2025, 2:00 PM
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar():
        """Standardized sidebar content"""
        with st.sidebar:
            st.header("📋 Incident Information")
            st.write(f"**Date:** {INCIDENT_CONTEXT['date']}")
            st.write(f"**Time:** {INCIDENT_CONTEXT['time']}")
            st.write(f"**Location:** {INCIDENT_CONTEXT['location']}")
            st.write(f"**Incident:** {INCIDENT_CONTEXT['incident']}")
            st.write(f"**Status:** Active Evidence Collection")
            
            st.header("📞 Emergency Contacts")
            st.write("**ICC OTP:** +31 70 515 8515")
            st.write("**Kenya Human Rights:** +254 20 272 1113")
            
            st.header("ℹ️ Submission Guidelines")
            st.write("• Ensure evidence is authentic")
            st.write("• Provide clear descriptions")
            st.write("• Include location/time data")
            st.write("• Protect witness identity if needed")

class SharedFileHandling:
    """Shared file handling functionality"""
    
    SUPPORTED_TYPES = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
        'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg'],
        'document': ['.pdf', '.doc', '.docx', '.txt']
    }
    
    @staticmethod
    def render_file_uploader(key: str = "evidence_files", multiple: bool = True) -> List:
        """Standardized file uploader"""
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        st.subheader("📂 Drop Evidence Files for AI Analysis")
        
        uploaded_files = st.file_uploader(
            "Supported: Images, Videos, Audio, Documents",
            accept_multiple_files=multiple,
            type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'pdf', 'docx', 'txt'],
            help="Max 100MB per file - AI analysis available",
            key=key
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        return uploaded_files
    
    @staticmethod
    def preview_file(uploaded_file) -> None:
        """Standardized file preview"""
        if uploaded_file.type.startswith('image/'):
            image = Image.open(uploaded_file)
            st.image(image, width=300)
        else:
            st.info(f"**Type:** {uploaded_file.type}\\n**Size:** {uploaded_file.size:,} bytes")
    
    @staticmethod
    def get_file_category(file_type: str) -> str:
        """Determine file category"""
        for category, extensions in SharedFileHandling.SUPPORTED_TYPES.items():
            if any(ext in file_type.lower() for ext in extensions):
                return category
        return 'other'

class SharedAI:
    """Shared AI functionality across all apps"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    
    def check_api_health(self) -> tuple[bool, Optional[Dict]]:
        """Check FastAPI backend health"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=3)
            return response.status_code == 200, response.json()
        except Exception:
            return False, None
    
    def analyze_evidence_basic(self, file_content: bytes, file_type: str, 
                              additional_context: str = "") -> Dict[str, Any]:
        """Basic evidence analysis using Groq"""
        if not self.groq_client:
            return {"error": "Groq API not configured"}
        
        prompt = f"""
        Analyze this evidence file for ICC submission regarding the GSU shooting incident:
        
        INCIDENT CONTEXT:
        - Date: {INCIDENT_CONTEXT['date']}
        - Time: {INCIDENT_CONTEXT['time']}
        - Location: {INCIDENT_CONTEXT['location']}
        - Incident: {INCIDENT_CONTEXT['incident']}
        
        FILE INFO:
        - Type: {file_type}
        - Additional Context: {additional_context}
        
        Provide analysis in JSON format:
        {{
            "evidence_type": "photograph|video|audio|document|witness_statement|other",
            "evidence_description": "Clear description of evidence content",
            "incident_relation": "How evidence relates to the incident",
            "relevance_score": "1-10 relevance rating",
            "legal_significance": "Why this evidence is legally significant",
            "icc_relevance": "high|medium|low",
            "evidence_quality": "excellent|good|fair|poor",
            "recommended_action": "Next steps for this evidence"
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def generate_submission_context(self, evidence_analyses: List[Dict], 
                                  user_context: str = "") -> str:
        """Generate comprehensive ICC submission context"""
        if not self.groq_client:
            return "AI context generation not available"
        
        prompt = f"""
        Generate comprehensive ICC submission context for GSU shooting incident:
        
        INCIDENT: {INCIDENT_CONTEXT['incident']}
        LOCATION: {INCIDENT_CONTEXT['location']}
        DATE/TIME: {INCIDENT_CONTEXT['date']} {INCIDENT_CONTEXT['time']}
        
        EVIDENCE ANALYSES:
        {json.dumps(evidence_analyses, indent=2)}
        
        USER CONTEXT: {user_context}
        
        Generate a professional 800+ word ICC submission context covering:
        1. Executive Summary
        2. Incident Description
        3. Evidence Analysis
        4. Legal Significance
        5. Recommended Action
        
        Focus on human rights violations and excessive force by state agents.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating context: {str(e)}"

class SharedCache:
    """Shared caching functionality"""
    
    @staticmethod
    def init_cache():
        """Initialize session state cache"""
        if 'icc_cache' not in st.session_state:
            st.session_state.icc_cache = {
                'evidence_analyses': {},
                'form_data': {},
                'submission_history': []
            }
    
    @staticmethod
    def cache_analysis(file_name: str, analysis: Dict) -> None:
        """Cache analysis result"""
        SharedCache.init_cache()
        file_hash = hashlib.md5(file_name.encode()).hexdigest()
        st.session_state.icc_cache['evidence_analyses'][file_hash] = {
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'file_name': file_name
        }
    
    @staticmethod
    def get_cached_analysis(file_name: str) -> Optional[Dict]:
        """Get cached analysis"""
        SharedCache.init_cache()
        file_hash = hashlib.md5(file_name.encode()).hexdigest()
        return st.session_state.icc_cache['evidence_analyses'].get(file_hash)
    
    @staticmethod
    def clear_cache():
        """Clear all cached data"""
        if 'icc_cache' in st.session_state:
            del st.session_state.icc_cache
        st.success("Cache cleared successfully!")

class SharedSubmission:
    """Shared submission functionality"""
    
    @staticmethod
    def generate_submission_id() -> str:
        """Generate unique submission ID"""
        return f"ICC-KE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    @staticmethod
    def simulate_icc_submission(form_data: Dict, evidence_files: List) -> Dict:
        """Simulate ICC submission for all apps"""
        time.sleep(2)  # Simulate processing
        
        submission_id = SharedSubmission.generate_submission_id()
        
        result = {
            'success': True,
            'submission_id': submission_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'submitted',
            'evidence_count': len(evidence_files),
            'form_data_size': len(json.dumps(form_data)) if form_data else 0,
            'incident_context': INCIDENT_CONTEXT
        }
        
        # Store in cache
        SharedCache.init_cache()
        st.session_state.icc_cache['submission_history'].append(result)
        
        return result
    
    @staticmethod
    def render_submission_success(submission_result: Dict):
        """Standardized submission success display"""
        st.balloons()
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {KENYAN_COLORS['green']}, {KENYAN_COLORS['black']}); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <h3>🎉 Evidence Successfully Submitted to ICC!</h3>
            <p><strong>Submission ID:</strong> {submission_result['submission_id']}</p>
            <p><strong>Timestamp:</strong> {submission_result['timestamp']}</p>
            <p><strong>Evidence Files:</strong> {submission_result['evidence_count']}</p>
            <p><strong>Status:</strong> SUBMITTED TO ICC</p>
            <p><em>Your evidence has been submitted to the International Criminal Court for review.</em></p>
        </div>
        """, unsafe_allow_html=True)

class SharedUtils:
    """Shared utility functions"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/1024**2:.1f} MB"
        else:
            return f"{size_bytes/1024**3:.1f} GB"
    
    @staticmethod
    def get_environment_status() -> Dict[str, bool]:
        """Check environment variables status"""
        return {
            'groq_api': bool(GROQ_API_KEY),
            'google_api': bool(GOOGLE_API_KEY),
            'huggingface': bool(HUGGINGFACE_TOKEN),
            'roboflow': bool(ROBOFLOW_API_KEY)
        }
    
    @staticmethod
    def render_environment_status():
        """Display environment status in sidebar"""
        env_status = SharedUtils.get_environment_status()
        
        st.sidebar.markdown("---")
        st.sidebar.header("🔧 Environment Status")
        
        for service, status in env_status.items():
            status_icon = "✅" if status else "❌"
            st.sidebar.write(f"{status_icon} **{service.replace('_', ' ').title()}:** {'Ready' if status else 'Not configured'}")

# Export commonly used instances
shared_ai = SharedAI()
shared_components = SharedComponents()
shared_file_handling = SharedFileHandling()
shared_cache = SharedCache()
shared_submission = SharedSubmission()
shared_utils = SharedUtils()

# Quick initialization function for apps
def initialize_app(title: str, subtitle: str = "AI-Powered Evidence Submission"):
    """Quick app initialization with all shared components"""
    shared_components.setup_page_config(title)
    shared_components.setup_kenyan_css()
    shared_components.render_header(title, subtitle)
    shared_components.render_emergency_banner()
    shared_components.render_sidebar()
    shared_utils.render_environment_status()
    shared_cache.init_cache()
    
    return {
        'ai': shared_ai,
        'components': shared_components,
        'files': shared_file_handling,
        'cache': shared_cache,
        'submission': shared_submission,
        'utils': shared_utils
    }
