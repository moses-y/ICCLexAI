#!/bin/bash

# ICCLexAI Quick Deployment Script
# Supports multiple deployment targets

set -e

echo "🏛️ ICCLexAI Deployment Script"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All dependencies are installed."
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cat > .env << 'EOF'
# AI API Keys
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
ROBOFLOW_API_KEY=your_roboflow_api_key_here

# Deployment Tokens
NETLIFY_AUTH_TOKEN=your_netlify_token_here
NETLIFY_SITE_ID=your_netlify_site_id_here
RAILWAY_TOKEN=your_railway_token_here
HF_TOKEN=your_hf_token_here
EOF
        print_warning "Please edit .env file with your actual API keys before deploying."
    fi
    
    print_success "Environment setup complete."
}

# Build frontend
build_frontend() {
    print_status "Building React frontend..."
    
    cd apps/frontend
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    print_status "Building production frontend..."
    npm run build:production
    
    cd ../..
    print_success "Frontend build complete."
}

# Deploy to HuggingFace Spaces
deploy_huggingface() {
    print_status "Deploying to HuggingFace Spaces..."
    
    # Check if HF CLI is installed
    if ! command -v huggingface-cli &> /dev/null; then
        print_status "Installing HuggingFace CLI..."
        pip install huggingface_hub
    fi
    
    # Create deployment directory
    rm -rf hf-deployment
    mkdir -p hf-deployment
    
    # Copy frontend build
    cp -r apps/frontend/dist/* hf-deployment/
    
    # Copy backend
    cp -r apps/backend/* hf-deployment/
    cp requirements.txt hf-deployment/
    
    # Create Gradio app wrapper
    cat > hf-deployment/app.py << 'EOF'
import gradio as gr
import subprocess
import threading
import time
import os

def start_backend():
    subprocess.Popen(["uvicorn", "fast_api_backend:app", "--host", "0.0.0.0", "--port", "7861"])

threading.Thread(target=start_backend, daemon=True).start()
time.sleep(5)

with gr.Blocks(title="ICCLexAI - AI-Powered Legal Case Analysis", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
        <h1 style="margin: 0; font-size: 2.5em;">🏛️ ICCLexAI Platform</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2em;">AI-Powered Evidence Analysis for International Criminal Court Submissions</p>
    </div>
    """)
    
    with gr.Tab("🚀 Quick Start"):
        gr.Markdown("""
        ## Welcome to ICCLexAI
        
        This platform revolutionizes ICC submission processing with AI:
        
        - 📄 **Upload Evidence**: Documents, images, videos, audio files
        - 🤖 **AI Analysis**: Automatic metadata extraction and content analysis  
        - 📊 **Case Generation**: Professional legal case summaries (500-2000 words)
        - ✅ **Human Review**: Review and approve AI-generated content
        - 🏛️ **ICC Ready**: Submissions ready for International Criminal Court
        """)
        
        gr.HTML("""
        <div style="text-align: center; margin: 20px 0;">
            <a href="/static" target="_blank" style="
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 1.1em;
            ">🚀 Launch ICCLexAI Platform</a>
        </div>
        """)
    
    with gr.Tab("📖 Documentation"):
        gr.Markdown("""
        ## How ICCLexAI Works
        
        ### 1. Evidence Upload
        - Support for multiple file formats (PDF, DOCX, JPG, PNG, MP4, MP3, etc.)
        - Secure file handling with encryption
        - Batch upload capabilities
        
        ### 2. AI Processing Pipeline
        - **Document Analysis**: Extract text, metadata, and structure
        - **Image Analysis**: Object detection, facial recognition, scene analysis
        - **Video Processing**: Frame analysis, transcription, timeline extraction
        - **Audio Processing**: Speech-to-text, speaker identification, sentiment analysis
        
        ### 3. Legal Case Generation
        - Comprehensive case summaries with timestamps
        - Evidence correlation and cross-referencing
        - Legal citation formatting
        - Metadata-rich documentation
        
        ### 4. Human-AI Collaboration
        - AI generates professional drafts
        - Legal experts review and refine
        - Version control and approval workflows
        - Export to ICC-compatible formats
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
EOF
    
    # Create Dockerfile
    cat > hf-deployment/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gradio uvicorn

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
EOF
    
    # Create README for HuggingFace
    cat > hf-deployment/README.md << 'EOF'
---
title: ICCLexAI Platform
emoji: 🏛️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
tags:
  - legal-tech
  - ai
  - document-analysis
  - international-law
  - evidence-processing
---

# 🏛️ ICCLexAI - AI-Powered Legal Case Analysis

Revolutionary AI platform that automates ICC (International Criminal Court) submission processing using advanced multimodal AI models.

## 🚀 Features

- **📄 Multimodal Analysis**: Process documents, images, videos, and audio files
- **🤖 AI-Generated Summaries**: Professional 500-2000 word legal case summaries
- **📊 Metadata Extraction**: Automatic extraction of timestamps, locations, and evidence details
- **🎯 Human-AI Collaboration**: AI generates drafts, humans approve and refine
- **⚡ Real-time Processing**: Lightning-fast analysis using Groq LLMs
- **🔒 Secure Processing**: Enterprise-grade security for sensitive legal documents

## 🎯 Use Cases

- **Evidence Processing**: Convert raw evidence into structured legal documents
- **Case Preparation**: Generate comprehensive case summaries with AI assistance
- **Metadata Extraction**: Automatic analysis of timestamps, locations, and key details
- **Document Standardization**: Ensure ICC submission format compliance
- **Efficiency Enhancement**: Reduce manual processing time by 80%

## 🛠️ Technology Stack

- **Frontend**: React + TypeScript + TailwindCSS
- **Backend**: FastAPI + Python
- **AI Models**: Groq (Llama, Mixtral), Google Vision AI, Whisper
- **Processing**: Computer Vision, Speech Recognition, NLP, Document Analysis

## 🔬 AI Capabilities

### Document Analysis
- Text extraction and structure analysis
- Legal citation detection and formatting
- Cross-reference validation
- Metadata extraction (dates, locations, entities)

### Image & Video Processing
- Object and scene detection
- Facial recognition and identification
- Timeline and timestamp extraction
- Evidence correlation analysis

### Audio Processing
- High-accuracy speech-to-text transcription
- Speaker identification and separation
- Sentiment and emotion analysis
- Key phrase and entity extraction

## 🏛️ Legal Institution Benefits

- **Enhanced Accuracy**: AI-assisted analysis reduces human error
- **Faster Processing**: Automated workflows accelerate case preparation
- **Standardized Output**: Consistent formatting and documentation
- **Resource Optimization**: Legal professionals focus on high-value tasks
- **Quality Assurance**: Multi-layer validation and approval processes

## 🌍 Impact

ICCLexAI empowers legal professionals and institutions to:
- Process evidence more efficiently and accurately
- Generate comprehensive, professional case documentation
- Maintain the highest standards required by international legal institutions
- Leverage cutting-edge AI while preserving human oversight and judgment

---

**Note**: This platform is designed to assist legal professionals and does not replace human judgment in legal proceedings. All AI-generated content should be reviewed and approved by qualified legal experts.
EOF
    
    print_success "HuggingFace deployment package created in ./hf-deployment/"
    print_warning "Please upload the hf-deployment folder to your HuggingFace Space manually or use the HuggingFace CLI."
}

# Deploy to Netlify
deploy_netlify() {
    print_status "Preparing Netlify deployment..."
    
    # Check if Netlify CLI is installed
    if ! command -v netlify &> /dev/null; then
        print_status "Installing Netlify CLI..."
        npm install -g netlify-cli
    fi
    
    cd apps/frontend
    
    # Build for production
    npm run build:production
    
    print_success "Frontend built for Netlify."
    print_warning "To deploy to Netlify:"
    print_warning "1. Run: netlify deploy --dir=dist --prod"
    print_warning "2. Or connect your GitHub repo to Netlify dashboard"
    
    cd ../..
}

# Main deployment menu
main_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) 🤗 HuggingFace Spaces (AI-optimized, free GPU)"
    echo "2) 🌐 Netlify (Frontend only, fast CDN)"
    echo "3) 📦 Build All (prepare for manual deployment)"
    echo "4) ❓ Help & Documentation"
    echo "5) 🚪 Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            deploy_huggingface
            ;;
        2)
            deploy_netlify
            ;;
        3)
            build_frontend
            print_success "All builds complete. Check apps/frontend/dist for deployable files."
            ;;
        4)
            echo ""
            echo "📖 Documentation:"
            echo "- Full deployment guide: ./DEPLOYMENT_STRATEGY.md"
            echo "- Frontend guide: ./apps/frontend/DEPLOYMENT.md"
            echo "- Backend API docs: http://localhost:8000/docs (when running locally)"
            echo ""
            echo "🔗 Useful Links:"
            echo "- HuggingFace Spaces: https://huggingface.co/spaces"
            echo "- Netlify Dashboard: https://app.netlify.com"
            echo "- Railway Dashboard: https://railway.app"
            echo ""
            main_menu
            ;;
        5)
            print_success "Goodbye! 👋"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please choose 1-5."
            main_menu
            ;;
    esac
}

# Script execution
echo ""
check_dependencies
setup_environment
main_menu

print_success "Deployment script completed! 🎉"
