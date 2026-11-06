#!/usr/bin/env python3
"""
ICC Legal AI Platform - Smart Process Manager
Single-terminal launcher with proper process management and port handling
"""

import subprocess
import time
import os
import sys
import socket
from pathlib import Path

class SmartLauncher:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.venv_python = self.base_dir / ".venv" / "Scripts" / "python.exe"
        self.venv_streamlit = self.base_dir / ".venv" / "Scripts" / "streamlit.exe"
        
    def check_port(self, port):
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def find_free_port(self, start_port, max_attempts=10):
        """Find the next available port starting from start_port"""
        for i in range(max_attempts):
            port = start_port + i
            if self.check_port(port):
                return port
        raise Exception(f"No free ports found starting from {start_port}")
    
    def kill_existing_processes(self):
        """Kill any existing processes on our target ports"""
        ports_to_check = [8000, 8501, 5173, 5174]
        
        for port in ports_to_check:
            try:
                # Windows netstat to find process using port
                result = subprocess.run(
                    f'netstat -ano | findstr ":{port}"',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    # Extract PID and kill it
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            pid = line.split()[-1]
                            try:
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                                print(f"✅ Killed existing process on port {port} (PID: {pid})")
                            except subprocess.SubprocessError:
                                pass
            except (subprocess.SubprocessError, OSError):
                pass
    
    def start_backend(self):
        """Start FastAPI backend with proper reload"""
        backend_port = self.find_free_port(8000)
        
        print(f"🚀 Starting FastAPI Backend on port {backend_port}...")
        
        # Use uvicorn with proper module import for reload
        cmd = [
            str(self.venv_python), "-m", "uvicorn", 
            "fast_api_backend:app",
            "--host", "0.0.0.0",
            "--port", str(backend_port),
            "--reload",
            "--reload-dir", str(self.base_dir)
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(self.base_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        self.processes.append(('Backend', process, backend_port))
        return backend_port
    
    def start_streamlit(self):
        """Start Streamlit UI"""
        streamlit_port = self.find_free_port(8501)
        
        print(f"📊 Starting Streamlit UI on port {streamlit_port}...")
        
        cmd = [
            str(self.venv_streamlit), "run", 
            str(self.base_dir / "fast_streamlit_app.py"),
            "--server.port", str(streamlit_port),
            "--server.headless", "true",
            "--server.fileWatcherType", "none"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(self.base_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        self.processes.append(('Streamlit', process, streamlit_port))
        return streamlit_port
    
    def start_react(self):
        """Start React development server"""
        react_port = self.find_free_port(5173)
        
        print(f"⚛️  Starting React UI on port {react_port}...")
        
        # Set environment variable for Vite port
        env = os.environ.copy()
        env['PORT'] = str(react_port)
        
        cmd = ["npm", "run", "dev", "--", "--port", str(react_port)]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(self.base_dir / "frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        
        self.processes.append(('React', process, react_port))
        return react_port
    
    def monitor_processes(self):
        """Monitor all processes and display status"""
        print("\n" + "="*60)
        print("🎯 ICC Legal AI Platform - All Services Running!")
        print("="*60)
        
        for name, process, port in self.processes:
            if name == 'Backend':
                print(f"🔥 {name:10}: http://localhost:{port}")
                print(f"📚 API Docs:    http://localhost:{port}/docs")
            elif name == 'Streamlit':
                print(f"📊 {name:10}: http://localhost:{port}")
            elif name == 'React':
                print(f"⚛️  {name:10}: http://localhost:{port}")
        
        print("="*60)
        print("🔍 Live Process Monitor (Ctrl+C to stop all)")
        print("="*60)
        
        try:
            while True:
                all_running = True
                for name, process, port in self.processes:
                    if process.poll() is not None:
                        print(f"❌ {name} stopped unexpectedly!")
                        all_running = False
                
                if not all_running:
                    print("⚠️  Some processes stopped. Restarting...")
                    self.restart_failed()
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down all services...")
            self.cleanup()
    
    def restart_failed(self):
        """Restart any failed processes"""
        new_processes = []
        for name, process, port in self.processes:
            if process.poll() is not None:
                print(f"🔄 Restarting {name}...")
                if name == 'Backend':
                    new_port = self.start_backend()
                elif name == 'Streamlit':
                    new_port = self.start_streamlit()
                elif name == 'React':
                    new_port = self.start_react()
            else:
                new_processes.append((name, process, port))
        
        self.processes = new_processes
    
    def cleanup(self):
        """Clean shutdown of all processes"""
        for name, process, port in self.processes:
            try:
                print(f"🔄 Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"⚡ Force killing {name}...")
                process.kill()
            except:
                pass
        
        print("✅ All services stopped cleanly!")
    
    def run(self):
        """Main execution flow"""
        print("🚀 ICC Legal AI Platform - Smart Launcher")
        print("="*50)
        
        # Clean up any existing processes
        print("🧹 Cleaning up existing processes...")
        self.kill_existing_processes()
        time.sleep(2)
        
        # Start all services
        try:
            backend_port = self.start_backend()
            time.sleep(3)  # Give backend time to start
            
            streamlit_port = self.start_streamlit()
            time.sleep(2)
            
            react_port = self.start_react()
            time.sleep(3)
            
            # Monitor everything
            self.monitor_processes()
            
        except Exception as e:
            print(f"❌ Error during startup: {e}")
            self.cleanup()
            sys.exit(1)

if __name__ == "__main__":
    launcher = SmartLauncher()
    launcher.run()
