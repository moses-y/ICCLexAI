# ICCLexAI Frontend Deployment Script (PowerShell)
# Automates deployment to HuggingFace Spaces

param(
    [switch]$BuildOnly,
    [switch]$PrepareOnly,
    [switch]$Help
)

# Configuration
$FrontendDir = "apps\frontend"
$BuildDir = "dist"
$BackendUrl = "https://icclexai-backend.railway.app"

# Colors for output
$InfoColor = "Green"
$WarnColor = "Yellow"
$ErrorColor = "Red"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    switch ($Level) {
        "INFO" { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor $InfoColor }
        "WARN" { Write-Host "[$timestamp] [WARN] $Message" -ForegroundColor $WarnColor }
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor $ErrorColor }
    }
}

function Show-Help {
    Write-Host "ICCLexAI Frontend Deployment Script" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy-frontend.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -BuildOnly     Only build the application"
    Write-Host "  -PrepareOnly   Only prepare deployment files"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\deploy-frontend.ps1              # Full deployment preparation"
    Write-Host "  .\deploy-frontend.ps1 -BuildOnly   # Build only"
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    $errors = @()
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Log "Node.js version: $nodeVersion"
    }
    catch {
        $errors += "Node.js is not installed or not in PATH"
    }
    
    # Check npm
    try {
        $npmVersion = npm --version
        Write-Log "npm version: $npmVersion"
    }
    catch {
        $errors += "npm is not installed or not in PATH"
    }
    
    # Check Git
    try {
        $gitVersion = git --version
        Write-Log "Git version: $gitVersion"
    }
    catch {
        $errors += "Git is not installed or not in PATH"
    }
    
    if ($errors.Count -gt 0) {
        Write-Log "Prerequisites check failed:" "ERROR"
        foreach ($error in $errors) {
            Write-Log "  - $error" "ERROR"
        }
        exit 1
    }
    
    Write-Log "Prerequisites check passed ✅"
}

function Build-Application {
    Write-Log "Building React application..."
    
    # Navigate to frontend directory
    Push-Location $FrontendDir
    
    try {
        # Install dependencies
        Write-Log "Installing dependencies..."
        npm ci
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
        
        # Run type checking
        Write-Log "Running type check..."
        npm run type-check
        if ($LASTEXITCODE -ne 0) { throw "Type check failed" }
        
        # Run linting
        Write-Log "Running linter..."
        npm run lint
        if ($LASTEXITCODE -ne 0) { throw "Linting failed" }
        
        # Create production environment file
        Write-Log "Creating production environment..."
        @"
VITE_API_URL=$BackendUrl
VITE_APP_VERSION=1.0.0
VITE_GA_TRACKING_ID=
VITE_SENTRY_DSN=
"@ | Out-File -FilePath ".env.production" -Encoding UTF8
        
        # Build for production
        Write-Log "Building for production..."
        npm run build:production
        if ($LASTEXITCODE -ne 0) { throw "Build failed" }
        
        Write-Log "Build completed successfully ✅"
    }
    catch {
        Write-Log "Build failed: $_" "ERROR"
        Pop-Location
        exit 1
    }
    finally {
        Pop-Location
    }
}

function Prepare-HFDeployment {
    Write-Log "Preparing HuggingFace deployment files..."
    
    $buildPath = Join-Path $FrontendDir $BuildDir
    
    # Copy Docker files to build directory
    Copy-Item "$FrontendDir\Dockerfile.production" "$buildPath\Dockerfile"
    Copy-Item "$FrontendDir\nginx.production.conf" "$buildPath\nginx.conf"
    
    # Create HuggingFace README
    $readmeContent = @"
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

Built with React, TypeScript, and Tailwind CSS.

## Technology Stack
- React 18 + TypeScript
- Vite for fast builds
- Tailwind CSS + Radix UI
- TanStack Query for data fetching
- Zustand for state management

## Support
For support and documentation, visit our [GitHub repository](https://github.com/your-username/icclexai).
"@
    
    $readmeContent | Out-File -FilePath "$buildPath\README.md" -Encoding UTF8
    
    Write-Log "HuggingFace files prepared ✅"
}

function Generate-Report {
    Write-Log "Generating deployment report..."
    
    $buildPath = Join-Path $FrontendDir $BuildDir
    $reportContent = @"
# ICCLexAI Frontend Deployment Report

**Date**: $(Get-Date)
**Build Status**: ✅ Success
**Frontend Directory**: $FrontendDir
**Build Directory**: $BuildDir

## Build Summary
- TypeScript compilation: ✅ Passed
- ESLint checks: ✅ Passed
- Production build: ✅ Success
- File optimization: ✅ Complete

## Deployment Files
- Dockerfile: ✅ Created
- Nginx config: ✅ Ready
- Environment: ✅ Configured
- README: ✅ Generated

## Next Steps
1. Create HuggingFace Space at https://huggingface.co/spaces
2. Choose Docker SDK
3. Upload deployment files from $buildPath\
4. Configure custom domain (optional)
5. Set up monitoring

## File Information
$(Get-ChildItem $buildPath -Recurse | Measure-Object -Property Length -Sum | ForEach-Object { "Total files: $($_.Count), Total size: $([math]::Round($_.Sum / 1MB, 2)) MB" })

## Quick Deployment Commands
```bash
# 1. Create and clone your HuggingFace space
git clone https://huggingface.co/spaces/YOUR_USERNAME/icclexai-frontend

# 2. Copy files
Copy-Item "$buildPath\*" "icclexai-frontend\" -Recurse -Force

# 3. Deploy
cd icclexai-frontend
git add .
git commit -m "🚀 Deploy ICCLexAI Frontend v1.0.0"
git push
```
"@
    
    $reportContent | Out-File -FilePath "deployment-report.md" -Encoding UTF8
    Write-Log "Deployment report saved to deployment-report.md"
}

function Show-NextSteps {
    Write-Host ""
    Write-Log "🎉 Deployment preparation completed!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Review deployment-report.md"
    Write-Host "2. Create HuggingFace Space at https://huggingface.co/spaces"
    Write-Host "3. Choose 'Docker' as SDK"
    Write-Host "4. Upload files from $FrontendDir\$BuildDir\"
    Write-Host "5. Test the deployed application"
    Write-Host ""
    Write-Log "Your ICCLexAI frontend is ready for production! 🇰🇪"
}

# Main execution flow
function Main {
    Write-Host "🇰🇪 ICCLexAI Frontend Deployment Script" -ForegroundColor Cyan
    Write-Host "=======================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($Help) {
        Show-Help
        return
    }
    
    if ($PrepareOnly) {
        Prepare-HFDeployment
        return
    }
    
    if ($BuildOnly) {
        Test-Prerequisites
        Build-Application
        return
    }
    
    # Full deployment preparation
    Test-Prerequisites
    Build-Application
    Prepare-HFDeployment
    Generate-Report
    Show-NextSteps
}

# Run the main function
Main
