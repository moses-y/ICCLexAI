"""
LIGHTNING-FAST AI-ICC Evidence Analysis App
Real-time multimodal AI analysis using FastAPI + Streamlit
Optimized for speed with caching and parallel processing
Testing auto-reload functionality
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import io
import os

# Page configuration for speed
st.set_page_config(
    page_title="⚡ Fast AI-ICC Evidence Analyzer",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "Real-time AI evidence analysis for ICC submissions"
    }
)

# Custom CSS for ultra-fast UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #000000 20%, #FFFFFF 20% 22%, #FF0000 22% 78%, #FFFFFF 78% 80%, #008000 80%);
        padding: 10px;
        text-align: center;
        color: #000000;
        font-weight: bold;
        font-size: 1.8rem;
        margin: 5px 0;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        border-radius: 8px;
    }
    
    .analysis-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #008000;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .speed-indicator {
        background: #00ff00;
        color: black;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }
    
    .upload-zone {
        border: 3px dashed #008000;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background: rgba(0, 128, 0, 0.05);
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        background: rgba(0, 128, 0, 0.1);
        border-color: #006600;
    }
    
    .metric-card {
        background: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 5px 0;
    }
    
    .ai-insight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .legal-assessment {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for caching
if 'analysis_cache' not in st.session_state:
    st.session_state.analysis_cache = {}
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"

class FastAnalysisUI:
    def __init__(self):
        self.api_url = st.session_state.api_base_url
    
    def check_api_health(self):
        """Check if FastAPI backend is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            return response.status_code == 200, response.json()
        except:
            return False, None
    
    def analyze_file_fast(self, uploaded_file):
        """Send file to FastAPI backend for lightning-fast analysis"""
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
                
        except requests.exceptions.Timeout:
            st.error("⏰ Analysis timeout - file too large or server overloaded")
            return None, False
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None, False
    
    def render_analysis_results(self, analysis, from_cache=False):
        """Render beautiful analysis results with visualizations"""
        
        # Header with performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cache_status = "🔥 FROM CACHE" if from_cache else "⚡ REAL-TIME"
            st.markdown(f'<div class="speed-indicator">{cache_status}</div>', unsafe_allow_html=True)
        
        with col2:
            analysis_time = analysis.get('analysis_time', 0)
            st.metric("Analysis Time", f"{analysis_time:.2f}s")
        
        with col3:
            file_size_mb = analysis['file_size'] / (1024 * 1024)
            st.metric("File Size", f"{file_size_mb:.2f} MB")
        
        with col4:
            confidence = analysis.get('content_analysis', {}).get('analysis_confidence', 'unknown')
            st.metric("AI Confidence", confidence.upper())
        
        # Main analysis sections
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Content Analysis
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.subheader("🔍 AI Content Analysis")
            
            content_analysis = analysis.get('content_analysis', {})
            
            if 'labels' in content_analysis and content_analysis['labels']:
                st.write("**Detected Content:**")
                labels_df = pd.DataFrame({
                    'Content': content_analysis['labels'][:10],
                    'Relevance': [1.0 - i*0.1 for i in range(len(content_analysis['labels'][:10]))]
                })
                
                fig = px.bar(labels_df, x='Relevance', y='Content', orientation='h',
                           title="AI-Detected Content Elements",
                           color='Relevance', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            
            if 'text_content' in content_analysis and content_analysis['text_content']:
                st.write("**Extracted Text:**")
                st.text_area("", content_analysis['text_content'], height=100)
            
            if 'faces_detected' in content_analysis:
                st.write(f"**Faces Detected:** {content_analysis['faces_detected']}")
            
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
                                       title="Detected Objects with Confidence")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No specific objects detected in this evidence")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            # Metadata Information
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.subheader("📊 Evidence Metadata")
            
            metadata = analysis.get('metadata', {})
            
            if 'gps_coordinates' in metadata:
                gps = metadata['gps_coordinates']
                st.write(f"**📍 Location:** {gps['latitude']:.6f}, {gps['longitude']:.6f}")
                
                if 'location_name' in metadata:
                    st.write(f"**🏠 Address:** {metadata['location_name']}")
                
                # Map visualization
                map_df = pd.DataFrame([gps])
                fig = px.scatter_mapbox(map_df, lat='latitude', lon='longitude',
                                      zoom=15, height=300,
                                      mapbox_style="open-street-map",
                                      title="Evidence Location")
                st.plotly_chart(fig, use_container_width=True)
            
            if 'timestamp' in metadata:
                st.write(f"**📅 Timestamp:** {metadata['timestamp']}")
            
            if 'camera_make' in metadata:
                st.write(f"**📱 Device:** {metadata['camera_make']} {metadata.get('camera_model', '')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Legal Assessment
        legal_assessment = analysis.get('legal_assessment', {})
        if legal_assessment:
            st.markdown('<div class="legal-assessment">', unsafe_allow_html=True)
            st.subheader("⚖️ AI Legal Assessment (DeepSeek R1)")
            
            if 'legal_summary' in legal_assessment:
                st.write(legal_assessment['legal_summary'])
            
            col1, col2 = st.columns(2)
            with col1:
                evidence_quality = legal_assessment.get('evidence_quality', 'unknown')
                st.metric("Evidence Quality", evidence_quality.upper())
            
            with col2:
                icc_relevance = legal_assessment.get('icc_relevance', 'unknown')
                st.metric("ICC Relevance", icc_relevance.upper())
            
            if 'recommendations' in legal_assessment:
                st.write("**AI Recommendations:**")
                for rec in legal_assessment['recommendations']:
                    st.write(f"• {rec}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_main_interface(self):
        """Main application interface"""
        
        # Header
        st.markdown('<div class="main-header">⚡ LIGHTNING-FAST AI-ICC Evidence Analyzer 🇰🇪</div>', 
                   unsafe_allow_html=True)
        
        # API Status Check
        api_healthy, health_data = self.check_api_health()
        
        if not api_healthy:
            st.error("🚨 FastAPI backend not running! Start it with: `python fast_api_backend.py`")
            st.info("💡 The backend provides lightning-fast AI analysis using Groq, Google Vision, and Roboflow")
            st.stop()
        
        # Show API capabilities
        if health_data:
            st.success(f"🚀 AI Analysis Engine: {health_data.get('status', 'unknown').upper()}")
            
            capabilities = health_data.get('capabilities', [])
            if capabilities:
                with st.expander("🤖 AI Capabilities Available"):
                    for cap in capabilities:
                        st.write(f"✅ {cap}")
        
        # File Upload Section
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        st.subheader("📂 Drop Evidence File for Instant AI Analysis")
        
        uploaded_file = st.file_uploader(
            "Supported: Images, Videos, Audio, Documents",
            type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'pdf', 'docx', 'txt'],
            help="Max 100MB - Analysis typically completes in under 3 seconds"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Show file preview if it's an image
            if uploaded_file.type.startswith('image/'):
                col1, col2 = st.columns([1, 2])
                with col1:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, use_column_width=True)
                with col2:
                    st.info(f"**File:** {uploaded_file.name}\n**Size:** {uploaded_file.size:,} bytes\n**Type:** {uploaded_file.type}")
            else:
                st.info(f"**File:** {uploaded_file.name} | **Size:** {uploaded_file.size:,} bytes | **Type:** {uploaded_file.type}")
            
            # Real-time analysis button
            if st.button("🚀 ANALYZE WITH AI", type="primary", use_container_width=True):
                with st.spinner("⚡ Lightning-fast AI analysis in progress..."):
                    analysis, from_cache = self.analyze_file_fast(uploaded_file)
                    
                    if analysis:
                        st.balloons()
                        self.render_analysis_results(analysis, from_cache)
                    else:
                        st.error("❌ Analysis failed - please try again")
        
        # Performance Dashboard
        with st.expander("📊 Performance Dashboard"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Cached Analyses", len(st.session_state.analysis_cache))
            
            with col2:
                if health_data and 'ai_models' in health_data:
                    active_models = sum(health_data['ai_models'].values())
                    st.metric("Active AI Models", active_models)
            
            with col3:
                cache_enabled = health_data.get('cache_enabled', False) if health_data else False
                st.metric("Cache Status", "ENABLED" if cache_enabled else "DISABLED")

# Run the application
def main():
    app = FastAnalysisUI()
    app.render_main_interface()

if __name__ == "__main__":
    main()
