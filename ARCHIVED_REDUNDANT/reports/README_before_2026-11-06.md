# ICC Legal AI Platform

�️ **International Criminal Court AI-Powered Evidence Analysis Platform**

[![Deploy AI-ICC Evidence Tool](https://github.com/Moses-y/ai-icc-evidence-platform/workflows/Deploy%20AI-ICC%20Evidence%20Tool/badge.svg)](https://github.com/Moses-y/ai-icc-evidence-platform/actions)
[![AI Model Monitoring](https://github.com/Moses-y/ai-icc-evidence-platform/workflows/AI%20Model%20Performance%20Monitoring/badge.svg)](https://github.com/Moses-y/ai-icc-evidence-platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌍 Mission Statement

The LLM could do more. DeepSeek is among the reasoning models. We're deploying multimodal LLMs to help extract information from ICC submissions. This is fantastic for background in building Multimodal Agentic LLMs in AI.

ICC has submission limits. In this way, we'll help them have more context of injustice around the world. We can think of this as a development direction.

## 🚀 Features

### 🤖 AI-Powered Evidence Processing
- **DeepSeek R1 Distill Llama 70B** primary reasoning model
- **Llama 3.3 70B** fallback model for reliability
- **Multimodal content extraction** from images, videos, audio, PDFs
- **Automated metadata extraction** (GPS, timestamps, EXIF data)
- **AI-generated evidence descriptions** for legal documentation

### 📱 Modern User Experience
- **TypeScript + React Frontend** with ShadCN UI components
- **Professional legal interface** suitable for ICC submissions
- **Real-time file upload** with drag-and-drop support
- **Live AI analysis results** with progress indicators
- **Responsive design** for desktop and mobile
- **Dark/light mode support** for accessibility
- **Real-time system status** monitoring

### 📱 Legacy User Experience (Streamlit)
- **Kenyan flag-themed interface** for cultural relevance
- **Multi-step form wizard** with progress tracking
- **Drag-and-drop file upload** with cloud integration placeholders
- **Real-time AI assistance** for form completion
- **Anonymous submission option** for whistleblower protection

### 🔧 Technical Architecture
- **FastAPI** async backend with parallel processing
- **TypeScript + React** modern frontend with ShadCN UI
- **Groq API** for lightning-fast AI inference
- **Google Vision API** for advanced image analysis
- **HuggingFace** for specialized AI models
- **Roboflow** for computer vision tasks
- **Redis** for caching and rate limit optimization
- **Docker** containerization for production deployment
- **Streamlit** legacy frontend option

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Groq API Key
- Chrome/Brave browser for automated submissions

### Quick Start

#### Option 1: Full Stack (TypeScript + React Frontend) - RECOMMENDED
```bash
# Windows
launch_full_stack.bat

# Linux/Mac
chmod +x launch_frontend.sh
./launch_frontend.sh
```

#### Option 2: Fast Launch (Streamlit Frontend)
```bash
# Linux/Mac
./launch_fast_app.sh

# Windows
launch_fast_app.bat
```

#### Option 3: Manual Launch
```bash
# Terminal 1 - Backend
python fast_api_backend.py

# Terminal 2 - TypeScript Frontend (Modern UI)
cd frontend
npm install
npm run dev

# OR Terminal 2 - Streamlit Frontend (Legacy)  
streamlit run fast_streamlit_app.py
```

### Environment Setup

### Docker Deployment
```bash
docker build -t ai-icc-evidence-tool .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key ai-icc-evidence-tool
```

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### AI Model Configuration
- **Primary Model**: `deepseek-r1-distill-llama-70b`
- **Fallback Model**: `llama-3.3-70b-versatile`
- **Temperature**: 0.6 (balanced creativity/accuracy)
- **Max Tokens**: 300 (optimized for legal descriptions)

## 📊 AI Model Performance

Our continuous monitoring ensures optimal AI performance:

- **Daily automated testing** of both AI models
- **Response quality validation** for legal accuracy
- **Latency monitoring** for real-time user experience
- **Fallback system testing** for 99.9% uptime

## 🌐 Deployment

### Streamlit Cloud
Automatically deployed on every push to main branch.

### Heroku
Production-ready deployment with environment isolation.

### Docker Hub
Containerized deployment for any cloud provider.

## 🛡️ Security & Privacy

- **No personal data storage** on servers
- **Anonymous submission options**
- **Encrypted file transmission**
- **Regular security scanning** with Bandit and Safety
- **GDPR-compliant data handling**

## 🤝 Contributing

We welcome contributions to enhance the AI capabilities and expand support for international justice!

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-ai-enhancement`)
3. Commit changes (`git commit -m 'Add amazing AI feature'`)
4. Push to branch (`git push origin feature/amazing-ai-enhancement`)
5. Open Pull Request

### AI Model Integration
- **Add new models** via Groq API integration
- **Implement multimodal capabilities** for video/audio analysis
- **Enhance reasoning chains** for complex evidence relationships
- **Improve multilingual support** for global accessibility

## 📈 Roadmap

### Phase 1: Foundation ✅
- [x] Basic Streamlit application
- [x] DeepSeek R1 integration
- [x] Metadata extraction
- [x] ICC form automation

### Phase 2: AI Enhancement 🚧
- [ ] Multimodal evidence analysis
- [ ] Advanced reasoning chains
- [ ] Evidence cross-referencing
- [ ] Automated evidence validation

### Phase 3: Global Scale 🔮
- [ ] Multi-language support
- [ ] Regional court integrations
- [ ] Real-time incident monitoring
- [ ] AI-powered evidence correlation

## 📚 Documentation

- [PRD - Product Requirements Document](./PRD.md)
- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [AI Model Documentation](./docs/ai-models.md)

## 🏆 Recognition

This project leverages cutting-edge AI reasoning models to democratize access to international justice mechanisms, making ICC submissions more accessible and comprehensive for victims of injustice worldwide.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Moses-y/ai-icc-evidence-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Moses-y/ai-icc-evidence-platform/discussions)
- **Email**: moses.y@ai-icc-platform.org

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for international justice and powered by advanced AI reasoning models.**

*"Technology in service of justice, AI in service of humanity."*
