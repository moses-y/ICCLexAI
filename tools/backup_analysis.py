#!/usr/bin/env python3
"""
🔍 ICCLexAI Backup File Analysis
Analyze backup files in agentic-ui to determine if they can be safely removed
"""

import os
from pathlib import Path

def analyze_backup_files():
    """Analyze backup files in the agentic-ui directory"""
    agentic_dir = Path("d:/ICCLexAI/apps/agentic-ui")
    
    files = {
        "production": "agentic_icc_app.py",
        "backup": "agentic_icc_app_BACKUP.py", 
        "merged": "agentic_icc_app_MERGED.py"
    }
    
    print("🔍 AGENTIC UI BACKUP FILE ANALYSIS")
    print("=" * 50)
    
    for file_type, filename in files.items():
        file_path = agentic_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            lines = len(file_path.read_text(encoding='utf-8').splitlines())
            print(f"{file_type.upper()}: {filename}")
            print(f"  Size: {size:,} bytes")
            print(f"  Lines: {lines:,}")
            print(f"  Status: {'✅ KEEP' if file_type == 'production' else '❌ CANDIDATE FOR REMOVAL'}")
            print()
        else:
            print(f"{file_type.upper()}: {filename} - NOT FOUND")
    
    # Check if production file is working
    prod_path = agentic_dir / files["production"]
    if prod_path.exists():
        content = prod_path.read_text(encoding='utf-8')
        
        # Basic functionality checks
        has_imports = "import streamlit as st" in content
        has_groq = "from groq import Groq" in content or "groq" in content.lower()
        has_main_function = "def main(" in content or "if __name__" in content
        has_ui_components = "st." in content
        
        print("🔧 PRODUCTION FILE HEALTH CHECK")
        print("=" * 30)
        print(f"✅ Has Streamlit imports: {has_imports}")
        print(f"✅ Has Groq integration: {has_groq}")
        print(f"✅ Has main function: {has_main_function}")
        print(f"✅ Has UI components: {has_ui_components}")
        
        if all([has_imports, has_groq, has_main_function, has_ui_components]):
            print("🎉 Production file appears fully functional!")
            print("✅ Backup files can likely be safely removed")
        else:
            print("⚠️ Production file may have issues - keep backups for now")
    
    return files

def calculate_savings():
    """Calculate potential savings from removing backup files"""
    agentic_dir = Path("d:/ICCLexAI/apps/agentic-ui")
    
    backup_files = [
        "agentic_icc_app_BACKUP.py",
        "agentic_icc_app_MERGED.py"
    ]
    
    total_size = 0
    total_lines = 0
    
    print("\n💾 POTENTIAL SAVINGS FROM BACKUP REMOVAL")
    print("=" * 45)
    
    for filename in backup_files:
        file_path = agentic_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            lines = len(file_path.read_text(encoding='utf-8').splitlines())
            total_size += size
            total_lines += lines
            print(f"- {filename}: {size:,} bytes, {lines:,} lines")
    
    print(f"\nTOTAL SAVINGS:")
    print(f"  Files removed: {len([f for f in backup_files if (agentic_dir / f).exists()])}")
    print(f"  Disk space: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"  Code lines: {total_lines:,} lines")
    
    return total_size, total_lines

def recommend_actions():
    """Provide intelligent recommendations"""
    print("\n🎯 INTELLIGENT RECOMMENDATIONS")
    print("=" * 35)
    
    print("1. ✅ IMMEDIATE ACTIONS (Safe)")
    print("   - Remove agentic_icc_app_BACKUP.py after testing production")
    print("   - Remove agentic_icc_app_MERGED.py (redundant merge artifact)")
    print("   - Keep only agentic_icc_app.py as single source of truth")
    
    print("\n2. 🧪 VERIFICATION STEPS")
    print("   - Test all core functions in agentic_icc_app.py")
    print("   - Verify AI agents work correctly")
    print("   - Confirm form submission functionality")
    print("   - Check Groq integration and model usage")
    
    print("\n3. 🚀 ADVANCED OPTIMIZATIONS")
    print("   - Extract common components to shared-ui")
    print("   - Optimize imports and dependencies")  
    print("   - Add type hints for better maintainability")
    print("   - Create automated testing for core workflows")

def main():
    """Main analysis process"""
    print("🔍 ICCLexAI Backup File Analysis Tool")
    print("=" * 50)
    
    files = analyze_backup_files()
    total_size, total_lines = calculate_savings()
    recommend_actions()
    
    print(f"\n🎉 ANALYSIS COMPLETE")
    print(f"Ready to remove {total_size:,} bytes of redundant backup code!")

if __name__ == "__main__":
    main()
