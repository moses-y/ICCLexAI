#!/usr/bin/env python3
"""
ICCLexAI Development Watcher
Monitors file changes and triggers appropriate service reloads
"""

import os
import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from typing import Set

class ICCLexAIDevWatcher(FileSystemEventHandler):
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.streamlit_url = "http://localhost:8502"
        self.react_url = "http://localhost:5173"
        self.last_reload_time = {}
        self.debounce_seconds = 2  # Prevent rapid reloads
        
        # Track which services need what file types
        self.service_file_mapping = {
            'backend': {'.py', '.env', '.json'},
            'streamlit': {'.py'},
            'frontend': {'.tsx', '.ts', '.css', '.html', '.js', '.json'}
        }
        
    def should_reload(self, service: str, filepath: str) -> bool:
        """Check if we should reload based on file change and timing"""
        now = time.time()
        last_reload = self.last_reload_time.get(service, 0)
        
        if now - last_reload < self.debounce_seconds:
            return False
            
        file_ext = Path(filepath).suffix.lower()
        return file_ext in self.service_file_mapping.get(service, set())
    
    def reload_service(self, service: str, filepath: str):
        """Trigger service reload"""
        if not self.should_reload(service, filepath):
            return
            
        self.last_reload_time[service] = time.time()
        file_name = Path(filepath).name
        
        print(f"🔄 [{service.upper()}] File changed: {file_name}")
        
        try:
            if service == 'backend':
                # FastAPI auto-reloads with uvicorn --reload
                print(f"⚡ Backend auto-reload triggered by {file_name}")
                
            elif service == 'streamlit':
                # Streamlit auto-reruns with runOnSave
                print(f"📊 Streamlit auto-rerun triggered by {file_name}")
                
            elif service == 'frontend':
                # React/Vite has built-in HMR
                print(f"⚛️  React HMR triggered by {file_name}")
                
        except Exception as e:
            print(f"❌ Error reloading {service}: {e}")
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        filepath = event.src_path
        file_path = Path(filepath)
        
        # Skip hidden files, cache files, and build artifacts
        if any(part.startswith('.') for part in file_path.parts):
            return
        if file_path.name.startswith(('.', '__pycache__')):
            return
        if 'node_modules' in file_path.parts:
            return
        if '.git' in file_path.parts:
            return
            
        # Determine which services should reload
        if file_path.suffix.lower() in {'.py', '.env'}:
            if 'fast_api_backend.py' in filepath or '.env' in filepath:
                self.reload_service('backend', filepath)
            if any(name in filepath for name in ['streamlit', 'app.py']):
                self.reload_service('streamlit', filepath)
                
        elif file_path.suffix.lower() in {'.tsx', '.ts', '.css', '.html', '.js'}:
            if 'frontend' in filepath:
                self.reload_service('frontend', filepath)

def check_services_running():
    """Check if all services are running"""
    services = {
        'Backend (FastAPI)': 'http://localhost:8001/health',
        'Streamlit': 'http://localhost:8502',
        'React': 'http://localhost:5173'
    }
    
    print("🔍 Checking service status...")
    all_running = True
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ {service_name}: Running")
            else:
                print(f"⚠️  {service_name}: Responding but with status {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"❌ {service_name}: Not running")
            all_running = False
    
    return all_running

def main():
    print("🚀 ICCLexAI Development Watcher")
    print("=" * 50)
    print("Monitoring file changes for auto-reload...")
    print("Watching: Python files, TypeScript/React files, CSS, ENV files")
    print("Press Ctrl+C to stop")
    print()
    
    # Check if services are running
    if not check_services_running():
        print("\n⚠️  Some services are not running. Start them first:")
        print("   Backend:   python -m uvicorn fast_api_backend:app --reload --port 8001")
        print("   Streamlit: streamlit run fast_streamlit_app.py --server.port 8502")
        print("   React:     cd frontend && npm run dev")
        print()
    
    # Set up file watcher
    event_handler = ICCLexAIDevWatcher()
    observer = Observer()
    
    # Watch current directory and frontend
    observer.schedule(event_handler, path='.', recursive=True)
    observer.schedule(event_handler, path='./frontend', recursive=True)
    
    observer.start()
    
    print("👀 File watcher active!")
    print("🔄 All services will auto-reload on relevant file changes")
    print("=" * 50)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Development watcher stopped")
    
    observer.join()

if __name__ == "__main__":
    main()
