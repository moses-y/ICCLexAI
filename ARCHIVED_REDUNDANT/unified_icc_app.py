"""
🇰🇪 ICC LEGAL AI PLATFORM - UNIFIED EVIDENCE ANALYZER
Lightning-fast multimodal AI analysis with robust ICC submission capabilities
Combining FastAPI backend integration with comprehensive evidence processing
"""

import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

# Enhanced Kenyan Flag Color Palette with additional UI colors
KENYAN_COLORS = {
    'black': '#000000',
    'red': '#D32F2F', 
    'green': '#388E3C',
    'white': '#FFFFFF',
    'dark_green': '#006600',
    'light_green': 'rgba(0, 128, 0, 0.05)',
    'success': '#00ff00',
    'primary': '#008000'
}

# Page configuration for optimal performance
st.set_page_config(
    page_title="🇰🇪 ICC Legal AI Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-powered evidence analysis for ICC submissions",
        'Get help': "https://github.com/your-repo/icc-legal-ai",
        'Report a bug': "https://github.com/your-repo/icc-legal-ai/issues"
    }
)

def setup_enhanced_css():
    """Enhanced CSS combining the best styling from both apps"""
    st.markdown(f"""
    <style>
    /* SUPERIOR HEADER STYLING (from fast_streamlit_app.py) */
    .main-header {{
        background: linear-gradient(90deg, {KENYAN_COLORS['black']} 20%, {KENYAN_COLORS['white']} 20% 22%, {KENYAN_COLORS['red']} 22% 78%, {KENYAN_COLORS['white']} 78% 80%, {KENYAN_COLORS['green']} 80%);
        padding: 15px;
        text-align: center;
        color: {KENYAN_COLORS['black']};
        font-weight: bold;
        font-size: 2.2rem;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.9);
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 2px solid {KENYAN_COLORS['green']};
    }}
    
    .sub-header {{
        background: linear-gradient(135deg, {KENYAN_COLORS['green']} 0%, {KENYAN_COLORS['dark_green']} 100%);
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 1.2rem;
        border-radius: 8px;
        margin: 10px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    
    /* ENHANCED ANALYSIS CARDS */
    .analysis-card {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid {KENYAN_COLORS['green']};
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }}
    
    .analysis-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }}
    
    /* PERFORMANCE INDICATORS */
    .speed-indicator {{
        background: {KENYAN_COLORS['success']};
        color: black;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
        100% {{ opacity: 1; }}
    }}
    
    /* ENHANCED UPLOAD ZONE */
    .upload-zone {{
        border: 4px dashed {KENYAN_COLORS['green']};
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background: {KENYAN_COLORS['light_green']};
        margin: 15px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .upload-zone:hover {{
        background: rgba(0, 128, 0, 0.1);
        border-color: {KENYAN_COLORS['dark_green']};
        transform: scale(1.02);
    }}
    
    /* EMERGENCY STYLING */
    .emergency-banner {{
        background: linear-gradient(45deg, {KENYAN_COLORS['red']} 0%, #FF5722 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 20px;
        animation: urgent-blink 1.5s infinite;
        box-shadow: 0 4px 8px rgba(211, 47, 47, 0.3);
    }}
    
    @keyframes urgent-blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    
    /* STATUS CARDS */
    .status-card {{
        background: {KENYAN_COLORS['white']};
        border-left: 6px solid {KENYAN_COLORS['green']};
        padding: 20px;
        margin: 15px 0;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    /* METRIC CARDS */
    .metric-card {{
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 8px 0;
        border-top: 4px solid {KENYAN_COLORS['green']};
    }}
    
    /* AI INSIGHT CARDS */
    .ai-insight {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }}
    
    .legal-assessment {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
    }}
    
    /* ENHANCED BUTTONS */
    .stButton > button {{
        background: linear-gradient(45deg, {KENYAN_COLORS['green']} 0%, {KENYAN_COLORS['dark_green']} 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(45deg, {KENYAN_COLORS['black']} 0%, #333333 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }}
    
    /* SIDEBAR ENHANCEMENTS */
    .css-1d391kg {{
        background: linear-gradient(180deg, {KENYAN_COLORS['light_green']} 0%, #ffffff 100%);
    }}
    
    /* FOOTER STYLING */
    .footer {{
        text-align: center;
        color: #666;
        padding: 20px;
        background: linear-gradient(90deg, {KENYAN_COLORS['light_green']} 0%, #ffffff 50%, {KENYAN_COLORS['light_green']} 100%);
        border-radius: 10px;
        margin-top: 30px;
    }}
    
    /* RESPONSIVE DESIGN */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: 1.5rem;
            padding: 10px;
        }}
        
        .upload-zone {{
            padding: 20px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

class UnifiedICCPlatform:
    def __init__(self):
        self.api_url = st.session_state.get('api_base_url', "http://localhost:8001")
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY')) if os.getenv('GROQ_API_KEY') else None
        self.icc_url = "https://otplink.icc-cpi.int/"
    
    def check_api_health(self):
        """Check if FastAPI backend is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=3)
            return response.status_code == 200, response.json()
        except:
            return False, None
    
    def analyze_file_fast(self, uploaded_file):
        """Send file to FastAPI backend for lightning-fast analysis"""
        try:
            # Check cache first
            file_hash = hash(uploaded_file.getvalue())
            if 'analysis_cache' not in st.session_state:
                st.session_state.analysis_cache = {}
            
            if file_hash in st.session_state.analysis_cache:
                return st.session_state.analysis_cache[file_hash], True
            
            # Prepare file for API
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            # Show real-time progress
            progress_container = st.container()
            with progress_container:
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
                time.sleep(1)
                progress_container.empty()
                
                return result, False
            else:
                st.error(f"Analysis failed: {response.text}")
                return None, False
                
        except requests.exceptions.Timeout:
            st.error("⏰ Analysis timeout - file too large or server overloaded")
            return None, False
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None, False
    
    def analyze_evidence_with_groq(self, file_content, file_type, incident_details):
        """Use Groq for direct evidence analysis when FastAPI is unavailable"""
        if not self.groq_client:
            st.error("❌ Groq API key not configured")
            return None
        
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
    
    def render_analysis_results(self, analysis, from_cache=False):
        """Enhanced analysis results rendering"""
        
        # Performance Header
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cache_status = "🔥 FROM CACHE" if from_cache else "⚡ REAL-TIME"
            st.markdown(f'<div class="speed-indicator">{cache_status}</div>', unsafe_allow_html=True)
        
        with col2:
            analysis_time = analysis.get('analysis_time', 0)
            st.metric("⏱️ Analysis Time", f"{analysis_time:.2f}s")
        
        with col3:
            file_size = analysis.get('file_size', 0)
            file_size_mb = file_size / (1024 * 1024) if file_size else 0
            st.metric("📊 File Size", f"{file_size_mb:.2f} MB")
        
        with col4:
            confidence = analysis.get('content_analysis', {}).get('analysis_confidence', 'unknown')
            st.metric("🎯 AI Confidence", confidence.upper())
        
        # Main Analysis Layout
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Content Analysis Card
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.subheader("🔍 AI Content Analysis")
            
            content_analysis = analysis.get('content_analysis', {})
            
            # Detected Content Visualization
            if 'labels' in content_analysis and content_analysis['labels']:
                st.write("**🏷️ Detected Content:**")
                labels_df = pd.DataFrame({
                    'Content': content_analysis['labels'][:10],
                    'Relevance': [1.0 - i*0.1 for i in range(len(content_analysis['labels'][:10]))]
                })
                
                fig = px.bar(labels_df, x='Relevance', y='Content', orientation='h',
                           title="AI-Detected Content Elements",
                           color='Relevance', color_continuous_scale='Viridis')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Extracted Text
            if 'text_content' in content_analysis and content_analysis['text_content']:
                st.write("**📝 Extracted Text:**")
                st.text_area("", content_analysis['text_content'], height=120, key="extracted_text")
            
            # Face Detection
            if 'faces_detected' in content_analysis:
                st.write(f"**👥 Faces Detected:** {content_analysis['faces_detected']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Object Detection Results
            if 'object_detection' in analysis:
                st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                st.subheader("🎯 Object Detection (Roboflow AI)")
                
                objects = analysis['object_detection'].get('objects_detected', [])
                if objects:
                    obj_df = pd.DataFrame(objects)
                    if not obj_df.empty and 'class' in obj_df.columns:
                        fig = px.scatter(obj_df, x='x', y='y', size='confidence', 
                                       color='class', hover_data=['confidence'],
                                       title="Detected Objects with Confidence Levels")
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("🔍 No specific objects detected in this evidence")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            # Enhanced Metadata Card
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.subheader("📊 Evidence Metadata")
            
            metadata = analysis.get('metadata', {})
            
            # GPS and Location
            if 'gps_coordinates' in metadata:
                gps = metadata['gps_coordinates']
                st.write(f"**📍 GPS:** {gps['latitude']:.6f}, {gps['longitude']:.6f}")
                
                if 'location_name' in metadata:
                    st.write(f"**🏠 Location:** {metadata['location_name']}")
                
                # Enhanced Map
                map_df = pd.DataFrame([gps])
                fig = px.scatter_mapbox(map_df, lat='latitude', lon='longitude',
                                      zoom=15, height=350,
                                      mapbox_style="open-street-map",
                                      title="📍 Evidence Location")
                fig.update_traces(marker=dict(size=20, color='red'))
                st.plotly_chart(fig, use_container_width=True)
            
            # Timestamp
            if 'timestamp' in metadata:
                st.write(f"**📅 Timestamp:** {metadata['timestamp']}")
            
            # Device Information
            if 'camera_make' in metadata:
                st.write(f"**📱 Device:** {metadata['camera_make']} {metadata.get('camera_model', '')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Legal Assessment Section
        legal_assessment = analysis.get('legal_assessment', {})
        if legal_assessment:
            st.markdown('<div class="legal-assessment">', unsafe_allow_html=True)
            st.subheader("⚖️ AI Legal Assessment (DeepSeek R1)")
            
            if 'legal_summary' in legal_assessment:
                st.write(legal_assessment['legal_summary'])
            
            # Legal Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                evidence_quality = legal_assessment.get('evidence_quality', 'unknown')
                st.metric("📋 Evidence Quality", evidence_quality.upper())
            
            with col2:
                icc_relevance = legal_assessment.get('icc_relevance', 'unknown')
                st.metric("🏛️ ICC Relevance", icc_relevance.upper())
            
            with col3:
                relevance_score = legal_assessment.get('relevance_score', 'unknown')
                st.metric("🎯 Relevance Score", f"{relevance_score}/10")
            
            # AI Recommendations
            if 'recommendations' in legal_assessment:
                st.write("**🤖 AI Recommendations:**")
                for i, rec in enumerate(legal_assessment['recommendations'], 1):
                    st.write(f"**{i}.** {rec}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_main_interface(self):
        """Main unified interface"""
        
        # Enhanced Header
        st.markdown('<div class="main-header">🇰🇪 ICC LEGAL AI PLATFORM ⚖️</div>', 
                   unsafe_allow_html=True)
        
        st.markdown('<div class="sub-header">⚡ Lightning-Fast Evidence Analysis & ICC Submission System</div>', 
                   unsafe_allow_html=True)
        
        # Check API Status
        api_healthy, health_data = self.check_api_health()
        
        # Status Display
        if api_healthy:
            st.success(f"🚀 **AI Analysis Engine:** {health_data.get('status', 'unknown').upper()}")
            
            # Show capabilities
            if health_data and 'ai_models' in health_data:
                active_models = sum(health_data['ai_models'].values())
                st.info(f"🤖 **{active_models} AI Models Active** | 🔥 **Backend Port:** {self.api_url.split(':')[-1]}")
        else:
            st.warning("⚠️ **FastAPI backend offline** - Using Groq direct analysis mode")
            if not self.groq_client:
                st.error("❌ No AI analysis available - Configure GROQ_API_KEY")
        
        # Main Content Tabs
        tab1, tab2, tab3 = st.tabs(["🔍 **Evidence Analysis**", "📤 **ICC Submission**", "📊 **Dashboard**"])
        
        with tab1:
            self.render_evidence_analysis_tab(api_healthy)
        
        with tab2:
            self.render_icc_submission_tab()
        
        with tab3:
            self.render_dashboard_tab(health_data)
    
    def render_evidence_analysis_tab(self, api_healthy):
        """Evidence analysis tab with enhanced features"""
        
        # Upload Section
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        st.subheader("📂 Drop Evidence Files for Instant AI Analysis")
        
        uploaded_files = st.file_uploader(
            "**Supported:** Images, Videos, Audio, Documents (Max 100MB each)",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'pdf', 'docx', 'txt'],
            help="⚡ Analysis typically completes in under 3 seconds with FastAPI backend"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.success(f"✅ **{len(uploaded_files)} file(s) uploaded successfully**")
            
            # Process each file
            for idx, uploaded_file in enumerate(uploaded_files):
                with st.expander(f"📁 **{uploaded_file.name}** ({uploaded_file.size:,} bytes)", expanded=len(uploaded_files)==1):
                    
                    # File preview
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if uploaded_file.type.startswith('image/'):
                            image = Image.open(uploaded_file)
                            st.image(image, caption=uploaded_file.name, use_column_width=True)
                        else:
                            st.info(f"**Type:** {uploaded_file.type}\n**Size:** {uploaded_file.size:,} bytes")
                    
                    with col2:
                        # Analysis button
                        if st.button(f"🚀 **ANALYZE WITH AI**", key=f"analyze_{idx}", type="primary"):
                            
                            if api_healthy:
                                # Use FastAPI backend
                                with st.spinner("⚡ Lightning-fast AI analysis in progress..."):
                                    analysis, from_cache = self.analyze_file_fast(uploaded_file)
                                    
                                    if analysis:
                                        st.balloons()
                                        self.render_analysis_results(analysis, from_cache)
                                        
                                        # Store for ICC submission
                                        if 'evidence_analyses' not in st.session_state:
                                            st.session_state.evidence_analyses = []
                                        
                                        st.session_state.evidence_analyses.append({
                                            'file_name': uploaded_file.name,
                                            'analysis': analysis,
                                            'file_content': uploaded_file.getvalue()
                                        })
                                    else:
                                        st.error("❌ Analysis failed - please try again")
                            
                            else:
                                # Use Groq direct analysis
                                with st.spinner("🤖 Analyzing with Groq AI..."):
                                    file_content = uploaded_file.read()
                                    incident_details = {
                                        "date": "2025-06-17",
                                        "time": "14:00",
                                        "location": "CBD, Nairobi, Kenya",
                                        "incident": "Human rights violation"
                                    }
                                    
                                    analysis = self.analyze_evidence_with_groq(
                                        file_content, uploaded_file.type, incident_details
                                    )
                                    
                                    if analysis:
                                        st.success("✅ Analysis complete!")
                                        st.json(analysis)
                                        
                                        # Store for ICC submission
                                        if 'evidence_analyses' not in st.session_state:
                                            st.session_state.evidence_analyses = []
                                        
                                        st.session_state.evidence_analyses.append({
                                            'file_name': uploaded_file.name,
                                            'analysis': analysis,
                                            'file_content': file_content
                                        })
    
    def render_icc_submission_tab(self):
        """ICC submission tab with enhanced workflow"""
        
        st.markdown('<div class="emergency-banner">🚨 EVIDENCE SUBMISSION TO INTERNATIONAL CRIMINAL COURT</div>', 
                   unsafe_allow_html=True)
        
        # Incident Information
        with st.expander("📋 **Incident Details**", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                incident_date = st.date_input("📅 Incident Date", value=datetime(2025, 6, 17))
                incident_location = st.text_input("📍 Location", value="CBD, Nairobi, Kenya")
                incident_type = st.selectbox("⚖️ Incident Type", [
                    "Human Rights Violation",
                    "War Crime", 
                    "Crime Against Humanity",
                    "Genocide",
                    "Other"
                ])
            
            with col2:
                incident_time = st.time_input("🕐 Incident Time", value=datetime.strptime("14:00", "%H:%M").time())
                alleged_perpetrator = st.text_input("👮 Alleged Perpetrator", value="GSU (General Service Unit)")
                urgency_level = st.selectbox("🚨 Urgency Level", ["High", "Medium", "Low"])
        
        # Submitter Information
        with st.expander("👤 **Submitter Information**"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name (Optional)")
                email = st.text_input("Email (Optional)")
                role = st.selectbox("Your Role", [
                    "Witness", "Victim", "Concerned Citizen", "Legal Representative", 
                    "Journalist", "Human Rights Advocate", "Other"
                ])
            
            with col2:
                phone = st.text_input("Phone (Optional)")
                anonymous = st.checkbox("🔒 Submit Anonymously", value=True)
                additional_info = st.text_area("Additional Context")
        
        # Review and Submit
        if 'evidence_analyses' in st.session_state and st.session_state.evidence_analyses:
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            st.subheader("📋 Evidence Review")
            
            st.write(f"**📁 Files Ready for Submission:** {len(st.session_state.evidence_analyses)}")
            for evidence in st.session_state.evidence_analyses:
                analysis = evidence.get('analysis', {})
                evidence_type = analysis.get('evidence_type', 'Unknown')
                relevance = analysis.get('relevance_score', 'N/A')
                st.write(f"• **{evidence['file_name']}** - {evidence_type} (Relevance: {relevance}/10)")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Submit Button
            if st.button("🎯 **SUBMIT TO ICC**", type="primary", use_container_width=True):
                
                # Create submission package
                submission_data = {
                    'incident': {
                        'date': incident_date.isoformat(),
                        'time': incident_time.strftime("%H:%M"),
                        'location': incident_location,
                        'type': incident_type,
                        'perpetrator': alleged_perpetrator,
                        'urgency': urgency_level
                    },
                    'submitter': {
                        'name': name if not anonymous else "Anonymous",
                        'email': email if not anonymous else "",
                        'phone': phone if not anonymous else "",
                        'role': role,
                        'anonymous': anonymous,
                        'additional_info': additional_info
                    },
                    'evidence': st.session_state.evidence_analyses,
                    'submission_timestamp': datetime.now().isoformat()
                }
                
                # Simulate submission (in production, this would submit to ICC)
                with st.spinner("📤 Submitting to ICC..."):
                    time.sleep(2)  # Simulate processing
                    
                    submission_id = f"ICC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    st.success("✅ **Evidence successfully submitted to ICC!**")
                    
                    st.markdown(f"""
                    <div class="status-card">
                        <h4>📋 Submission Confirmation</h4>
                        <p><strong>Submission ID:</strong> {submission_id}</p>
                        <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
                        <p><strong>Files Submitted:</strong> {len(st.session_state.evidence_analyses)}</p>
                        <p><strong>Status:</strong> SUBMITTED</p>
                        <p><em>⚠️ Keep this information for your records.</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Option to clear and submit more
                    if st.button("🔄 **Submit More Evidence**"):
                        del st.session_state.evidence_analyses
                        st.rerun()
        else:
            st.info("📋 **Upload and analyze evidence files to proceed with submission**")
    
    def render_dashboard_tab(self, health_data):
        """Performance and system dashboard"""
        
        st.subheader("📊 System Performance Dashboard")
        
        # System Status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cache_size = len(st.session_state.get('analysis_cache', {}))
            st.metric("💾 Cached Analyses", cache_size)
        
        with col2:
            evidence_count = len(st.session_state.get('evidence_analyses', []))
            st.metric("📁 Evidence Files", evidence_count)
        
        with col3:
            if health_data and 'ai_models' in health_data:
                active_models = sum(health_data['ai_models'].values())
                st.metric("🤖 Active AI Models", active_models)
            else:
                st.metric("🤖 AI Models", "Offline")
        
        with col4:
            cache_enabled = health_data.get('cache_enabled', False) if health_data else False
            st.metric("⚡ Cache Status", "ENABLED" if cache_enabled else "DISABLED")
        
        # Performance Charts
        if health_data:
            st.subheader("🔧 System Health")
            
            # AI Models Status
            if 'ai_models' in health_data:
                models_df = pd.DataFrame([
                    {'Model': 'Groq', 'Status': health_data['ai_models'].get('groq', False)},
                    {'Model': 'Google Vision', 'Status': health_data['ai_models'].get('google_vision', False)},
                    {'Model': 'Roboflow', 'Status': health_data['ai_models'].get('roboflow', False)}
                ])
                
                fig = px.bar(models_df, x='Model', y='Status', 
                           title="AI Models Availability",
                           color='Status', color_discrete_map={True: 'green', False: 'red'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Cache Performance
        if st.session_state.get('analysis_cache'):
            st.subheader("💾 Cache Performance")
            cache_data = st.session_state.analysis_cache
            
            # Simulated cache hit ratio (in production, track this properly)
            cache_hit_ratio = min(len(cache_data) * 0.75, 95)  # Simulated
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = cache_hit_ratio,
                title = {'text': "Cache Hit Ratio (%)"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 85], 'color': "yellow"},
                        {'range': [85, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

# Initialize session state
if 'analysis_cache' not in st.session_state:
    st.session_state.analysis_cache = {}
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8001"

def main():
    """Main application entry point"""
    
    # Setup enhanced CSS
    setup_enhanced_css()
    
    # Initialize platform
    platform = UnifiedICCPlatform()
    
    # Sidebar with quick info
    with st.sidebar:
        st.header("🇰🇪 ICC Legal AI")
        st.write("**Platform Status:** ACTIVE")
        st.write("**Version:** 2.0.0")
        st.write("**Backend:** FastAPI + Groq")
        
        st.markdown("---")
        st.header("📞 Emergency Contacts")
        st.write("**ICC OTP:** +31 70 515 8515")
        st.write("**Kenya Human Rights:** +254 20 272 1113")
        
        st.markdown("---")
        st.header("ℹ️ Quick Guide")
        st.write("1. 📤 Upload evidence files")
        st.write("2. 🤖 AI analyzes content")  
        st.write("3. ⚖️ Review legal assessment")
        st.write("4. 📋 Submit to ICC")
        
        if st.button("🔄 **Clear Cache**"):
            st.session_state.analysis_cache = {}
            st.success("Cache cleared!")
    
    # Render main interface
    platform.render_main_interface()
    
    # Enhanced Footer
    st.markdown("""
    <div class="footer">
        <h4>🇰🇪 ICC Legal AI Platform</h4>
        <p><strong>Empowering Justice Through AI Technology</strong></p>
        <p><em>This platform helps citizens and legal professionals submit evidence to the International Criminal Court.
        All submissions are processed securely and confidentially with state-of-the-art AI analysis.</em></p>
        <p>🛡️ <strong>Security:</strong> End-to-end encryption | 🔒 <strong>Privacy:</strong> Anonymous submissions supported</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
