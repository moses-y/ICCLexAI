# Deployment Guide

## Overview

This guide covers deploying the AI-ICC Evidence Platform across multiple environments.

## Quick Deployment Options

### 1. Streamlit Cloud (Recommended for Demo)

**Prerequisites:**
- GitHub repository
- Streamlit Cloud account
- Groq API key

**Steps:**
1. Connect repository to Streamlit Cloud
2. Set environment variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   ```
3. Deploy from `main` branch
4. Access at: `https://ai-icc-evidence-platform.streamlit.app`

### 2. Heroku Deployment

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Steps:**
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create ai-icc-evidence-tool

# Set environment variables
heroku config:set GROQ_API_KEY=your_groq_api_key

# Deploy
git push heroku main
```

### 3. Docker Deployment

**Local Docker:**
```bash
# Build image
docker build -t ai-icc-evidence-tool .

# Run container
docker run -p 8501:8501 -e GROQ_API_KEY=your_key ai-icc-evidence-tool
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./uploads:/app/uploads
```

## Production Deployment

### AWS ECS with Fargate

**Infrastructure as Code (Terraform):**
```hcl
resource "aws_ecs_cluster" "ai_icc_cluster" {
  name = "ai-icc-evidence-platform"
}

resource "aws_ecs_task_definition" "ai_icc_task" {
  family                   = "ai-icc-evidence-tool"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  
  container_definitions = jsonencode([{
    name  = "ai-icc-app"
    image = "moses-y/ai-icc-evidence-tool:latest"
    
    portMappings = [{
      containerPort = 8501
      hostPort      = 8501
    }]
    
    environment = [
      {
        name  = "GROQ_API_KEY"
        value = var.groq_api_key
      }
    ]
  }])
}
```

### Google Cloud Run

**Deployment:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-icc-evidence-tool

# Deploy to Cloud Run
gcloud run deploy ai-icc-evidence-platform \
  --image gcr.io/PROJECT_ID/ai-icc-evidence-tool \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key
```

### Azure Container Instances

**Deployment:**
```bash
# Create resource group
az group create --name ai-icc-rg --location eastus

# Deploy container
az container create \
  --resource-group ai-icc-rg \
  --name ai-icc-evidence-tool \
  --image moses-y/ai-icc-evidence-tool:latest \
  --dns-name-label ai-icc-evidence \
  --ports 8501 \
  --environment-variables GROQ_API_KEY=your_key
```

## Environment Configuration

### Environment Variables

**Required:**
```bash
GROQ_API_KEY=your_groq_api_key_here
```

**Optional:**
```bash
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50

# AI Configuration
PRIMARY_MODEL=deepseek-r1-distill-llama-70b
FALLBACK_MODEL=llama-3.3-70b-versatile
AI_TEMPERATURE=0.6
MAX_TOKENS=300
```

### Secrets Management

**GitHub Secrets:**
- `GROQ_API_KEY`: Groq API access
- `STREAMLIT_TOKEN`: Streamlit Cloud deployment
- `HEROKU_API_KEY`: Heroku deployment
- `DOCKERHUB_USERNAME`: Docker Hub access
- `DOCKERHUB_TOKEN`: Docker Hub token
- `DISCORD_WEBHOOK`: Deployment notifications

**AWS Secrets Manager:**
```json
{
  "groq_api_key": "your_groq_api_key",
  "streamlit_config": {
    "server_port": 8501,
    "max_upload_size": 200
  }
}
```

## Monitoring & Observability

### Health Checks

**Application Health:**
```python
# Health check endpoint
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "ai_models": {
            "primary": "deepseek-r1-distill-llama-70b",
            "fallback": "llama-3.3-70b-versatile"
        }
    }
```

**Docker Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

### Logging

**Structured Logging:**
```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log AI model usage
logger.info(json.dumps({
    "event": "ai_request",
    "model": "deepseek-r1-distill-llama-70b",
    "response_time": 1.2,
    "tokens_used": 150
}))
```

### Metrics

**Application Metrics:**
- Request count and response times
- AI model usage and performance
- File upload statistics
- Error rates and types

**Infrastructure Metrics:**
- CPU and memory usage
- Network I/O
- Storage utilization
- Container health

## Security Considerations

### Application Security

**Environment Isolation:**
```bash
# Use non-root user
USER app

# Read-only file system
--read-only --tmpfs /tmp
```

**API Security:**
```python
# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
def ai_generate():
    pass
```

### Data Protection

**Encryption in Transit:**
- HTTPS enforcement
- TLS 1.3 minimum
- Certificate pinning

**Encryption at Rest:**
- Temporary file encryption
- Database encryption
- Backup encryption

**Data Retention:**
- No persistent user data storage
- Automatic temporary file cleanup
- Audit log retention policies

## Performance Optimization

### Caching Strategy

**Model Response Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_ai_response(prompt_hash, model):
    return generate_ai_response(prompt, model)
```

**Static Asset Caching:**
```nginx
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Load Balancing

**Nginx Configuration:**
```nginx
upstream ai_icc_app {
    server app1:8501;
    server app2:8501;
    server app3:8501;
}

server {
    listen 80;
    location / {
        proxy_pass http://ai_icc_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Disaster Recovery

### Backup Strategy

**Application State:**
- Configuration backups
- Database snapshots
- File storage backups

**Recovery Procedures:**
1. Infrastructure restoration
2. Configuration deployment
3. Data restoration
4. Service validation

### High Availability

**Multi-Region Deployment:**
- Primary: US East
- Secondary: EU West
- Tertiary: Asia Pacific

**Failover Strategy:**
- Automatic health monitoring
- DNS-based failover
- Load balancer health checks

## Troubleshooting

### Common Issues

**AI Model Timeouts:**
```bash
# Check model availability
curl -H "Authorization: Bearer $GROQ_API_KEY" \
     https://api.groq.com/openai/v1/models
```

**Memory Issues:**
```bash
# Monitor container memory
docker stats ai-icc-evidence-tool
```

**File Upload Problems:**
```python
# Check upload limits
streamlit config show | grep maxUploadSize
```

### Debugging Tools

**Local Development:**
```bash
# Run with debug mode
streamlit run main_app.py --logger.level debug

# Check application logs
docker logs -f ai-icc-evidence-tool
```

**Production Debugging:**
```bash
# Remote debugging
kubectl exec -it ai-icc-pod -- /bin/bash

# Log streaming
kubectl logs -f deployment/ai-icc-evidence-platform
```
