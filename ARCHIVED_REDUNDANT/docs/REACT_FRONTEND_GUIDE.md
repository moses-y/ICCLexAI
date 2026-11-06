# TypeScript React Frontend - Quick Start

## 🚀 Ultra-Fast Setup for ICC Evidence Platform

### Prerequisites
- Node.js 18+ (Download from [nodejs.org](https://nodejs.org))
- Python 3.9+ for backend
- Your Groq API key from [console.groq.com](https://console.groq.com)

### ⚡ Lightning Setup (2 minutes)

1. **Configure Environment**
   ```bash
   # Make sure .env file exists with your API keys
   echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
   ```

2. **Launch Full Stack**
   ```bash
   # Windows (Double-click or run in PowerShell)
   launch_full_stack.bat
   
   # Linux/Mac  
   chmod +x launch_frontend.sh
   ./launch_frontend.sh
   ```

3. **Access the Application**
   - 🌐 **Frontend**: http://localhost:5173 (Modern React UI)
   - 🔗 **Backend**: http://localhost:8000 (FastAPI)
   - 📚 **API Docs**: http://localhost:8000/docs

### 🛠️ Manual Setup (Development)

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend
python fast_api_backend.py
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server with hot reload
npm run dev
```

### 🎯 Key Features

#### Modern UI Components
- **Professional Legal Interface** - Clean, accessible design suitable for ICC submissions
- **Real-time File Upload** - Drag and drop with instant feedback
- **Live Analysis Results** - See AI processing in real-time
- **Progress Indicators** - Visual feedback for long-running analyses
- **Responsive Design** - Works on desktop, tablet, and mobile

#### AI-Powered Analysis
- **Multi-format Support** - Images, audio, PDFs, Word documents
- **Parallel Processing** - Multiple files analyzed simultaneously  
- **Smart Caching** - Redis-backed caching for faster repeat analyses
- **Rate Limit Handling** - Automatic queue management for API limits

#### Technical Stack
- **Frontend**: TypeScript + React + Vite + ShadCN UI + TailwindCSS
- **Backend**: FastAPI + Python + Async processing
- **AI**: Groq (Lightning-fast inference) + Google Vision + HuggingFace
- **Caching**: Redis for performance optimization
- **State Management**: Zustand + React Query

### 🐳 Docker Deployment

#### Quick Docker Launch
```bash
# Build and run everything
docker-compose up --build

# Access at http://localhost (production-ready)
```

#### Individual Containers
```bash
# Backend only
docker build -f Dockerfile.fastapi -t icc-backend .
docker run -p 8000:8000 icc-backend

# Frontend only  
docker build -f Dockerfile.react -t icc-frontend ./frontend
docker run -p 80:80 icc-frontend
```

### 🚀 Production Deployment

#### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy backend
railway login
railway link [your-project-id]
railway up

# Deploy frontend (separate service)
cd frontend
railway up
```

#### Vercel (Frontend) + Railway (Backend)
```bash
# Frontend to Vercel
cd frontend
npm install -g vercel
vercel

# Backend to Railway
railway up
```

### 🔧 Configuration

#### Environment Variables (.env)
```bash
# Required for AI functionality
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_vision_key  
HUGGINGFACE_TOKEN=your_huggingface_token
ROBOFLOW_API_KEY=your_roboflow_key

# Optional for advanced features
REDIS_URL=redis://localhost:6379
SENTRY_DSN=your_sentry_dsn_for_monitoring
```

#### Frontend Configuration (frontend/.env.local)
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE="ICC Evidence AI"
VITE_ENABLE_ANALYTICS=false
```

### 🎨 UI Customization

#### Theme Colors (frontend/src/index.css)
```css
:root {
  --primary: 221.2 83.2% 53.3%;        /* Blue for ICC branding */
  --secondary: 210 40% 96%;             /* Light gray */
  --accent: 210 40% 96%;                /* Accent color */
  --destructive: 0 84.2% 60.2%;         /* Red for errors */
}
```

#### Component Styling
- Uses **ShadCN UI** components for consistency
- **TailwindCSS** for rapid styling
- **Dark/Light mode** support built-in
- **Responsive breakpoints** for all devices

### 🔍 Debugging

#### Check System Status
```bash
# Backend health
curl http://localhost:8000/health

# Frontend build
cd frontend && npm run build

# Check API connectivity
curl http://localhost:8000/analyze -X POST -F "file=@test.jpg"
```

#### Common Issues
1. **Port conflicts**: Change ports in vite.config.ts or fast_api_backend.py
2. **API key issues**: Verify .env file is in root directory
3. **CORS errors**: Ensure backend CORS settings allow frontend origin
4. **Build failures**: Clear node_modules and reinstall dependencies

### 📱 Mobile Support

The React frontend is fully responsive:
- **Mobile-first design** with touch-friendly interactions
- **Progressive Web App** capabilities for offline use
- **Optimized file upload** for mobile cameras
- **Adaptive layouts** for different screen sizes

### 🚀 Performance

#### Optimization Features
- **Code splitting** - Lazy load components for faster initial load
- **Image optimization** - Automatic compression and format conversion
- **Bundle analysis** - Use `npm run build && npm run preview` to test
- **Service workers** - Background processing and caching

#### Monitoring
```bash
# Build size analysis
cd frontend
npm run build
npm run analyze

# Performance testing
npm install -g lighthouse
lighthouse http://localhost:5173
```

---

## 🎯 Next Steps

1. **Configure Groq Organization**: Follow `GROQ_ORGANIZATION.md`
2. **Deploy to Production**: Use Railway/Vercel for live deployment
3. **Add Custom Features**: Extend with additional AI models or integrations
4. **Monitor Usage**: Set up analytics and error tracking

**Ready to process ICC evidence with lightning speed! ⚡🏛️**
