@echo off
REM 🇰🇪 ICCLexAI OPTIMIZED CONSOLIDATED LAUNCHER
REM Launches the NEW 5-agent architecture after June 2025 consolidation
REM Author: ICCLexAI Consolidation Team | Date: June 18, 2025

title ICCLexAI - Consolidated 5-Agent Platform

color 0A
echo.
echo ============================================================================
echo   🇰🇪 ICCLexAI - CONSOLIDATED 5-AGENT AI PLATFORM (Post-Consolidation)
echo ============================================================================
echo   🤖 Master Orchestrator  │  📊 Evidence Analysis  │  🔧 Automation Agents
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
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8505"') do taskkill /PID %%a /F >nul 2>&1
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

REM Display menu for consolidated architecture
echo 🎯 CONSOLIDATED 5-AGENT LAUNCH OPTIONS:
echo.
echo [1] 🚀 FULL PLATFORM      - Master Orchestrator + Backend + Frontend
echo [2] 🤖 MASTER ORCHESTRATOR - Main agentic workflow (apps/agentic-ui/)
echo [3] 🔧 BACKEND API        - FastAPI + 4 specialized agents
echo [4] 💻 REACT FRONTEND     - Modern TypeScript interface
echo [5] 🔬 DEVELOPMENT MODE   - All services with debug logging
echo [6] 🧪 AGENT TESTING      - Test individual agents
echo [7] ❌ EXIT
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto full_platform
if "%choice%"=="2" goto master_orchestrator
if "%choice%"=="3" goto backend_only
if "%choice%"=="4" goto frontend_only
if "%choice%"=="5" goto development
if "%choice%"=="6" goto agent_testing
if "%choice%"=="7" goto exit
goto invalid_choice

:full_platform
echo.
echo 🚀 LAUNCHING CONSOLIDATED FULL PLATFORM...
echo ==========================================
echo.

echo 🔥 [1/3] Starting Consolidated Backend (5 agents)...
start "ICCLexAI-Backend" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 4 /nobreak > nul

echo 🤖 [2/3] Starting Master Orchestrator...
start "ICCLexAI-Orchestrator" cmd /k "cd apps/agentic-ui && uv run streamlit run agentic_icc_app.py --server.port 8505 --server.headless false"
timeout /t 3 /nobreak > nul

echo 💻 [3/3] Starting React Frontend...
start "ICCLexAI-Frontend" cmd /k "cd apps/frontend && npm run dev"

goto show_full_platform

:master_orchestrator
echo.
echo 🤖 LAUNCHING MASTER ORCHESTRATOR ONLY...
echo =======================================
echo.
echo 🔥 Starting Backend (required for orchestrator)...
start "ICCLexAI-Backend" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 4 /nobreak > nul

echo 🤖 Starting Master Orchestrator...
start "ICCLexAI-Orchestrator" cmd /k "cd apps/agentic-ui && uv run streamlit run agentic_icc_app.py --server.port 8505 --server.headless false"
goto show_orchestrator

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
echo    - 📋 Master Orchestrator API
echo.
start "ICCLexAI-Backend" cmd /k "cd apps/backend && uv run uvicorn fast_api_backend:app --host 0.0.0.0 --port 8001 --reload"
goto show_backend

:frontend_only
echo.
echo 💻 LAUNCHING REACT FRONTEND ONLY...
echo ==================================
echo.
echo 💻 Starting Modern React Frontend...
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

echo 🤖 [2/3] Starting Orchestrator with debug...
start "ICCLexAI-Orchestrator-Dev" cmd /k "cd apps/agentic-ui && uv run streamlit run agentic_icc_app.py --server.port 8505 --server.headless false --logger.level debug"
timeout /t 3 /nobreak > nul

echo 💻 [3/3] Starting Frontend with dev tools...
start "ICCLexAI-Frontend-Dev" cmd /k "cd apps/frontend && npm run dev"

echo 🔍 Opening agent monitoring...
start "Agent-Monitor" cmd /k "echo === 5-AGENT MONITORING === && echo 1. Metadata Extraction Agent && echo 2. Selenium Automation Agent && echo 3. FastAPI Integration Agent && echo 4. Evidence Analysis Agent && echo 5. Master Orchestrator && echo === Check http://localhost:8001/docs for API === && pause"

goto show_full_platform

:agent_testing
echo.
echo 🧪 AGENT TESTING MODE...
echo ======================
echo.
echo Testing individual agents in the consolidated architecture:
echo.
echo [A] Test Metadata Extraction Agent
echo [B] Test Selenium Automation Agent  
echo [C] Test FastAPI Integration Agent
echo [D] Test Evidence Analysis Agent
echo [E] Test Master Orchestrator
echo [F] Return to main menu
echo.

set /p agent_choice="Choose agent to test (A-F): "

if /i "%agent_choice%"=="A" goto test_metadata
if /i "%agent_choice%"=="B" goto test_selenium
if /i "%agent_choice%"=="C" goto test_fastapi
if /i "%agent_choice%"=="D" goto test_evidence
if /i "%agent_choice%"=="E" goto test_orchestrator
if /i "%agent_choice%"=="F" goto menu
goto agent_testing

:test_metadata
echo.
echo 📊 Testing Metadata Extraction Agent...
start "Test-Metadata" cmd /k "cd libs/icc-automation && uv run python -c \"from metadata_extraction_agent import *; print('Metadata agent loaded successfully')\""
goto agent_testing

:test_selenium
echo.
echo 🤖 Testing Selenium Automation Agent...
start "Test-Selenium" cmd /k "cd libs/icc-automation && uv run python -c \"from selenium_automation_agent import *; print('Selenium agent loaded successfully')\""
goto agent_testing

:test_fastapi
echo.
echo 🔗 Testing FastAPI Integration Agent...
start "Test-FastAPI" cmd /k "cd libs/icc-automation && uv run python -c \"from fastapi_integration_agent import *; print('FastAPI agent loaded successfully')\""
goto agent_testing

:test_evidence
echo.
echo 🧠 Testing Evidence Analysis Agent...
start "Test-Evidence" cmd /k "cd libs/icc-automation && uv run python -c \"from evidence_analysis_agent import *; print('Evidence agent loaded successfully')\""
goto agent_testing

:test_orchestrator
echo.
echo 🎭 Testing Master Orchestrator...
start "Test-Orchestrator" cmd /k "cd apps/agentic-ui && uv run python -c \"import agentic_icc_app; print('Orchestrator loaded successfully')\""
goto agent_testing

:show_full_platform
echo.
echo ✅ CONSOLIDATED ICCLEXAI PLATFORM LAUNCHED!
echo ==========================================
echo.
echo 🇰🇪 CONSOLIDATED SERVICES:
echo    🤖 Master Orchestrator:    http://localhost:8505
echo    🔥 Backend (5 agents):     http://localhost:8001  
echo    💻 React Frontend:         http://localhost:5173
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
echo 💡 TIP: Use the Master Orchestrator for optimal AI-powered workflows!
goto end

:show_orchestrator
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
echo ❌ Invalid choice! Please enter a number between 1-7.
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye! Thank you for using ICCLexAI Consolidated Platform.
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

:menu
goto :eof
