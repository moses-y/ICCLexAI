#!/usr/bin/env python3
"""
🇰🇪 ICC LEGAL AI - CONSOLIDATED APP LAUNCHER
Launch the intelligently merged applications after redundancy elimination.

CONSOLIDATION COMPLETE! ✨
Redundant files have been merged into comprehensive solutions.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_workspace_root():
    """Get the workspace root directory"""
    return Path(__file__).parent.parent

def launch_app(app_path, app_name, description):
    """Launch a Streamlit app with error handling"""
    print(f"\n🚀 Starting {app_name}...")
    print(f"📝 {description}")
    print(f"📂 Path: {app_path}")
    
    if not os.path.exists(app_path):
        print(f"❌ ERROR: {app_path} not found!")
        return False
    
    try:
        # Use streamlit run command
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501"]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch {app_name}: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⏹️ {app_name} stopped by user")
        return True

def main():
    """Main launcher with consolidated, intelligent apps"""
    workspace = get_workspace_root()
    
    print("=" * 80)
    print("🇰🇪 ICC LEGAL AI - CONSOLIDATED LAUNCHER")
    print("=" * 80)
    print("\n✨ INTELLIGENT CONSOLIDATION COMPLETE!")
    print("🎯 Redundant files merged into comprehensive solutions")
    print("🚀 Choose from optimized, feature-complete applications:")
    
    # Consolidated apps after intelligent merging
    apps = {
        '1': {
            'name': '🎯 THE COMPLETE MERGED SOLUTION',
            'path': workspace / 'apps' / 'agentic-ui' / 'agentic_icc_app.py',
            'description': '''Complete ICC Evidence Submission Tool with ALL best features:
       • Multi-step workflow + metadata extraction (from main_app.py)
       • Selenium automation (from app.py) 
       • FastAPI integration + analytics (from unified_icc_app.py)
       • Lightning-fast analysis (from fast_streamlit_app.py)
       • Agentic workflow automation (from agentic_processor.py)'''
        },
        '2': {
            'name': '🏛️ Legacy Simple Version',
            'path': workspace / 'apps' / 'legacy-ui' / 'app.py',
            'description': 'Original simple ICC submission tool (kept for reference)'
        },
        '3': {
            'name': '🎨 Enhanced UI Version', 
            'path': workspace / 'apps' / 'enhanced-ui' / 'enhanced_app.py',
            'description': 'Enhanced UI with improved styling and UX'
        },
        '4': {
            'name': '📊 Alternative Implementation',
            'path': workspace / 'apps' / 'icc-streamlit-app' / 'icc_streamlit_app.py',
            'description': 'Alternative ICC app with different approach'
        }
    }
    
    print("\nCONSOLIDATED APPLICATIONS:")
    print("=" * 50)
    
    for key, app in apps.items():
        print(f"\n{key}. {app['name']}")
        lines = app['description'].split('\n')
        for line in lines:
            print(f"   📝 {line.strip()}")
        status = "✅ Available" if os.path.exists(app['path']) else "❌ Not Found"
        print(f"   📍 Status: {status}")
    
    archived_path = workspace / 'apps' / 'ARCHIVED_REDUNDANT'
    print(f"\n📁 ARCHIVED REDUNDANT FILES:")
    print(f"   📂 {archived_path}/")
    if archived_path.exists():
        for file in archived_path.iterdir():
            print(f"   ├── {file.name} (merged)")
    
    print("\n" + "=" * 50)
    
    while True:
        try:
            choice = input("\n🔥 Enter your choice (1-4) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                print("👋 Goodbye!")
                break
            
            if choice in apps:
                app = apps[choice]
                print(f"\n🎯 LAUNCHING: {app['name']}")
                print("=" * 60)
                
                success = launch_app(app['path'], app['name'], app['description'])
                
                if success:
                    print(f"✅ {app['name']} completed successfully")
                else:
                    print(f"❌ {app['name']} failed to launch")
                
                print("\n" + "=" * 60)
                print("You can now launch another app or quit.")
            else:
                print("❌ Invalid choice. Please enter 1-4 or 'q' to quit.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
