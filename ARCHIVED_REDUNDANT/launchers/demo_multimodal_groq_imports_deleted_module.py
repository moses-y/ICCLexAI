"""
🚀 ICCLexAI MULTIMODAL GROQ OPTIMIZATION DEMONSTRATION
Complete showcase of all Groq models optimized for ICC evidence analysis

This demonstrates how the Evidence Analysis Agent now uses ALL 17+ Groq models
strategically for maximum efficiency on your free account.
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libs.icc_automation.evidence_analysis_agent import EvidenceAnalysisAgent
# Note: Import the EvidenceAnalysisAgent when running this demo

def main():
    st.set_page_config(
        page_title="🚀 ICCLexAI Multimodal Groq Demo",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🚀 ICCLexAI: Complete Multimodal Groq Optimization")
    st.markdown("**Demonstrating ALL 17+ Groq models optimized for ICC evidence analysis**")
    
    # Initialize the optimized evidence analysis agent
    agent = EvidenceAnalysisAgent(cache_enabled=True)
    
    # Display the comprehensive dashboard
    agent.display_model_usage_dashboard()
    
    st.markdown("---")
    
    # Evidence type demonstration
    st.subheader("🧪 Test Evidence Analysis with Optimal Model Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        evidence_type = st.selectbox(
            "Select Evidence Type",
            ['photograph', 'video', 'audio', 'document', 'witness_statement', 'digital_evidence']
        )
        
        file_size = st.slider("File Size (MB)", 0.1, 50.0, 5.0)
        complexity = st.selectbox("Complexity Level", ['standard', 'high_priority', 'experimental', 'fast'])
    
    with col2:
        if st.button("🧠 Get Optimal Model Recommendation"):
            recommendation = agent.get_smart_model_recommendation(evidence_type, file_size)
            
            st.success("**Recommended Strategy:**")
            
            primary = recommendation['primary']
            st.code(f"""
MODEL: {primary['model']}
TOKENS: {primary['max_tokens']}
TEMPERATURE: {primary['temperature']}
USE CASE: {primary['use_case']}
            """)
            
            st.write("**AI Reasoning:**")
            for reason in recommendation['reasoning']:
                st.write(f"• {reason}")
    
    # Real file upload test
    st.markdown("---")
    st.subheader("📁 Upload Real Evidence for Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload evidence file",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mp3', 'wav', 'pdf', 'docx', 'txt']
    )
    
    if uploaded_file:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {len(uploaded_file.getvalue()) / 1024 / 1024:.2f} MB")
            st.write(f"**Type:** {uploaded_file.type}")
        
        with col_b:
            if st.button("🔍 Analyze with Optimal Model"):
                with st.spinner("🚀 Running multimodal analysis..."):
                    analysis, from_cache = agent.analyze_evidence_comprehensive(uploaded_file)
                    
                    if analysis:
                        if from_cache:
                            st.success("⚡ Analysis retrieved from cache!")
                        else:
                            st.success("🤖 Fresh AI analysis complete!")
                        
                        # Display key results
                        st.json(analysis)
                    else:
                        st.error("❌ Analysis failed")
    
    # Show all available models
    st.markdown("---")
    st.subheader("🎯 Your Complete Groq Model Arsenal")
    
    models_info = {
        "🏆 Premium Models (Limited Daily Use)": [
            "llama-3.3-70b-versatile (30 RPM, 1,000 RPD, 12,000 TPM)",
            "deepseek-r1-distill-llama-70b (30 RPM, 1,000 RPD, 6,000 TPM)",
            "qwen-qwq-32b (30 RPM, 1,000 RPD, 6,000 TPM)",
            "meta-llama/llama-4-scout-17b-16e-instruct (30 RPM, 1,000 RPD, 30,000 TPM)",
            "mistral-saba-24b (30 RPM, 1,000 RPD, 6,000 TPM)"
        ],
        "⚡ High-Volume Models (14,400 RPD)": [
            "gemma2-9b-it (30 RPM, 14,400 RPD, 15,000 TPM)",
            "llama-3.1-8b-instant (30 RPM, 14,400 RPD, 6,000 TPM)",
            "llama3-70b-8192 (30 RPM, 14,400 RPD, 6,000 TPM)",
            "llama3-8b-8192 (30 RPM, 14,400 RPD, 6,000 TPM)",
            "meta-llama/llama-guard-4-12b (30 RPM, 14,400 RPD, 15,000 TPM)"
        ],
        "🎵 Audio Processing Models": [
            "whisper-large-v3-turbo (20 RPM, 2,000 RPD, 7,200 sec/hour)",
            "whisper-large-v3 (20 RPM, 2,000 RPD, 7,200 sec/hour)",
            "distil-whisper-large-v3-en (20 RPM, 2,000 RPD, 7,200 sec/hour)"
        ],
        "🧪 Experimental & Specialized": [
            "compound-beta (15 RPM, 200 RPD, 70,000 TPM!)",
            "qwen/qwen3-32b (60 RPM, 1,000 RPD, 6,000 TPM)",
            "allam-2-7b (30 RPM, 7,000 RPD, 6,000 TPM)",
            "playai-tts (10 RPM, 100 RPD) - Text-to-Speech"
        ]
    }
    
    for category, models in models_info.items():
        with st.expander(category):
            for model in models:
                st.write(f"• {model}")
    
    st.markdown("---")
    st.success("🎊 **Your ICCLexAI platform now uses ALL available Groq models strategically for maximum multimodal evidence analysis capability!**")

if __name__ == "__main__":
    main()
