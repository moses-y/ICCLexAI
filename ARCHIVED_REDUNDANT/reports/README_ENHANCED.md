# 🇰🇪 Enhanced ICC Evidence Analysis System

## Comprehensive AI-Powered Forensic Case Building for International Criminal Court Submissions

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/your-repo/ICC-Evidence-Analysis)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Production%20Ready-success.svg)]()

### 🎯 **System Overview**

The Enhanced ICC Evidence Analysis System is a comprehensive AI-powered platform that supports **ALL file types accepted by the International Criminal Court** and provides **human-in-the-loop validation** for witness submissions.

---

## 🚀 **Key Features**

### 📁 **Complete ICC File Type Support**
- **Documents**: PDF, DOC/DOCX, TXT, RTF, ODT
- **Images**: JPG/JPEG, PNG, GIF, BMP, TIFF, WEBP, HEIC, RAW
- **Videos**: MP4, AVI, MOV, MKV, WMV, WEBM, M4V, 3GP
- **Audio**: MP3, WAV, M4A, FLAC, OGG, AAC, WMA, AMR
- **Digital Evidence**: XML, JSON, CSV, XLSX, HTML, MHTML
- **Archives**: ZIP, RAR, 7Z, TAR, GZ
- **Forensic Evidence**: DD, E01, AFF, VMDK

### 🤖 **Multi-Agent AI Analysis**
- **Transcription Agent**: Audio/video transcription with speaker identification
- **Visual Analysis Agent**: Scene analysis, object detection, face recognition
- **Document Intelligence Agent**: Entity extraction, legal analysis
- **Context Engine**: Cross-referencing and case correlation

### 👤 **Human-in-the-Loop Validation**
- **Interactive Review Interface**: Edit AI-generated summaries
- **Evidence Validation**: Rate accuracy and legal relevance
- **Case Summary Editing**: Modify incident descriptions and legal analysis
- **Final Approval Workflow**: Comprehensive validation checklist

### 🛡️ **Witness Protection & Safety**
- **Identity Protection**: Anonymous submission options
- **Consent Management**: Explicit consent tracking
- **Security Features**: Secure file handling and chain of custody
- **Protection Levels**: Standard, high security, relocation options

---

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Upload   │ -> │  AI Agent        │ -> │  Human          │
│   (All ICC      │    │  Pipeline        │    │  Validation     │
│   File Types)   │    │  Analysis        │    │  Interface      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ICC Document  │ <- │  Case Summary    │ <- │  Evidence       │
│   Generation    │    │  Generation      │    │  Correlation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- Required API Keys (Groq, Google Vision, etc.)
- 4GB+ RAM (recommended for video/forensic analysis)

### **Quick Start**

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-repo/ICC-Evidence-Analysis.git
   cd ICC-Evidence-Analysis
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Launch System**
   ```bash
   python launch_enhanced_icc_system.py
   ```

### **Manual Setup**

1. **Backend (FastAPI)**
   ```bash
   cd apps/backend
   uvicorn enhanced_icc_api:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Validation Interface (Streamlit)**
   ```bash
   cd apps/validation
   streamlit run icc_validation_interface.py --server.port 8502
   ```

3. **Access System**
   - **API Backend**: http://localhost:8001
   - **API Docs**: http://localhost:8001/docs
   - **Validation Interface**: http://localhost:8502

---

## 🎯 **Usage Workflow**

### **Step 1: Upload Evidence**
- Upload files through the validation interface
- Automatic ICC compliance validation
- Support for single files or batch uploads
- Real-time file type and size verification

### **Step 2: AI Analysis**
- Multi-agent AI processing pipeline
- Category-specific analysis (documents, images, videos, etc.)
- Metadata extraction and forensic analysis
- Cross-referencing and correlation

### **Step 3: Human Validation**
- Review AI-generated analysis
- Edit case summaries and legal significance
- Validate evidence accuracy and relevance
- Add additional context and notes

### **Step 4: Final Submission**
- Complete validation checklist
- Configure witness protection options
- Generate professional ICC submission document
- Submit to ICC through multiple channels

---

## 📊 **API Endpoints**

### **Core Endpoints**
- `GET /` - System information
- `GET /health` - Health check
- `GET /supported-file-types` - ICC file type matrix

### **File Processing**
- `POST /validate-file` - Validate single file
- `POST /analyze-evidence` - Analyze single evidence file
- `POST /analyze-batch` - Batch evidence analysis

### **Case Management**
- `GET /case-summary/{session_id}` - Retrieve case summary
- `POST /update-case-summary/{session_id}` - Update with human edits
- `POST /generate-icc-document/{session_id}` - Generate ICC document

### **Submission**
- `POST /submit-to-icc/{session_id}` - Final ICC submission

---

## 🧪 **Testing**

### **Automated Test Suite**
```bash
python test_icc_system.py
```

**Test Coverage:**
- ✅ File type validation (all ICC formats)
- ✅ API endpoint functionality
- ✅ Multi-agent analysis pipeline
- ✅ Human validation workflow
- ✅ Case document generation
- ✅ Final submission process

### **Manual Testing**
1. Upload sample evidence files
2. Review AI analysis results
3. Edit case summaries
4. Complete validation workflow
5. Generate ICC submission document

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

# Optional
HUGGINGFACE_TOKEN=your_huggingface_token
ROBOFLOW_API_KEY=your_roboflow_api_key

# System Configuration
MAX_FILE_SIZE_MB=5000
BATCH_SIZE_LIMIT=50
```

