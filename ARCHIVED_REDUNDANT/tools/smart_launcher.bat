@echo off
echo ==========================================
echo ICC Legal AI Platform - Smart Launcher
echo ==========================================
echo.

REM Kill existing processes on our ports
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5174"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak > nul

echo.
echo 🚀 Starting all services in coordinated manner...
echo.

REM Create a single PowerShell session to manage all processes
powershell -Command "& {
    Write-Host '🔥 [1/3] Starting FastAPI Backend with proper reload...' -ForegroundColor Green
    $backend = Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m', 'uvicorn', 'fast_api_backend:app', '--host', '0.0.0.0', '--port', '8000', '--reload' -PassThru -WindowStyle Hidden
    
    Start-Sleep -Seconds 3
    
    Write-Host '📊 [2/3] Starting Streamlit UI...' -ForegroundColor Blue  
    $streamlit = Start-Process -FilePath '.\.venv\Scripts\streamlit.exe' -ArgumentList 'run', 'fast_streamlit_app.py', '--server.port', '8501', '--server.headless', 'true' -PassThru -WindowStyle Hidden
    
    Start-Sleep -Seconds 2
    
    Write-Host '⚛️  [3/3] Starting React Development Server...' -ForegroundColor Cyan
    $react = Start-Process -FilePath 'npm' -ArgumentList 'run', 'dev', '--', '--port', '5173' -WorkingDirectory '.\frontend' -PassThru -WindowStyle Hidden
    
    Start-Sleep -Seconds 3
    
    Write-Host ''
    Write-Host '=================================' -ForegroundColor Yellow
    Write-Host '🎯 All Services Running!' -ForegroundColor Yellow
    Write-Host '=================================' -ForegroundColor Yellow
    Write-Host '🔥 Backend API:    http://localhost:8000' -ForegroundColor Green
    Write-Host '📚 API Docs:       http://localhost:8000/docs' -ForegroundColor Green
    Write-Host '📊 Streamlit UI:   http://localhost:8501' -ForegroundColor Blue
    Write-Host '⚛️  React UI:       http://localhost:5173' -ForegroundColor Cyan
    Write-Host '=================================' -ForegroundColor Yellow
    Write-Host ''
    Write-Host '🔍 Process Monitor Active (Ctrl+C to stop)' -ForegroundColor White
    Write-Host ''
    
    # Monitor processes
    try {
        while ($true) {
            if ($backend.HasExited) { 
                Write-Host '❌ Backend stopped!' -ForegroundColor Red 
                $backend = Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m', 'uvicorn', 'fast_api_backend:app', '--host', '0.0.0.0', '--port', '8000', '--reload' -PassThru -WindowStyle Hidden
                Write-Host '🔄 Backend restarted' -ForegroundColor Green
            }
            if ($streamlit.HasExited) { 
                Write-Host '❌ Streamlit stopped!' -ForegroundColor Red 
                $streamlit = Start-Process -FilePath '.\.venv\Scripts\streamlit.exe' -ArgumentList 'run', 'fast_streamlit_app.py', '--server.port', '8501', '--server.headless', 'true' -PassThru -WindowStyle Hidden
                Write-Host '🔄 Streamlit restarted' -ForegroundColor Blue
            }
            if ($react.HasExited) { 
                Write-Host '❌ React stopped!' -ForegroundColor Red 
                $react = Start-Process -FilePath 'npm' -ArgumentList 'run', 'dev', '--', '--port', '5173' -WorkingDirectory '.\frontend' -PassThru -WindowStyle Hidden
                Write-Host '🔄 React restarted' -ForegroundColor Cyan
            }
            Start-Sleep -Seconds 2
        }
    }
    catch {
        Write-Host ''
        Write-Host '🛑 Shutting down all services...' -ForegroundColor Yellow
        Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
        Stop-Process -Id $streamlit.Id -Force -ErrorAction SilentlyContinue  
        Stop-Process -Id $react.Id -Force -ErrorAction SilentlyContinue
        Write-Host '✅ All services stopped cleanly!' -ForegroundColor Green
    }
}"

echo.
echo Press any key to continue...
pause
