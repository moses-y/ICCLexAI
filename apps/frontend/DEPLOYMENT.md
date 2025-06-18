# ICCLexAI Frontend Deployment Guide

## HuggingFace Spaces Deployment (Recommended)

### Prerequisites
- Node.js 18+ installed
- HuggingFace account
- Git configured

### Step 1: Prepare the Build
```bash
# Navigate to frontend directory
cd apps/frontend

# Install dependencies
npm install

# Build for production
npm run build:hf
```

### Step 2: Create HuggingFace Space
1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure:
   - **Space name**: `icclexai-frontend`
   - **License**: `MIT`
   - **SDK**: `Docker`
   - **Hardware**: `CPU basic` (free tier)
   - **Visibility**: `Public`

### Step 3: Deploy to HuggingFace
```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/icclexai-frontend
cd icclexai-frontend

# Copy built files
cp -r ../apps/frontend/dist/* .
cp ../apps/frontend/Dockerfile.production ./Dockerfile
cp ../apps/frontend/nginx.production.conf ./nginx.conf

# Create README.md for the space
cat > README.md << 'EOF'
---
title: ICCLexAI
emoji: ⚖️
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
---

# ICCLexAI - Kenya Legal AI Platform

Professional AI-powered platform for International Criminal Court (ICC) legal document analysis and submission generation.

## Features
- 🇰🇪 **Kenyan-themed interface**
- 📄 **Multi-format document analysis**
- 🤖 **AI-powered legal insights**
- 📱 **Mobile-responsive design**
- ⚡ **Real-time processing**

## Usage
1. Upload legal documents (PDF, Word, images)
2. Provide case keywords and context
3. Get AI-powered analysis and suggestions
4. Generate ICC-compliant submissions

Built with React, TypeScript, and modern AI technologies.
EOF

# Add environment file for production
cat > .env.production << 'EOF'
VITE_API_URL=https://icclexai-backend.railway.app
VITE_APP_VERSION=1.0.0
VITE_GA_TRACKING_ID=your-ga-id
EOF

# Commit and push
git add .
git commit -m "🚀 Deploy ICCLexAI Frontend v1.0.0"
git push
```

### Step 4: Configure Backend API
Make sure your FastAPI backend is deployed and accessible at the URL specified in `.env.production`.

### Step 5: Custom Domain (Optional)
1. In your HuggingFace Space settings
2. Go to "Settings" → "Rename or transfer"
3. Add custom domain if you have one

## Alternative Deployment Options

### Option 1: Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd apps/frontend
npm run build
vercel --prod
```

### Option 2: Netlify
```bash
# Build the app
npm run build

# Deploy to Netlify (drag & drop dist folder)
# Or use Netlify CLI:
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### Option 3: Railway (Full Stack)
```bash
# Create railway.json in project root
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run start:production",
    "healthcheckPath": "/health"
  }
}
```

## Environment Variables

### Required for Production
```env
VITE_API_URL=https://your-backend-url.com
VITE_APP_VERSION=1.0.0
```

### Optional
```env
VITE_GA_TRACKING_ID=GA-XXXXXXXXX
VITE_SENTRY_DSN=https://your-sentry-dsn
```

## Performance Optimization

### Build Analysis
```bash
# Analyze bundle size
npm run analyze

# Check build output
npm run build && ls -la dist/
```

### Monitoring
- Use browser dev tools for performance metrics
- Monitor Core Web Vitals
- Set up error tracking with Sentry

## Security Checklist

- ✅ No API keys in frontend code
- ✅ Environment variables for configuration
- ✅ HTTPS enforcement
- ✅ Content Security Policy headers
- ✅ Input validation
- ✅ Error boundaries implemented

## Troubleshooting

### Common Issues

1. **Build fails with TypeScript errors**
   ```bash
   npm run type-check
   npm run lint:fix
   ```

2. **API calls fail in production**
   - Check CORS configuration on backend
   - Verify API URL in environment variables
   - Check network connectivity

3. **Static files not loading**
   - Verify nginx configuration
   - Check file paths and build output
   - Ensure proper MIME types

### Support
- Check logs in HuggingFace Spaces
- Use browser developer tools
- Review error boundary outputs

## Next Steps
1. Set up monitoring and analytics
2. Configure custom domain
3. Add SSL certificate
4. Set up CI/CD pipeline
5. Implement A/B testing
