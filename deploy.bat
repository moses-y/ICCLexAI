@echo off
REM ICCLexAI Quick Deployment Script for Windows
REM Supports multiple deployment targets

echo 🏛️ ICCLexAI Deployment Script (Windows)
echo ==========================================

REM Colors for output (Windows compatible)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Check dependencies
echo %INFO% Checking dependencies...

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo %ERROR% Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo %ERROR% npm is not installed. Please install npm first.
    pause
    exit /b 1
)

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo %ERROR% Git is not installed. Please install Git first.
    pause
    exit /b 1
)

echo %SUCCESS% All dependencies are installed.

REM Setup environment
echo %INFO% Setting up environment...

if not exist ".env" (
    echo %WARNING% .env file not found. Creating from template...
    (
        echo # AI API Keys
        echo GROQ_API_KEY=your_groq_api_key_here
        echo GOOGLE_API_KEY=your_google_api_key_here
        echo HUGGINGFACE_TOKEN=your_huggingface_token_here
        echo ROBOFLOW_API_KEY=your_roboflow_api_key_here
        echo.
        echo # Deployment Tokens
        echo NETLIFY_AUTH_TOKEN=your_netlify_token_here
        echo NETLIFY_SITE_ID=your_netlify_site_id_here
        echo RAILWAY_TOKEN=your_railway_token_here
        echo HF_TOKEN=your_hf_token_here
    ) > .env
    echo %WARNING% Please edit .env file with your actual API keys before deploying.
)

echo %SUCCESS% Environment setup complete.

:main_menu
echo.
echo Choose deployment option:
echo 1^) 🤗 HuggingFace Spaces (AI-optimized, free GPU^)
echo 2^) 🌐 Build for Netlify (Frontend only, fast CDN^)
echo 3^) 📦 Build All (prepare for manual deployment^)
echo 4^) 🐳 Docker Build (local container deployment^)
echo 5^) ❓ Help ^& Documentation
echo 6^) 🚪 Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto deploy_huggingface
if "%choice%"=="2" goto build_netlify
if "%choice%"=="3" goto build_all
if "%choice%"=="4" goto docker_build
if "%choice%"=="5" goto show_help
if "%choice%"=="6" goto exit_script
echo %ERROR% Invalid option. Please choose 1-6.
goto main_menu

:deploy_huggingface
echo %INFO% Preparing HuggingFace Spaces deployment...

REM Build frontend first
echo %INFO% Building React frontend...
cd apps\frontend

if not exist "node_modules" (
    echo %INFO% Installing frontend dependencies...
    npm install
)

echo %INFO% Building production frontend...
npm run build:production
cd ..\..

REM Create deployment directory
if exist "hf-deployment" rmdir /s /q hf-deployment
mkdir hf-deployment

REM Copy frontend build
xcopy "apps\frontend\dist\*" "hf-deployment\" /s /e /q

REM Copy backend
xcopy "apps\backend\*" "hf-deployment\" /s /e /q
copy "requirements.txt" "hf-deployment\"

REM Create Gradio app wrapper
(
    echo import gradio as gr
    echo import subprocess
    echo import threading
    echo import time
    echo import os
    echo.
    echo def start_backend(^):
    echo     subprocess.Popen(["uvicorn", "fast_api_backend:app", "--host", "0.0.0.0", "--port", "7861"]^)
    echo.
    echo threading.Thread(target=start_backend, daemon=True^).start(^)
    echo time.sleep(5^)
    echo.
    echo with gr.Blocks(title="ICCLexAI - AI-Powered Legal Case Analysis", theme=gr.themes.Soft(^)^) as demo:
    echo     gr.HTML("""
    echo     ^<div style="text-align: center; margin-bottom: 20px; padding: 20px; background: linear-gradient(90deg, #667eea 0%%, #764ba2 100%%^); border-radius: 10px; color: white;"^>
    echo         ^<h1 style="margin: 0; font-size: 2.5em;"^>🏛️ ICCLexAI Platform^</h1^>
    echo         ^<p style="margin: 10px 0 0 0; font-size: 1.2em;"^>AI-Powered Evidence Analysis for International Criminal Court Submissions^</p^>
    echo     ^</div^>
    echo     """^)
    echo     
    echo     gr.HTML("""
    echo     ^<div style="text-align: center; margin: 20px 0;"^>
    echo         ^<a href="/static" target="_blank" style="
    echo             display: inline-block;
    echo             padding: 15px 30px;
    echo             background: linear-gradient(90deg, #667eea 0%%, #764ba2 100%%^);
    echo             color: white;
    echo             text-decoration: none;
    echo             border-radius: 8px;
    echo             font-weight: bold;
    echo             font-size: 1.1em;
    echo         "^>🚀 Launch ICCLexAI Platform^</a^>
    echo     ^</div^>
    echo     """^)
    echo.
    echo if __name__ == "__main__":
    echo     demo.launch(server_name="0.0.0.0", server_port=7860^)
) > hf-deployment\app.py

REM Create Dockerfile
(
    echo FROM python:3.11-slim
    echo.
    echo WORKDIR /app
    echo.
    echo RUN apt-get update ^&^& apt-get install -y \
    echo     curl \
    echo     ffmpeg \
    echo     libsm6 \
    echo     libxext6 \
    echo     ^&^& rm -rf /var/lib/apt/lists/*
    echo.
    echo COPY requirements.txt .
    echo RUN pip install --no-cache-dir -r requirements.txt
    echo RUN pip install gradio uvicorn
    echo.
    echo COPY . .
    echo.
    echo EXPOSE 7860
    echo.
    echo CMD ["python", "app.py"]
) > hf-deployment\Dockerfile

echo %SUCCESS% HuggingFace deployment package created in .\hf-deployment\
echo %WARNING% Please upload the hf-deployment folder to your HuggingFace Space.
echo %WARNING% Visit: https://huggingface.co/spaces
pause
goto main_menu

:build_netlify
echo %INFO% Building for Netlify deployment...
cd apps\frontend

if not exist "node_modules" (
    echo %INFO% Installing frontend dependencies...
    npm install
)

echo %INFO% Building production frontend...
npm run build:production

echo %SUCCESS% Frontend built for Netlify in .\apps\frontend\dist\
echo %WARNING% To deploy to Netlify:
echo %WARNING% 1. Upload the dist folder to Netlify dashboard
echo %WARNING% 2. Or use Netlify CLI: netlify deploy --dir=dist --prod

cd ..\..
pause
goto main_menu

:build_all
echo %INFO% Building all components...

REM Build frontend
cd apps\frontend
if not exist "node_modules" (
    npm install
)
npm run build:production
cd ..\..

echo %SUCCESS% All builds complete!
echo - Frontend: .\apps\frontend\dist\
echo - Backend: .\apps\backend\
pause
goto main_menu

:docker_build
echo %INFO% Building Docker containers...
cd docker
docker-compose up --build -d

echo %SUCCESS% Docker containers started!
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs

cd ..
pause
goto main_menu

:show_help
echo.
echo 📖 Documentation:
echo - Full deployment guide: .\DEPLOYMENT_STRATEGY.md
echo - Frontend guide: .\apps\frontend\DEPLOYMENT.md
echo - Backend API docs: http://localhost:8000/docs (when running locally^)
echo.
echo 🔗 Useful Links:
echo - HuggingFace Spaces: https://huggingface.co/spaces
echo - Netlify Dashboard: https://app.netlify.com
echo - Railway Dashboard: https://railway.app
echo.
pause
goto main_menu

:exit_script
echo %SUCCESS% Goodbye! 👋
pause
exit /b 0
