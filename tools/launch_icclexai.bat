@echo off
REM 🇰🇪 ICCLexAI CONSOLIDATED 5-AGENT LAUNCHER  
REM Launches the consolidated 5-agent architecture (post-June 2025 optimization)
REM Author: ICCLexAI Consolidation Team | Date: June 18, 2025

title ICCLexAI - Consolidated 5-Agent Platform

color 0A
echo.
echo ============================================================================
echo   🇰🇪 ICCLexAI - CONSOLIDATED 5-AGENT AI PLATFORM (Post-Consolidation)
echo ============================================================================
echo   🤖 Master Orchestrator  │  � Evidence Analysis  │  � Automation Agents
echo ============================================================================
echo.

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: uv is not installed or not in PATH!
    echo Please install uv first: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

REM Clean up any existing processes on our ports
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8502"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8505"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8506"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak > nul

echo ✅ Port cleanup complete
echo.

REM Sync dependencies first
echo 📦 Syncing dependencies with uv...
uv sync
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to sync dependencies!
    pause
    exit /b 1
)
echo ✅ Dependencies synced
echo.

REM Display menu
echo Choose launch option:
echo.
echo [1] 🚀 FULL PLATFORM    - Master Orchestrator + Backend + Frontend  
echo [2] 🤖 MASTER ORCHESTRATOR - Main agentic workflow (CONSOLIDATED)
echo [3] 🔧 BACKEND ONLY     - API backend with 5 agents
echo [4] 💻 FRONTEND ONLY    - React frontend only
echo [5] 🔬 DEVELOPMENT      - All + extra debug info
echo [6] ❌ EXIT
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto full_platform
if "%choice%"=="2" goto agentic_only
if "%choice%"=="3" goto backend_only
if "%choice%"=="4" goto frontend_only
if "%choice%"=="5" goto development
if "%choice%"=="6" goto exit
goto invalid_choice

:full_platform
echo.
echo 🚀 LAUNCHING CONSOLIDATED FULL PLATFORM...
echo ==========================================
echo.

echo 🔥 [1/3] Starting Backend (5 Consolidated Agents)...
start "ICCLexAI-Backend" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 4 /nobreak > nul

echo 🤖 [2/3] Starting Master Orchestrator...
start "ICCLexAI-Orchestrator" cmd /k "cd apps/agentic-ui && uv run streamlit run agentic_icc_app.py --server.port 8505 --server.headless false"
timeout /t 3 /nobreak > nul

echo 💻 [3/3] Starting React Frontend...
start "ICCLexAI-Frontend" cmd /k "cd apps/frontend && npm run dev"

goto show_services

:agentic_only
echo.
echo 🤖 LAUNCHING MASTER ORCHESTRATOR (CONSOLIDATED)...
echo =================================================
echo.
echo 🔥 Starting Backend (5 Specialized Agents)...
start "ICCLexAI-Backend" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 4 /nobreak > nul

echo 🤖 Starting Master Orchestrator...
start "ICCLexAI-Orchestrator" cmd /k "cd apps/agentic-ui && uv run streamlit run agentic_icc_app.py --server.port 8505 --server.headless false"
goto show_agentic

:backend_only
echo.
echo 🔧 LAUNCHING BACKEND WITH 5 SPECIALIZED AGENTS...
echo ================================================
echo.
echo 🔥 Starting Consolidated Backend:
echo    - 📊 Metadata Extraction Agent
echo    - 🤖 Selenium Automation Agent  
echo    - 🔗 FastAPI Integration Agent
echo    - 🧠 Evidence Analysis Agent
echo    - � Master API Integration
echo.
start "ICCLexAI-Backend" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload"
goto show_backend

:frontend_only
echo.
echo 💻 LAUNCHING REACT FRONTEND ONLY...
echo ==================================
echo.
echo 💻 Starting React Frontend...
start "ICCLexAI-Frontend" cmd /k "cd apps/frontend && npm run dev"
goto show_frontend

