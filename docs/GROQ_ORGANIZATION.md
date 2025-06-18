# AI Legal Justice Initiative - Organization Configuration

## Groq Cloud Organization Details

**Organization Name**: `AI-Legal-Justice-Initiative`  
**Owner**: Moses Yebei  
**Purpose**: AI Legal Automation & Assistance for International Criminal Court Evidence Analysis  
**Use Case**: Real-time multimodal AI analysis for ICC submissions and international justice

## Model Usage Strategy

### Primary Models (Based on Rate Limits):
1. **deepseek-r1-distill-llama-70b**: 30 RPM, 1,000 RPD, 6,000 TPM
   - Use: Complex legal reasoning and ICC evidence assessment
   - Rate: Conservative usage for high-quality analysis

2. **llama-3.3-70b-versatile**: 30 RPM, 1,000 RPD, 12,000 TPM
   - Use: Fallback model and general text generation
   - Rate: Higher token limit for detailed descriptions

3. **whisper-large-v3-turbo**: 20 RPM, 2,000 RPD, 7,200 Audio Seconds/Hour
   - Use: Audio evidence transcription
   - Rate: Sufficient for real-time audio processing

### Secondary Models:
4. **gemma2-9b-it**: 30 RPM, 14,400 RPD, 15,000 TPM
   - Use: Fast preliminary analysis
   - Rate: High request limit for bulk processing

5. **llama-guard-3-8b**: 30 RPM, 14,400 RPD, 15,000 TPM
   - Use: Content moderation and safety filtering
   - Rate: Essential for legal content validation

## Cost Optimization
- Current spend: $0.00 USD (Free tier)
- Projected usage: Stay within free limits initially
- Scale to paid tier when deploying to production

## Groq Cloud Organization Setup Instructions

### Step 1: Create Organization Account
1. Visit [console.groq.com](https://console.groq.com)
2. Click "Create Organization" or use your existing personal account
3. **Organization Name**: `AI-Legal-Justice-Initiative` 
4. **Description**: `AI Legal Automation & Assistance for International Criminal Court Evidence Analysis - Accelerating international justice through lightning-fast AI-powered legal evidence analysis`
5. **Use Case**: `Real-time multimodal AI analysis for ICC submissions and international justice using Groq's ultra-fast inference capabilities`
6. **Purpose**: For the AI work we're doing for the ICC today - AI Legal AI automation and assistance for a good cause in the world

### Your Organization Information
Based on your console dashboard:
- **Owner**: Moses Yebei  
- **Current Plan**: Personal (Free tier)
- **Monthly Spend**: $0.00 USD
- **Organization Type**: For legal AI automation supporting international justice

### Step 2: Recommended Organization Configuration
- **Owner**: Moses Yebei
- **Billing**: Start with free tier, upgrade as needed
- **Team Members**: Add technical and legal team members
- **Usage Monitoring**: Enable alerts at 80% of rate limits

### Step 3: API Key Management
1. Navigate to "API Keys" section
2. Create production key: `ICC-Evidence-Production`
3. Create development key: `ICC-Evidence-Development` 
4. Create backup key: `ICC-Evidence-Backup`
5. Set appropriate permissions and rate limits

### Step 4: Rate Limit Configuration
Based on your current limits shown in the console:
- Primary: `deepseek-r1-distill-llama-70b` (30 RPM, 1,000 RPD)
- Fallback: `llama-3.3-70b-versatile` (30 RPM, 1,000 RPD)
- Audio: `whisper-large-v3-turbo` (20 RPM, 2,000 RPD)

### Step 5: Usage Optimization Strategy
1. **Smart Queue**: Distribute requests across models
2. **Caching**: Cache repeated analyses to avoid API calls
3. **Fallback Chain**: Primary → Secondary → Cached response
4. **Monitoring**: Track usage against limits in real-time
