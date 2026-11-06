@echo off
echo ========================================== 
echo ICC Legal AI Platform - System Health Check
echo International Criminal Court Evidence Analysis
echo ==========================================

echo.
echo Checking Python dependencies...
python -c "import fastapi, uvicorn, groq, redis" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Python backend dependencies: OK
) else (
    echo ❌ Python dependencies missing. Run: pip install -r requirements.txt
    pause
    exit
)

echo.
echo Checking Node.js frontend...
cd frontend
if exist node_modules (
    echo ✅ Node.js dependencies: OK
) else (
    echo ❌ Node.js dependencies missing. Run: npm install
    cd ..
    pause
    exit
)
cd ..

echo.
echo Checking environment configuration...
if exist .env (
    echo ✅ Environment file: Found
) else (
    echo ❌ .env file missing. Create with your API keys.
    pause
    exit
)

echo.
echo ==========================================
echo 🚀 ICC Legal AI Platform Ready for Launch!
echo ==========================================
echo Backend: FastAPI + Groq + Redis
echo Frontend: TypeScript + React + ShadCN
echo AI Models: DeepSeek R1, Llama 3.3, Whisper
echo ==========================================

echo.
choice /c YN /m "Launch the complete ICC Evidence AI platform now"
if %errorlevel% equ 1 (
    echo.
    echo Starting ICC Evidence AI Platform...
    call launch_full_stack.bat
) else (
    echo Setup complete. Run launch_full_stack.bat when ready.
)

pause
