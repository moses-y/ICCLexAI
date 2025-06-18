# 🏛️ ICCLexAI: AI-Powered Evidence Analysis Platform

<div align="center">

![ICCLexAI Banner](https://img.shields.io/badge/ICCLexAI-Production%20Ready-brightgreen?style=for-the-badge)
![React](https://img.shields.io/badge/React-TypeScript-blue?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-green?style=for-the-badge&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-AI%20Optimized-orange?style=for-the-badge)

**🌍 Empowering ICC Legal Professionals with Advanced AI Technology**

*Production-ready platform for evidence analysis, document processing, and legal workflow automation*

[📖 Documentation](docs/) | [🔧 Deploy Now](#-quick-deployment) | [🚀 Live Demo](https://huggingface.co/spaces/moses-y/icclexai)

</div>

---

## 🎯 **Mission Statement**

ICCLexAI transforms how International Criminal Court investigators and legal professionals analyze evidence, process documents, and conduct legal research. Built with cutting-edge AI technology and optimized for real-world deployment.

**Empowering justice through intelligent automation.**

## ✨ **Key Features**

### 🤖 **Advanced AI Integration**
- **Multi-modal Evidence Analysis** - Images, documents, audio, video processing
- **Groq AI Optimization** - Smart model selection for free tier efficiency  
- **Real-time Processing** - Instant analysis and feedback
- **Contextual Understanding** - Legal domain-specific intelligence

### 📱 **Professional Interface**
- **Mobile-Responsive Design** - Field evidence collection on any device
- **Kenya ICC Branding** - Professional legal interface
- **Intuitive Workflows** - Multi-step guided processes
- **Real-time Chat** - AI-powered legal assistance

### 🔧 **Enterprise Architecture**
- **5 Specialized Agents** - Modular, maintainable design
- **RESTful API** - FastAPI backend with comprehensive endpoints
- **Docker Ready** - Production deployment configurations
- **Security First** - Privacy-focused, no persistent sensitive data storage

### 📊 **Performance Optimized**
- **65KB Bundle** - Lightning-fast load times
- **Mobile Optimized** - 95+ performance scores
- **Scalable Architecture** - Handle large document processing
- **Cost Efficient** - Optimized for free-tier AI services

---

## 🚀 **Core Agents**

| Agent | Purpose | Technology | Status |
|-------|---------|------------|--------|
| **🎭 Master Orchestrator** | Multi-step workflows & AI chat | Streamlit + Groq | ✅ Production |
| **📄 Metadata Extraction** | Document analysis & OCR | PyPDF2 + Groq | ✅ Production |
| **🌐 Selenium Automation** | Web scraping & form automation | Selenium + Chrome | ✅ Production |
| **🔗 FastAPI Integration** | RESTful API services | FastAPI + Uvicorn | ✅ Production |
| **🔍 Evidence Analysis** | Multimodal AI analysis | Groq Vision Models | ✅ Production |

---

## 🚀 **Quick Deployment**

### **Option 1: HuggingFace Spaces (Recommended - FREE)**

```bash
# 1. Create new Space at https://huggingface.co/spaces
# 2. Upload files from apps/frontend/dist/
# 3. Set to "Static" application type
# ✅ Live in 5 minutes!
```

### **Option 2: Vercel (Premium Performance)**

```bash
cd apps/frontend
npx vercel --prod
# ✅ Live in 30 seconds
```

### **Option 3: Local Development**

```bash
# Backend
pip install -r requirements.txt
python apps/backend/fast_api_backend.py

# Frontend  
cd apps/frontend
npm install
npm run dev

# ✅ Access at http://localhost:3000
```

---

## 📋 **Quick Start Guide**

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- Groq API key (free tier available)

### **Installation**

1. **Clone Repository**
   ```bash
   git clone https://github.com/moses-y/ICCLexAI.git
   cd ICCLexAI
   ```

2. **Setup Environment**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   # Add your Groq API key to .env
   ```

3. **Install Dependencies**
   ```bash
   # Backend dependencies
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd apps/frontend
   npm install
   ```

4. **Start Services**
   ```bash
   # Terminal 1: Start backend
   python apps/backend/fast_api_backend.py
   
   # Terminal 2: Start frontend
   cd apps/frontend && npm run dev
   ```

5. **Access Platform**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 📊 **Performance Metrics**

| Metric | Value | Rating |
|--------|-------|--------|
| **Bundle Size** | 65KB (gzipped) | ⭐⭐⭐⭐⭐ |
| **Load Time** | < 2 seconds | ⭐⭐⭐⭐⭐ |
| **Mobile Score** | 95+ | ⭐⭐⭐⭐⭐ |
| **Desktop Score** | 98+ | ⭐⭐⭐⭐⭐ |
| **Code Quality** | TypeScript + ESLint | ⭐⭐⭐⭐⭐ |

---

## 🛠️ **Technology Stack**

### **Frontend**
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first styling
- **Radix UI** - Accessible components

### **Backend** 
- **FastAPI** - High-performance API framework
- **Python 3.9+** - Core backend language
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### **AI & ML**
- **Groq AI** - Ultra-fast inference
- **Multi-modal Models** - Vision + text processing
- **Smart Fallbacks** - Robust error handling
- **Usage Optimization** - Free tier efficiency

### **DevOps**
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipelines
- **Nginx** - Production web server
- **Multi-platform** - HuggingFace, Vercel, Netlify ready

---

## 🤝 **Contributing**

We welcome contributions from the international legal and technology communities!

### **How to Contribute**
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 **Support & Contact**

- **📧 Email**: mosesyebei@gmail.com
- **🐙 GitHub**: [@moses-y](https://github.com/moses-y)
- **🚀 Deployment Issues**: See [deployment guide](FRONTEND_DEPLOYMENT_STRATEGY.md)
- **🐛 Bug Reports**: [Open an issue](https://github.com/moses-y/ICCLexAI/issues)

---

<div align="center">

**🌍 Built with ❤️ for Global Justice and ICC Legal Professionals**

![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)
![For Justice](https://img.shields.io/badge/For-Global%20Justice-blue?style=for-the-badge)

*Empowering evidence analysis and legal workflows with cutting-edge AI technology*

</div>
