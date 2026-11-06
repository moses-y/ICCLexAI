# ICCLexAI Deployment Guide

## 🚀 Deployment Options

This guide covers multiple deployment strategies for the ICCLexAI platform, each optimized for different use cases.

## 📋 Prerequisites

### Required Accounts
- [GitHub](https://github.com) - Source code management
- [HuggingFace](https://huggingface.co) - AI-focused deployment
- [Netlify](https://netlify.com) - Frontend hosting
- [Railway](https://railway.app) - Backend hosting

### Required API Keys
```bash
# AI Services
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
HUGGINGFACE_TOKEN=your_hf_token
ROBOFLOW_API_KEY=your_roboflow_key

# Deployment Services
NETLIFY_AUTH_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_netlify_site_id
RAILWAY_TOKEN=your_railway_token
HF_TOKEN=your_hf_token
```

## 🎯 Option 1: HuggingFace Spaces (Recommended for AI Platform)

### Why HuggingFace?
- **AI-First Platform**: Perfect for ML/AI applications
- **Free GPU Access**: Hardware acceleration for AI models
- **Integrated ML Tools**: Built-in model hosting and inference
- **Community**: AI/ML focused audience

### Setup Steps

1. **Create HuggingFace Space**
   ```bash
   # Go to https://huggingface.co/spaces
   # Click "Create new Space"
   # Name: icclexai-platform
   # SDK: Docker
   # Hardware: CPU Basic (free) or GPU T4 small ($0.60/hour)
   ```

2. **Configure GitHub Secrets**
   ```bash
   # In your GitHub repo settings > Secrets and variables > Actions
   HF_TOKEN=your_huggingface_token
   ```

3. **Deploy**
   ```bash
   git push origin main
   # GitHub Actions will automatically deploy to HuggingFace
   ```

4. **Access Your Platform**
   ```
   https://huggingface.co/spaces/your-username/icclexai-platform
   ```

### Features
- ✅ Integrated frontend + backend
- ✅ AI model hosting
- ✅ Free tier available
- ✅ Automatic scaling
- ✅ GPU acceleration (paid tiers)

## 🌐 Option 2: Netlify + Railway (Production Ready)

### Why This Stack?
- **Performance**: Optimized for web applications
- **Scalability**: Independent scaling of frontend/backend
- **Reliability**: Enterprise-grade infrastructure
- **Cost-Effective**: Pay-as-you-scale pricing

### Frontend Deployment (Netlify)

1. **Connect GitHub to Netlify**
   ```bash
   # Visit https://app.netlify.com
   # Click "Add new site" > "Import from Git"
   # Select your ICCLexAI repository
   ```

2. **Configure Build Settings**
   ```yaml
   Build command: cd apps/frontend && npm ci && npm run build:production
   Publish directory: apps/frontend/dist
   ```

3. **Environment Variables**
   ```bash
   # In Netlify dashboard > Site settings > Environment variables
   VITE_API_URL=https://your-railway-backend.railway.app
   ```

### Backend Deployment (Railway)

1. **Connect GitHub to Railway**
   ```bash
   # Visit https://railway.app
   # Click "Deploy from GitHub repo"
   # Select your ICCLexAI repository
   ```

2. **Configure Railway**
   ```bash
   # Railway will auto-detect your Python app
   # Add environment variables in Railway dashboard
   ```

3. **Add Environment Variables**
   ```bash
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key
   HUGGINGFACE_TOKEN=your_hf_token
   ROBOFLOW_API_KEY=your_roboflow_key
   ```

### Features
- ✅ CDN-optimized frontend
- ✅ Auto-scaling backend
- ✅ Custom domains
- ✅ SSL certificates
- ✅ Production monitoring

## 🔧 Option 3: Self-Hosted Docker

### For Organizations Requiring On-Premises Deployment

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/ICCLexAI.git
   cd ICCLexAI
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Deploy with Docker Compose**
   ```bash
   cd docker
   docker-compose up -d
   ```

4. **Access Services**
   ```bash
   Frontend: http://localhost:3000
   Backend API: http://localhost:8000
   API Docs: http://localhost:8000/docs
   ```

## 🚀 Quick Start Deployment

### 1-Click HuggingFace Deployment

```bash
# Clone repository
git clone https://github.com/your-username/ICCLexAI.git
cd ICCLexAI

# Set up GitHub secrets
gh secret set HF_TOKEN --body "your_huggingface_token"

# Push to trigger deployment
git push origin main
```

### Netlify + Railway Deployment

```bash
# Set up GitHub secrets for both platforms
gh secret set NETLIFY_AUTH_TOKEN --body "your_netlify_token"
gh secret set NETLIFY_SITE_ID --body "your_netlify_site_id"
gh secret set RAILWAY_TOKEN --body "your_railway_token"

# Push to trigger deployment
git push origin main
```

## 📊 Deployment Comparison

| Feature | HuggingFace Spaces | Netlify + Railway | Self-Hosted |
|---------|-------------------|-------------------|-------------|
| **Setup Complexity** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **AI/ML Optimization** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost (Free Tier)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Control** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🔍 Monitoring and Analytics

### HuggingFace Spaces
- Built-in usage analytics
- Model performance metrics
- Community engagement stats

### Netlify + Railway
- **Netlify**: Site analytics, form submissions, build logs
- **Railway**: Resource usage, deployment logs, metrics

### Recommended Monitoring Tools
- **Sentry**: Error tracking and performance monitoring
- **LogRocket**: User session replay and debugging
- **Mixpanel**: User analytics and behavior tracking

## 🛡️ Security Considerations

### API Key Management
- Use environment variables (never commit keys)
- Rotate keys regularly
- Implement rate limiting
- Monitor API usage

### Data Privacy
- GDPR compliance for EU users
- End-to-end encryption for sensitive data
- Regular security audits
- Secure file handling for evidence uploads

## 📞 Support and Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version (18+)
   - Verify environment variables
   - Clear npm cache: `npm cache clean --force`

2. **API Connection Issues**
   - Verify backend URL in frontend config
   - Check CORS settings
   - Validate API key format

3. **Performance Issues**
   - Monitor AI model usage
   - Implement caching strategies
   - Optimize file upload sizes

### Getting Help
- 📧 Email: support@icclexai.com
- 💬 Discord: [ICCLexAI Community](https://discord.gg/icclexai)
- 📖 Docs: [docs.icclexai.com](https://docs.icclexai.com)

---

**Recommended for Legal Institutions**: Start with HuggingFace Spaces for proof-of-concept, then migrate to Netlify + Railway for production deployment with custom domains and enhanced security.
