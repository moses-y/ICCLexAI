#!/usr/bin/env python3
"""
🇰🇪 ICCLexAI Specialized Apps Launcher
Demonstrates the specialized workflow chaining approach
Shows how app.py's multi-step pattern informs the agentic workflow
"""

import subprocess
import time
import requests
import os
import sys
from pathlib import Path

def print_banner():
    """Print ICCLexAI banner"""
    print("=" * 80)
    print("🇰🇪 ICCLexAI SPECIALIZED APPS LAUNCHER")
    print("=" * 80)
    print("Specialized workflow chaining for ICC evidence submission")
    print("Based on app.py's proven multi-step approach with AI enhancements")
    print()

def check_environment():
    """Check environment setup"""
    print("🔧 Environment Check:")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"✅ Python: {python_version}")
    
    # Check key dependencies
    try:
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit: Not installed")
    
    try:
        import groq
        print(f"✅ Groq: {groq.__version__}")
    except ImportError:
        print("❌ Groq: Not installed")
    
    # Check environment variables
    env_vars = {
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'HUGGINGFACE_TOKEN': os.getenv('HUGGINGFACE_TOKEN')
    }
    
    print("\\n🔑 Environment Variables:")
    for var, value in env_vars.items():
        status = "✅ Set" if value else "❌ Not set"
        print(f"{status} {var}")
    
    print()

def check_port(port):
    """Check if a port is available"""
    try:
        requests.get(f"http://localhost:{port}", timeout=1)
        return True
    except Exception:
        return False

def launch_app(app_name, script_path, port, description):
    """Launch a specialized ICC app"""
    print(f"🚀 Starting {app_name}...")
    print(f"   📄 Script: {script_path}")
    print(f"   🌐 Port: {port}")
    print(f"   📝 Description: {description}")
    
    if check_port(port):
        print(f"⚠️  Port {port} already in use for {app_name}")
        return None
    
    try:
        # Use uv run for proper environment
        command = [
            'uv', 'run', 'streamlit', 'run', script_path,
            '--server.port', str(port),
            '--server.headless', 'true',
            '--server.enableCORS', 'false'
        ]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        time.sleep(3)  # Give app time to start
        
        if process.poll() is None:
            print(f"✅ {app_name} started successfully")
            print(f"   🌐 URL: http://localhost:{port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {app_name} failed to start")
            print(f"   Error: {stderr.decode()[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {app_name}: {e}")
        return None