### **File Type Configuration**
File type support and size limits can be configured in:
- `libs/icc-automation/icc_file_types.py`

### **AI Model Configuration**
AI analysis models can be configured in:
- `libs/icc-automation/icc_orchestrator.py`

---

## 🛡️ **Security & Privacy**

### **Data Protection**
- **Encryption**: All file transfers encrypted
- **Temporary Storage**: Files processed in memory when possible
- **Access Control**: API key based authentication
- **Audit Trail**: Complete processing history

### **Witness Protection**
- **Anonymous Submissions**: No personal data required
- **Identity Protection**: Witness details kept separate
- **Secure Communication**: Encrypted submission channels
- **Consent Tracking**: Explicit consent management

### **Compliance**
- **ICC Standards**: Full compliance with ICC submission requirements
- **Chain of Custody**: Complete evidence tracking
- **Forensic Integrity**: Hash verification and timestamps
- **Legal Standards**: Professional evidence handling

---

## 📚 **Documentation**

### **User Guides**
- [Witness Submission Guide](docs/witness-guide.md)
- [Legal Professional Guide](docs/legal-guide.md)
- [System Administrator Guide](docs/admin-guide.md)

### **Technical Documentation**
- [API Reference](docs/api-reference.md)
- [Agent Architecture](docs/agent-architecture.md)
- [Deployment Guide](docs/deployment.md)

### **Development**
- [Contributing Guidelines](CONTRIBUTING.md)
- [Development Setup](docs/development.md)
- [Testing Guidelines](docs/testing.md)

---

## 🤝 **Contributing**

We welcome contributions to improve the ICC Evidence Analysis System:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/enhancement`)
3. **Commit changes** (`git commit -m 'Add enhancement'`)
4. **Push to branch** (`git push origin feature/enhancement`)
5. **Create Pull Request**

### **Areas for Contribution**
- Additional AI analysis agents
- New file type support
- Enhanced security features
- User interface improvements
- Documentation and translations

---

## 📞 **Support & Contact**

### **Technical Support**
- **Issues**: [GitHub Issues](https://github.com/your-repo/ICC-Evidence-Analysis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/ICC-Evidence-Analysis/discussions)
- **Email**: support@icc-evidence-analysis.org

### **ICC Resources**
- **ICC Official Website**: https://www.icc-cpi.int/
- **ICC Submission Guidelines**: https://www.icc-cpi.int/about/how-court-works/proceedings
- **ICC Office of the Prosecutor**: otp.informationdesk@icc-cpi.int

### **Human Rights Organizations**
- **Kenya Human Rights Commission**: +254 20 272 1113
- **International Bar Association**: https://www.ibanet.org/
- **Amnesty International**: https://www.amnesty.org/

---

## ⚖️ **Legal Disclaimer**

This system is designed to assist in preparing evidence for ICC submission but does not guarantee acceptance by the ICC. Users are responsible for:

- **Evidence Accuracy**: Ensuring all submitted evidence is accurate and authentic
- **Legal Compliance**: Following all applicable laws and ICC procedures
- **Witness Safety**: Taking appropriate measures to protect witness safety
- **Professional Review**: Having submissions reviewed by qualified legal professionals

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 **Acknowledgments**

- **International Criminal Court** for establishing justice standards
- **Human Rights Organizations** for their dedication to justice
- **AI Research Community** for advancing analysis capabilities
- **Witness Protection Organizations** for safety guidance
- **Open Source Community** for tools and frameworks

---

## 📈 **Roadmap**

### **Version 2.2 (Coming Soon)**
- [ ] Advanced forensic analysis agents
- [ ] Multi-language support
- [ ] Enhanced witness protection features
- [ ] Mobile app for field evidence collection

### **Version 2.3 (Planned)**
- [ ] Blockchain evidence verification
- [ ] Advanced timeline reconstruction
- [ ] Integration with legal case management systems
- [ ] Real-time collaboration features

### **Long Term Goals**
- [ ] Global witness protection network integration
- [ ] Automated ICC form submission
- [ ] AI-powered legal precedent analysis
- [ ] International court system integration

---

*For the latest updates and announcements, follow our [GitHub repository](https://github.com/your-repo/ICC-Evidence-Analysis) and [project blog](https://icc-evidence-analysis.org/blog).*
