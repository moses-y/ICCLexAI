"""
🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM LAUNCHER
Launch script for comprehensive ICC evidence analysis with human validation

COMPONENTS:
🔹 Enhanced FastAPI backend (ALL file types)
🔹 Streamlit validation interface (Human-in-the-loop)
🔹 Test suite execution
🔹 System health monitoring
"""

import subprocess
import sys
import time
import requests
import threading
from pathlib import Path
import os

class ICCSystemLauncher:
    """Launcher for the complete ICC evidence analysis system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        self.backend_port = 8001
        self.frontend_port = 8502
        
    def check_dependencies(self):
        """Check if required packages are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'streamlit', 'requests', 
            'python-dotenv', 'pandas'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ All dependencies installed!")
        return True
    
    def check_env_variables(self):
        """Check if required environment variables are set"""
        print("\n🔑 Checking environment variables...")
        
        required_vars = ['GROQ_API_KEY', 'GOOGLE_API_KEY']
        optional_vars = ['HUGGINGFACE_TOKEN', 'ROBOFLOW_API_KEY']
        
        env_status = True
        
        for var in required_vars:
            if os.getenv(var):
                print(f"   ✅ {var}")
            else:
                print(f"   ❌ {var} (Required)")
                env_status = False
        
        for var in optional_vars:
            if os.getenv(var):
                print(f"   ✅ {var}")
            else:
                print(f"   ⚠️ {var} (Optional)")
        
        if not env_status:
            print("\n⚠️ Please set required environment variables in .env file")
            return False
        
        print("✅ Environment variables configured!")
        return True
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("\n🚀 Starting Enhanced ICC API Backend...")
        
        backend_script = self.base_dir / "apps" / "backend" / "enhanced_icc_api.py"
        
        if not backend_script.exists():
            print(f"❌ Backend script not found: {backend_script}")
            return False
        
        try:
            # Start backend process
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "apps.backend.enhanced_icc_api:app",
                "--host", "0.0.0.0",
                "--port", str(self.backend_port),
                "--reload"
            ], cwd=str(self.base_dir))
              # Wait for backend to start
            print("   ⏳ Waiting for backend to start...")
            for i in range(30):
                try:
                    response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"   ✅ Backend started successfully on port {self.backend_port}")
                        return True
                except Exception:
                    time.sleep(1)
            
            print("   ❌ Backend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"   ❌ Failed to start backend: {e}")
            return False
    
    def start_validation_interface(self):
        """Start the Streamlit validation interface"""
        print("\n🎨 Starting Validation Interface...")
        
        validation_script = self.base_dir / "apps" / "validation" / "icc_validation_interface.py"
        
        if not validation_script.exists():
            print(f"❌ Validation interface not found: {validation_script}")
            return False
        
        try:
            # Start frontend process
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                str(validation_script),
                "--server.port", str(self.frontend_port),
                "--server.address", "0.0.0.0"
            ], cwd=str(self.base_dir))
            
            # Wait for frontend to start
            print("   ⏳ Waiting for validation interface to start...")
            time.sleep(5)  # Streamlit takes a bit longer to start
            
            print(f"   ✅ Validation interface started on port {self.frontend_port}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to start validation interface: {e}")
            return False
    
    def run_system_tests(self):
        """Run comprehensive system tests"""
        print("\n🧪 Running System Tests...")
        
        test_script = self.base_dir / "test_icc_system.py"
        
        if not test_script.exists():
            print(f"❌ Test script not found: {test_script}")
            return False
        
        try:
            # Run tests in a separate thread to avoid blocking
            def run_tests():
                time.sleep(2)  # Give backend time to fully start
                subprocess.run([sys.executable, str(test_script)], cwd=str(self.base_dir))
            
            test_thread = threading.Thread(target=run_tests)
            test_thread.daemon = True
            test_thread.start()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to run tests: {e}")
            return False
    
    def display_system_info(self):
        """Display system information and access URLs"""
        print("\n" + "=" * 70)
        print("🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM - READY!")
        print("=" * 70)
        
        print("\n📡 SYSTEM ENDPOINTS:")
        print(f"   🔗 Enhanced API Backend: http://localhost:{self.backend_port}")
        print(f"   📚 API Documentation: http://localhost:{self.backend_port}/docs")
        print(f"   🎨 Validation Interface: http://localhost:{self.frontend_port}")
        
        print("\n🎯 KEY FEATURES:")
        print("   ✅ ALL ICC file types supported (documents, images, videos, audio, digital, forensic)")
        print("   ✅ Multi-agent AI analysis pipeline")
        print("   ✅ Human-in-the-loop validation with editable interface")
        print("   ✅ Professional ICC document generation")
        print("   ✅ Comprehensive batch processing")
        print("   ✅ Witness protection and consent management")
        
        print("\n📋 USAGE WORKFLOW:")
        print("   1. Open validation interface: http://localhost:8502")
        print("   2. Upload evidence files (any ICC-supported format)")
        print("   3. Review AI analysis results")
        print("   4. Edit case summary and legal analysis")
        print("   5. Complete validation checklist")
        print("   6. Submit to ICC with witness protection options")
        
        print("\n🛡️ SECURITY FEATURES:")
        print("   ✅ Witness identity protection")
        print("   ✅ Secure file handling")
        print("   ✅ Chain of custody documentation")
        print("   ✅ Consent management")
        
        print("\n🔧 DEVELOPMENT:")
        print("   📊 Real-time API testing: http://localhost:8001/docs")
        print("   🧪 System tests: python test_icc_system.py")
        print("   📁 File validation: /validate-file endpoint")
        print("   📦 Batch processing: /analyze-batch endpoint")
        
        print("\n⚠️ IMPORTANT:")
        print("   • This is a development/demo system")
        print("   • Use .env file for API keys")
        print("   • Review all AI-generated content before submission")
        print("   • Ensure witness safety and consent")
        
        print("=" * 70)
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Shutting down system...")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("   ✅ Backend stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("   ✅ Validation interface stopped")
        
        print("✅ System shutdown complete")
    
    def launch_system(self):
        """Launch the complete ICC evidence analysis system"""
        print("🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM LAUNCHER")
        print("=" * 60)
        
        try:
            # Pre-flight checks
            if not self.check_dependencies():
                return False
            
            if not self.check_env_variables():
                return False
            
            # Start services
            if not self.start_backend():
                return False
            
            if not self.start_validation_interface():
                return False
            
            # Run tests
            self.run_system_tests()
            
            # Display system information
            self.display_system_info()
            
            # Keep system running
            print("\n🔄 System running. Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ System launch failed: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Main launcher function"""
    launcher = ICCSystemLauncher()
    success = launcher.launch_system()
    
    if success:
        print("\n✅ ICC Evidence Analysis System launched successfully!")
    else:
        print("\n❌ System launch failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
