#!/usr/bin/env python3
"""
🇰🇪 ICCLexAI Complete Service Launcher
Launches all services with proper uv environment and dependency management
"""

import subprocess
import time
import requests
import os

def check_port(port):
    """Check if a port is available"""
    try:
        requests.get(f"http://localhost:{port}", timeout=1)
        return True  # Port is in use
    except Exception:
        return False  # Port is available

def launch_service(command, service_name, port=None):
    """Launch a service and return the process"""
    print(f"🚀 Starting {service_name}...")
    
    if port and check_port(port):
        print(f"⚠️  Port {port} is already in use for {service_name}")
        return None
    
    try:
        # Always use uv run to ensure proper environment
        if command.startswith('streamlit'):
            full_command = ['uv', 'run'] + command.split()
        elif command.startswith('python'):
            full_command = ['uv', 'run'] + command.split()
        else:
            full_command = command.split()
        
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        time.sleep(2)  # Give service time to start
        
        if process.poll() is None:  # Process is still running
            print(f"✅ {service_name} started successfully")
            if port:
                print(f"   📍 Running on: http://localhost:{port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {service_name} failed to start")
            print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")
        return None

def main():
    print("🇰🇪 ICCLexAI PLATFORM LAUNCHER")
    print("=" * 50)
    print("Launching all services with proper uv environment...")
    print()
    
    services = []
    
    # 1. Backend API (Priority 1)
    backend_process = launch_service(
        "python fast_api_backend.py",
        "FastAPI Backend",
        8001
    )
    if backend_process:
        services.append(("FastAPI Backend", backend_process, 8001))
    
    # Wait for backend to fully initialize
    print("⏳ Waiting for backend to initialize...")
    time.sleep(5)
    
    # 2. Main Agentic ICC App (Priority 2)
    agentic_process = launch_service(
        "streamlit run agentic_icc_app.py --server.port 8505",
        "🇰🇪 Agentic ICC Submitter",
        8505
    )
    if agentic_process:
        services.append(("Agentic ICC App", agentic_process, 8505))
    
    # 3. Fast Analysis App (Priority 3)
    fast_process = launch_service(
        "streamlit run fast_streamlit_app.py --server.port 8502",
        "⚡ Fast Analysis App",
        8502
    )
    if fast_process:
        services.append(("Fast Analysis App", fast_process, 8502))
    
    # 4. Original ICC App (Priority 4)
    original_process = launch_service(
        "streamlit run app.py --server.port 8506",
        "📋 Original ICC App",
        8506
    )
    if original_process:
        services.append(("Original ICC App", original_process, 8506))
    
    print()
    print("🎯 ICCLexAI PLATFORM STATUS")
    print("=" * 50)
    
    if services:
        for service_name, process, port in services:
            status = "✅ RUNNING" if process.poll() is None else "❌ STOPPED"
            print(f"{status} {service_name}: http://localhost:{port}")
    
    print()
    print("🇰🇪 PRIMARY SERVICES:")
    print("   🤖 AGENTIC ICC SUBMITTER: http://localhost:8505")
    print("   🔥 Backend API: http://localhost:8001")
    print("   📚 API Docs: http://localhost:8001/docs")
    print()
    print("🔧 ADDITIONAL SERVICES:")
    print("   ⚡ Fast Analysis: http://localhost:8502")
    print("   📋 Original ICC App: http://localhost:8506")
    print()
    print("✅ All services launched with uv environment!")
    print("🚀 Ready for emergency ICC evidence submissions!")
    
    try:
        print("\n⏸️  Press Ctrl+C to stop all services...")
        while True:
            time.sleep(1)
            # Check if any service died
            for service_name, process, port in services:
                if process.poll() is not None:
                    print(f"⚠️  {service_name} stopped unexpectedly")
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for service_name, process, port in services:
            if process.poll() is None:
                process.terminate()
                print(f"🔴 Stopped {service_name}")
        
        print("✅ All services stopped. ICCLexAI platform shutdown complete.")

if __name__ == "__main__":
    main()