def main():
    """Main launcher with specialized app demonstration"""
    print_banner()
    check_environment()
    
    print("🎯 SPECIALIZED ICC APPS WORKFLOW")
    print("=" * 80)
    print()
    print("This launcher demonstrates how app.py's multi-step approach")
    print("informs our specialized agentic workflow chaining:")
    print()
    print("1. 📋 LEGACY APP (app.py) - Original multi-step workflow")
    print("2. 🤖 AGENTIC APP - Enhanced with AI workflow chain")
    print("3. ⚡ FAST ANALYSIS - Speed-optimized for quick analysis")
    print("4. 🏗️ UNIFIED PLATFORM - All features combined")
    print("5. 🚀 ENHANCED UI - Multi-step with agentic enhancement")
    print()
    
    # Define specialized apps
    apps = [
        {
            'name': '📋 Legacy Multi-Step App (app.py)',
            'script': 'apps/legacy-ui/app.py',
            'port': 8506,
            'description': 'Original proven multi-step workflow pattern'
        },
        {
            'name': '🤖 Agentic ICC Submitter',
            'script': 'apps/agentic-ui/agentic_icc_app.py', 
            'port': 8505,
            'description': 'AI-enhanced workflow with intelligent phases'
        },
        {
            'name': '⚡ Fast Analysis App',
            'script': 'apps/analysis-ui/fast_streamlit_app.py',
            'port': 8502,
            'description': 'Speed-optimized for rapid evidence analysis'
        },
        {
            'name': '🏗️ Unified ICC Platform',
            'script': 'apps/unified_icc_app.py',
            'port': 8503,
            'description': 'Comprehensive platform with all features'
        },
        {
            'name': '🚀 Enhanced Multi-Step UI',
            'script': 'apps/enhanced-ui/enhanced_app.py',
            'port': 8504,
            'description': 'Multi-step approach with agentic AI chain'
        }
    ]
    
    print("🚀 LAUNCHING SPECIALIZED APPS:")
    print("-" * 50)
    
    launched_apps = []
    
    for app in apps:
        if os.path.exists(app['script']):
            process = launch_app(
                app['name'], 
                app['script'], 
                app['port'], 
                app['description']
            )
            if process:
                launched_apps.append((app['name'], process, app['port']))
        else:
            print(f"❌ Script not found: {app['script']}")
        
        print()
    
    # Also start the backend if available
    backend_script = 'apps/backend/fast_api_backend.py'
    if os.path.exists(backend_script):
        print("🔥 Starting Backend API...")
        try:
            backend_process = subprocess.Popen([
                'uv', 'run', 'python', backend_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)
            if backend_process.poll() is None:
                print("✅ Backend API started on http://localhost:8001")
                launched_apps.append(("🔥 Backend API", backend_process, 8001))
            else:
                print("❌ Backend API failed to start")
        except Exception as e:
            print(f"❌ Backend error: {e}")
    
    print("\\n" + "=" * 80)
    print("🎯 ICCLexAI SPECIALIZED APPS STATUS")
    print("=" * 80)
    
    if launched_apps:
        print("\\n✅ RUNNING APPLICATIONS:")
        for app_name, process, port in launched_apps:
            status = "🟢 RUNNING" if process.poll() is None else "🔴 STOPPED"
            print(f"{status} {app_name}: http://localhost:{port}")
        
        print("\\n🔗 WORKFLOW DEMONSTRATION:")
        print("1. Start with 📋 Legacy App (port 8506) - See original multi-step pattern")
        print("2. Compare with 🤖 Agentic App (port 8505) - AI-enhanced workflow")
        print("3. Use ⚡ Fast Analysis (port 8502) - For quick evidence processing")
        print("4. Explore 🏗️ Unified Platform (port 8503) - All features combined")
        print("5. Try 🚀 Enhanced UI (port 8504) - Multi-step with AI chaining")
        
        print("\\n💡 KEY INSIGHTS FROM APP.PY INTEGRATION:")
        print("• Multi-step workflow prevents user overwhelm")
        print("• Session state management for complex workflows")
        print("• Progressive disclosure of functionality")
        print("• AI analysis integrated into familiar patterns")
        print("• Form generation based on accumulated evidence")
        
        print("\\n🤖 AGENTIC WORKFLOW ENHANCEMENTS:")
        print("• Intelligent phase transitions")
        print("• Contextual AI guidance")
        print("• Automated form population")
        print("• Legal relevance scoring")
        print("• Evidence relationship analysis")
        
    else:
        print("❌ No applications started successfully")
        print("\\n🔧 TROUBLESHOOTING:")
        print("1. Check that 'uv' is installed and available")
        print("2. Ensure all dependencies are installed (uv sync)")
        print("3. Verify environment variables are set")
        print("4. Check that ports are not in use by other services")
        return
    
    print("\\n" + "=" * 80)
    print("🇰🇪 ICCLexAI: READY FOR EMERGENCY ICC SUBMISSIONS")
    print("=" * 80)
    
    try:
        print("\\n⏸️  Press Ctrl+C to stop all applications...")
        while True:
            time.sleep(1)
            # Check if any app died
            for app_name, process, port in launched_apps:
                if process.poll() is not None:
                    print(f"⚠️  {app_name} stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\\n\\n🛑 Stopping all applications...")
        for app_name, process, port in launched_apps:
            if process.poll() is None:
                process.terminate()
                print(f"🔴 Stopped {app_name}")
        
        print("\\n✅ All applications stopped.")
        print("🇰🇪 ICCLexAI specialized apps shutdown complete.")
        print("\\n💡 Summary of Multi-Step Workflow Benefits:")
        print("• User-friendly progressive workflow")
        print("• AI enhancement without complexity")
        print("• Specialized apps for different use cases")
        print("• Shared core functionality eliminates duplication")
        print("• Environment variables for deployment readiness")

if __name__ == "__main__":
    main()
