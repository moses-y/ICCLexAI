#!/bin/bash

# GitHub Repository Creation Script for AI-ICC Evidence Platform
# Run this script to create and configure your GitHub repository

echo "🚀 Creating AI-ICC Evidence Platform Repository on GitHub..."

# Configuration
GITHUB_USERNAME="Moses-y"
REPO_NAME="ai-icc-evidence-platform"
GITHUB_TOKEN="${GITHUB_TOKEN:-your_github_token_here}"

# Create repository using GitHub CLI or curl
echo "📝 Creating repository: $REPO_NAME"

# Create repository via GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/user/repos \
     -d '{
       "name": "'$REPO_NAME'",
       "description": "🇰🇪 AI-Enhanced ICC Evidence Submission Platform - Multimodal LLMs for International Justice",
       "homepage": "https://ai-icc-evidence-platform.streamlit.app",
       "private": false,
       "has_issues": true,
       "has_projects": true,
       "has_wiki": true,
       "has_pages": true,
       "has_downloads": true,
       "auto_init": false,
       "license_template": "mit"
     }'

echo "✅ Repository created successfully!"

# Initialize Git if not already done
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git add .
    git commit -m "🎉 Initial commit: AI-ICC Evidence Platform with DeepSeek R1 & Llama 3.3"
fi

# Add GitHub remote
echo "🔗 Adding GitHub remote..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Create and push to main branch
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

# Set up branch protection rules
echo "🛡️ Setting up branch protection..."
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     -X PUT \
     https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/branches/main/protection \
     -d '{
       "required_status_checks": {
         "strict": true,
         "contexts": ["test", "security-scan"]
       },
       "enforce_admins": false,
       "required_pull_request_reviews": {
         "required_approving_review_count": 1,
         "dismiss_stale_reviews": true
       },
       "restrictions": null
     }'

# Configure repository topics
echo "🏷️ Adding repository topics..."
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.preview+json" \
     -X PUT \
     https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/topics \
     -d '{
       "names": [
         "ai", "llm", "icc", "justice", "deepseek", "llama", "streamlit", 
         "multimodal", "evidence", "legal-tech", "groq", "reasoning", 
         "kenya", "international-law", "human-rights"
       ]
     }'

# Create repository secrets (these need to be set manually in GitHub UI)
echo "🔐 Repository secrets to configure manually in GitHub:"
echo "   - GROQ_API_KEY: Your Groq API key"
echo "   - STREAMLIT_TOKEN: For Streamlit Cloud deployment"
echo "   - HEROKU_API_KEY: For Heroku deployment"
echo "   - DOCKERHUB_USERNAME: Your Docker Hub username"
echo "   - DOCKERHUB_TOKEN: Your Docker Hub access token"
echo "   - DISCORD_WEBHOOK: For deployment notifications"

echo ""
echo "🎉 Repository setup complete!"
echo "🔗 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "📊 Actions URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo "⚙️ Settings URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME/settings"
echo ""
echo "📋 Next steps:"
echo "1. Go to repository settings and add secrets"
echo "2. Enable GitHub Pages for documentation"
echo "3. Configure Streamlit Cloud deployment"
echo "4. Set up Discord webhook for notifications"
echo "5. Review and merge any pending PRs"
