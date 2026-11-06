#!/usr/bin/env python3
"""
🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM LAUNCHER
Comprehensive orchestrated workflow launcher for the ICC Evidence Analysis System
"""

import subprocess
import time
import requests
import sys
import signal
from datetime import datetime
from typing import List, Dict, Any
import socket

class ICCSystemLauncher:
    """Orchestrated launcher for the complete ICC system"""
    
    def __init__(self):
        self.services: List[Dict[str, Any]] = []
        self.running = True
        
        # Service definitions
        self.service_configs = [
            {
                "name": "ICC Context Engine API",
                "command": ["python", "apps/backend/icc_context_api.py"],
                "port": 8002,
                "health_url": "http://localhost:8002/api/health",
                "startup_delay": 3,
                "required": True
            },
            {
                "name": "React Frontend",
                "command": ["npm", "run", "dev"],
                "cwd": "apps/frontend",
                "port": 5173,
                "health_url": "http://localhost:5173",
                "startup_delay": 5,
                "required": True
            }
        ]
    
    def print_banner(self):
        """Print startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM - ORCHESTRATED LAUNCHER     ║
║                                                                  ║
║  🔹 Context Engine API (Port 8002)                              ║
║  🔹 React Validation Frontend (Port 5173)                       ║
║                                                                  ║
║  Human-in-the-Loop ICC Case Building & Submission               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🕒 Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    def check_port_availability(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex(('localhost', port)) != 0
        except Exception:
            return True
    
    def start_service(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a single service"""
        service_name = config["name"]
        port = config.get("port")
        
        print(f"🚀 Starting {service_name}...")
        
        # Check port availability
        if port and not self.check_port_availability(port):
            print(f"⚠️  Port {port} is already in use. Service may already be running.")
            if not config.get("required", True):
                return {"name": service_name, "status": "skipped", "process": None}
        
        try:
            # Setup process arguments
            kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "bufsize": 1,
                "universal_newlines": True
            }
            
            if config.get("cwd"):
                kwargs["cwd"] = config["cwd"]
            
            # Start the process
            process = subprocess.Popen(config["command"], **kwargs)
            
            # Wait for startup
            startup_delay = config.get("startup_delay", 2)
            print(f"⏳ Waiting {startup_delay}s for {service_name} to start...")
            time.sleep(startup_delay)
            
            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ {service_name} failed to start")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return {"name": service_name, "status": "failed", "process": None}
            
            print(f"✅ {service_name} started successfully (PID: {process.pid})")
            
            return {
                "name": service_name,
                "status": "running",
                "process": process,
                "port": port,
                "health_url": config.get("health_url")
            }
            
        except Exception as e:
            print(f"❌ Failed to start {service_name}: {e}")
            return {"name": service_name, "status": "error", "process": None}
    
    def health_check(self, service: Dict[str, Any]) -> bool:
        """Perform health check on a service"""
        health_url = service.get("health_url")
        if not health_url:
            return True  # Assume healthy if no health check URL
        
        try:
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_all_services(self):
        """Start all configured services"""
        print("🔄 Starting all ICC system services...")
        print()
        
        for config in self.service_configs:
            service = self.start_service(config)
            self.services.append(service)
            print()
        
        # Summary
        running_services = [s for s in self.services if s["status"] == "running"]
        failed_services = [s for s in self.services if s["status"] in ["failed", "error"]]
        
        print("=" * 70)
        print("📊 Service Status Summary:")
        print(f"   ✅ Running: {len(running_services)}")
        print(f"   ❌ Failed: {len(failed_services)}")
        print(f"   ⏭️  Skipped: {len(self.services) - len(running_services) - len(failed_services)}")
        print()
        
        if running_services:
            print("🌐 Access URLs:")
            for service in running_services:
                if service.get("port"):
                    print(f"   • {service['name']}: http://localhost:{service['port']}")
            print()
        
        return len(running_services) > 0
    
    def test_system_integration(self):
        """Test system integration"""
        print("🧪 Testing system integration...")
        
        tests = [
            {
                "name": "Context Engine Health",
                "url": "http://localhost:8002/api/health",
                "expected_keys": ["status", "context_engine_available"]
            },
            {
                "name": "Frontend Accessibility",
                "url": "http://localhost:5173",
                "check_type": "accessibility"
            }
        ]
        
        passed = 0
        for test in tests:
            try:
                if test.get("check_type") == "accessibility":
                    response = requests.get(test["url"], timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ {test['name']}: Accessible")
                        passed += 1
                    else:
                        print(f"   ❌ {test['name']}: HTTP {response.status_code}")
                else:
                    response = requests.get(test["url"], timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if all(key in data for key in test.get("expected_keys", [])):
                            print(f"   ✅ {test['name']}: Passed")
                            passed += 1
                        else:
                            print(f"   ⚠️  {test['name']}: Missing expected keys")
                    else:
                        print(f"   ❌ {test['name']}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {test['name']}: {e}")
        
        print(f"📊 Integration Tests: {passed}/{len(tests)} passed")
        print()
        
        return passed == len(tests)
    
    def show_usage_instructions(self):
        """Show usage instructions"""
        print("📖 USAGE INSTRUCTIONS:")
        print()
        print("🔹 ICC Validation Dashboard:")
        print("   • Open: http://localhost:5173")
        print("   • Click 'Initialize New ICC Case' to start")
        print("   • Upload evidence files for analysis")
        print("   • Review and edit AI-generated summaries")
        print("   • Complete validation checklist")
        print("   • Generate final ICC submission document")
        print()
        print("🔹 API Endpoints (Context Engine):")
        print("   • Health Check: GET http://localhost:8002/api/health")
        print("   • Create Session: POST http://localhost:8002/api/session/create")
        print("   • Upload Evidence: POST http://localhost:8002/api/session/{id}/evidence/upload")
        print("   • Update Validation: POST http://localhost:8002/api/session/{id}/validation/update")
        print()
        print("🔹 Keyboard Shortcuts:")
        print("   • Ctrl+C: Graceful shutdown")
        print()
    
    def shutdown_services(self):
        """Gracefully shutdown all services"""
        print("\n🔄 Shutting down ICC system services...")
        self.running = False
        
        for service in self.services:
            if service["status"] == "running" and service["process"]:
                try:
                    print(f"🔌 Stopping {service['name']}...")
                    service["process"].terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        service["process"].wait(timeout=5)
                        print(f"✅ {service['name']} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        print(f"⚠️  Force killing {service['name']}...")
                        service["process"].kill()
                        service["process"].wait()
                        print(f"❌ {service['name']} force stopped")
                        
                except Exception as e:
                    print(f"❌ Error stopping {service['name']}: {e}")
        
        print("🏁 All services stopped. Goodbye!")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n⚡ Received signal {signum}")
        self.shutdown_services()
        sys.exit(0)
    
    def run(self):
        """Run the complete ICC system"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Print banner
            self.print_banner()
            
            # Start services
            if not self.start_all_services():
                print("❌ Failed to start required services. Exiting.")
                return 1
            
            # Test integration
            print("⏳ Waiting for services to fully initialize...")
            time.sleep(5)
            self.test_system_integration()
            
            # Show instructions
            self.show_usage_instructions()
            
            # Keep running
            print("🎯 ICC Evidence Analysis System is ready!")
            print("   Press Ctrl+C to shutdown gracefully")
            print("=" * 70)
            
            # Wait for shutdown signal
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⚡ Keyboard interrupt received")
        except Exception as e:
            print(f"❌ System error: {e}")
        finally:
            self.shutdown_services()
        
        return 0

def main():
    """Main entry point"""
    launcher = ICCSystemLauncher()
    return launcher.run()

if __name__ == "__main__":
    sys.exit(main())
