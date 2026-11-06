# 🇰🇪 ICC Evidence Analysis System - Comprehensive Integration

A complete **Human-in-the-Loop** system for International Criminal Court (ICC) evidence analysis, validation, and submission. This system integrates AI-powered evidence analysis with human validation workflows for building strong ICC cases.

## 🌟 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    🇰🇪 ICC SYSTEM ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   React Frontend │◄──►│ Context Engine  │◄──►│ AI Agents    │ │
│  │  (Port 5173)    │    │ API (Port 8002) │    │ & Analysis   │ │
│  │                 │    │                 │    │              │ │
│  │ • File Upload   │    │ • Session Mgmt  │    │ • Visual AI  │ │
│  │ • Validation UI │    │ • Evidence Pool │    │ • Audio AI   │ │
│  │ • Summary Edit  │    │ • Human Review  │    │ • Document   │ │
│  │ • ICC Document  │    │ • State Persist │    │ • OCR & NLP  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ⚡ Quick Start Guide

### 1. Launch the Complete System

Run the orchestrated launcher to start all services:

```bash
python launch_icc_system.py
```

This automatically starts:
- **ICC Context Engine API** (Port 8002) - Core state management
- **React Frontend** (Port 5173) - Human validation interface

### 2. Access the Validation Dashboard

Open your browser to: **http://localhost:5173**

## 🔄 Complete Workflow

### Phase 1: Case Initialization
1. **Open Dashboard**: Navigate to http://localhost:5173
2. **Initialize Case**: Click "Initialize New ICC Case"
3. **Case Created**: System generates ICC file number and session

### Phase 2: Evidence Collection & Analysis
1. **Upload Files**: Drag & drop or select evidence files
   - Images, videos, audio, documents, digital files
   - Real-time AI analysis begins automatically
2. **Multi-Agent Analysis**: AI agents process evidence
   - Visual analysis for images/videos
   - Transcription for audio files
   - Document intelligence for text
   - Metadata extraction and cross-referencing

### Phase 3: Human Validation & Review
1. **Review Evidence**: Navigate to "Evidence" tab
   - Validate or reject each evidence item
   - Review AI analysis results
   - Add human annotations
2. **Edit Case Summary**: Navigate to "Validation" tab
   - Review AI-generated case summary
   - Edit and refine content
   - Add legal assessments
   - Update key findings and recommendations

### Phase 4: Final Document Generation
1. **Complete Validation**: Ensure 80%+ validation progress
2. **Generate ICC Document**: Navigate to "Document" tab
3. **Final Submission**: Professional ICC submission document generated

## 🔗 API Integration

The system provides comprehensive REST APIs for programmatic access:

### Session Management
```bash
# Create new case session
POST http://localhost:8002/api/session/create
Content-Type: application/json
{
  "date": "2025-06-22",
  "time": "14:00:00",
  "location": "Nairobi, Kenya",
  "description": "Human rights violation",
  "urgency_level": "High"
}

# Get session state
GET http://localhost:8002/api/session/{session_id}/state

# Get validation progress
GET http://localhost:8002/api/session/{session_id}/validation
```

### Evidence Management
```bash
# Upload evidence files
POST http://localhost:8002/api/session/{session_id}/evidence/upload
Content-Type: multipart/form-data
files: [file1, file2, ...]

# Get evidence pool
GET http://localhost:8002/api/session/{session_id}/evidence

# Validate evidence item
POST http://localhost:8002/api/session/{session_id}/evidence/validate
{
  "evidence_id": "EVD-...",
  "status": "validated",
  "validator_id": "human_validator"
}
```

### Human Validation
```bash
# Update validation state
POST http://localhost:8002/api/session/{session_id}/validation/update
{
  "field": "human_reviewed",
  "value": true,
  "reviewer_id": "validator123"
}

# Update case summary
POST http://localhost:8002/api/session/{session_id}/summary/update
{
  "human_edited_summary": "Updated case summary...",
  "legal_assessment": "Strong evidence of violations...",
  "editor_id": "editor123"
}
```

### Document Generation
```bash
# Generate AI summary
GET http://localhost:8002/api/session/{session_id}/summary/generate

# Generate final ICC document
POST http://localhost:8002/api/session/{session_id}/document/generate
```