:development
echo.
echo 🔬 LAUNCHING DEVELOPMENT MODE (CONSOLIDATED)...
echo ==============================================
echo.
echo 🔥 [1/3] Starting Backend with debug logging...
start "ICCLexAI-Backend-Dev" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload --log-level debug"
timeout /t 4 /nobreak > nul

echo 🤖 [2/3] Starting Master Orchestrator with debug...
start "ICCLexAI-Orchestrator-Dev" cmd /k "cd apps/agentic-ui && uv run streamlit run agentic_icc_app.py --server.port 8505 --server.headless false --logger.level debug"
timeout /t 3 /nobreak > nul

echo 💻 [3/3] Starting React Frontend with dev tools...
start "ICCLexAI-Frontend-Dev" cmd /k "cd apps/frontend && npm run dev"
timeout /t 2 /nobreak > nul

echo 🔍 Opening development monitoring...
start "Dev-Monitor" cmd /k "echo === 5-AGENT MONITORING === && echo 1. Metadata Extraction Agent && echo 2. Selenium Automation Agent && echo 3. FastAPI Integration Agent && echo 4. Evidence Analysis Agent && echo 5. Master Orchestrator && echo === API Docs: http://localhost:8001/docs === && pause"

goto show_services

:show_services
echo.
echo ✅ CONSOLIDATED ICCLEXAI PLATFORM LAUNCHED!
echo ==========================================
echo.
echo 🇰🇪 CONSOLIDATED SERVICES:
echo    🤖 Master Orchestrator:    http://localhost:8505
echo    🔥 Backend (5 agents):     http://localhost:8001  
echo     React Frontend:         http://localhost:5173
echo.
echo 📖 API Documentation:        http://localhost:8001/docs
echo 📊 Backend Health:           http://localhost:8001/health
echo.
echo 🎯 ARCHITECTURE: 5 specialized agents working together
echo    1. 📊 Metadata Extraction Agent (libs/icc-automation/)
echo    2. 🤖 Selenium Automation Agent (libs/icc-automation/)
echo    3. 🔗 FastAPI Integration Agent (libs/icc-automation/)
echo    4. 🧠 Evidence Analysis Agent (libs/icc-automation/)
echo    5. 🎭 Master Orchestrator (apps/agentic-ui/)
echo.
echo � TIP: Use the Master Orchestrator for optimal AI workflows!
goto end

:show_agentic
echo.
echo ✅ MASTER ORCHESTRATOR LAUNCHED!
echo ===============================
echo.
echo 🤖 Master Orchestrator:      http://localhost:8505
echo 🔥 Backend (5 agents):       http://localhost:8001
echo.
echo 🎯 All 5 specialized agents available through the orchestrator!
goto end

:show_backend
echo.
echo ✅ BACKEND WITH 5 AGENTS LAUNCHED!
echo =================================
echo.
echo 🔥 Backend API:              http://localhost:8001
echo 📖 API Documentation:        http://localhost:8001/docs
echo 📊 Backend Health:           http://localhost:8001/health
echo.
echo 🎯 Available Agents:
echo    📊 Metadata Extraction Agent
echo    🤖 Selenium Automation Agent
echo    🔗 FastAPI Integration Agent
echo    🧠 Evidence Analysis Agent
echo.
goto end

:show_frontend
echo.
echo ✅ REACT FRONTEND LAUNCHED!
echo ==========================
echo.
echo 💻 React Frontend:           http://localhost:5173
echo.
echo 🔗 Connect to backend:       http://localhost:8001
goto end

:invalid_choice
echo.
echo ❌ Invalid choice! Please enter a number between 1-6.
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye! Thank you for using ICCLexAI.
echo.
exit /b 0

:end
echo.
echo 🛡️  To stop all services, close their respective terminal windows.
echo 🔄 To restart, run this launcher again.
echo.
echo 🇰🇪 ICCLexAI - Consolidated 5-Agent Justice Through Technology
echo.
pause