## 🎯 Key Features

### Human-in-the-Loop Validation
- **Interactive Review**: Edit AI-generated summaries and analyses
- **Evidence Validation**: Approve/reject individual evidence items
- **Progress Tracking**: Real-time validation progress monitoring
- **Legal Assessment**: Human expert review and confirmation

### AI-Powered Analysis
- **Multi-Modal Processing**: Images, videos, audio, documents
- **Cross-Evidence Correlation**: Automatic relationship detection
- **Metadata Extraction**: Comprehensive technical analysis
- **Quality Scoring**: Evidence relevance and quality assessment

### Professional ICC Integration
- **Systematic File Numbering**: ICC-compliant case numbering
- **Document Generation**: Professional submission formats
- **Chain of Custody**: Evidence tracking and validation
- **Legal Compliance**: ICC procedure adherence

### Session Management
- **State Persistence**: Complete session state tracking
- **Multi-Session Support**: Handle multiple cases simultaneously
- **Real-time Updates**: Live synchronization across components
- **Error Recovery**: Robust error handling and recovery

## 🔧 Technical Architecture

### Context Engine (`icc_context_engine.py`)
- **Session Management**: Unique session tracking and state
- **Evidence Pool**: Centralized evidence storage and management
- **Validation State**: Human review progress tracking
- **Case Metadata**: ICC-compliant case information structure
- **Cross-References**: Evidence correlation and relationship mapping

### API Layer (`icc_context_api.py`)
- **RESTful Endpoints**: Complete CRUD operations
- **Background Processing**: Asynchronous evidence analysis
- **Session Isolation**: Secure multi-tenant architecture
- **Health Monitoring**: Service health and status tracking

### Frontend (`ICCValidationDashboard.tsx`)
- **Modern React UI**: Responsive, accessible interface
- **Real-time Updates**: Live data synchronization
- **Interactive Editing**: In-place content editing
- **Progress Visualization**: Clear validation progress indicators
- **Mobile Responsive**: Works on all device sizes

## 📊 Validation Workflow

The system implements a comprehensive validation checklist:

1. **Human Reviewed** ✅ - Human has reviewed case content
2. **Summary Edited** ✅ - AI summary refined by human
3. **Evidence Validated** ✅ - All evidence items reviewed
4. **Legal Analysis Confirmed** ✅ - Legal assessment verified
5. **Witness Consent** ✅ - Consent and protection confirmed
6. **Chain of Custody** ✅ - Evidence integrity verified

**Validation Progress**: `(completed_items / total_items) * 100%`

## 🌐 Deployment Options

### Development Mode
```bash
# Start all services
python launch_icc_system.py

# Or manually start individual services
python apps/backend/icc_context_api.py    # Port 8002
cd apps/frontend && npm run dev           # Port 5173
```

### Production Mode
```bash
# Build frontend
cd apps/frontend && npm run build

# Deploy with production server
# Configure reverse proxy (nginx/apache)
# Set environment variables for production
```

### Docker Deployment
```bash
# Build and start with Docker Compose
docker-compose up --build

# Access via configured ports
```

## 🔐 Security Considerations

- **Data Encryption**: All sensitive data encrypted in transit and at rest
- **Access Control**: Role-based access control for different user types
- **Audit Logging**: Complete audit trail of all actions
- **Secure Communication**: HTTPS/TLS for all API communications
- **Evidence Integrity**: Cryptographic hashing for evidence verification

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8002
   # Kill the process if needed
   taskkill /PID <process_id> /F
   ```

2. **Context Engine Import Errors**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   cd apps/frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

### Health Checks
```bash
# Check Context Engine
curl http://localhost:8002/api/health

# Check Frontend
curl http://localhost:5173

# List active sessions
curl http://localhost:8002/api/sessions
```

## 📚 Documentation

- **API Documentation**: Available at http://localhost:8002/docs (when running)
- **Frontend Components**: React component documentation in `/apps/frontend/src/components/`
- **Context Engine**: Detailed documentation in `/libs/icc-automation/`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Review documentation and troubleshooting guides

---

**🇰🇪 Built for International Justice | Powered by AI | Validated by Humans**
