#!/usr/bin/env python3
"""
RentalAI Backend Setup Script
Run this script to set up the FastAPI backend
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_step(step_num, description):
    """Print formatted step"""
    print(f"\n{'='*50}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*50}")

def run_command(command, description, check=True):
    """Run shell command with error handling"""
    print(f"\n[RUNNING] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[SUCCESS] {description} completed")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"[ERROR] {description} failed")
            if result.stderr:
                print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERROR] Python 3.8+ is required")
        return False
    print(f"[INFO] Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_environment():
    """Set up virtual environment and install dependencies"""
    print_step(1, "Setting up Python environment")
    
    if not check_python_version():
        return False
    
    # Create virtual environment
    run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = ".\\venv\\Scripts\\activate"
        pip_cmd = ".\\venv\\Scripts\\pip"
    else:  # Unix/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "./venv/bin/pip"
    
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    
    return True

def setup_environment_file():
    """Create .env file from template"""
    print_step(2, "Setting up environment variables")
    
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("[INFO] .env file already exists")
        return True
    
    if env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("[SUCCESS] Created .env file from template")
        print("[WARNING] Update the .env file with your actual API keys and configuration")
        return True
    else:
        print("[ERROR] env_example.txt not found")
        return False

def check_supabase_connection():
    """Test Supabase connection"""
    print_step(3, "Testing Supabase connection")
    
    try:
        from app.core.supabase_client import supabase_client
        
        result = supabase_client.table("users").select("count").execute()
        print("[SUCCESS] Supabase connection established")
        return True
    except Exception as e:
        print(f"[ERROR] Supabase connection failed: {e}")
        print("[WARNING] Check your Supabase credentials in .env file")
        return False

def initialize_database():
    """Initialize database schema"""
    print_step(4, "Initializing database schema")
    
    try:
        from app.core.database import init_db
        import asyncio
        
        asyncio.run(init_db())
        print("[SUCCESS] Database initialized")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

def test_ai_services():
    """Test AI service configuration"""
    print_step(5, "Testing AI services")
    
    try:
        from app.services.ai_service import ai_service
        
        # Test AI service initialization
        has_openai = ai_service.openai_client is not None
        has_anthropic = ai_service.anthropic_client is not None
        
        if has_openai:
            print("[SUCCESS] OpenAI service configured")
        else:
            print("[WARNING] OpenAI API key not found, AI features will use fallback")
        
        if has_anthropic:
            print("[SUCCESS] Anthropic service configured")
        else:
            print("[WARNING] Anthropic API key not found, using OpenAI as primary")
        
        if not has_openai and not has_anthropic:
            print("[WARNING] No AI services configured, descriptions will use templates")
        
        return True
    except Exception as e:
        print(f"[ERROR] AI service test failed: {e}")
        return False

def test_storage_service():
    """Test S3 storage configuration"""
    print_step(6, "Testing S3 storage service")
    
    try:
        from app.services.storage_service import storage_service
        
        if storage_service.s3_client:
            print("[SUCCESS] S3 storage service configured")
        else:
            print("[WARNING] S3 credentials not found, file uploads will be disabled")
        
        return True
    except Exception as e:
        print(f"[ERROR] Storage service test failed: {e}")
        return False

def create_run_script():
    """Create convenient run script"""
    print_step(7, "Creating run scripts")
    
    # Create run script for Unix/macOS
    run_script_unix = """#!/bin/bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""
    
    with open("run.sh", "w") as f:
        f.write(run_script_unix)
    
    os.chmod("run.sh", 0o755)
    
    run_script_windows = """@echo off
call venv\\Scripts\\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""
    
    with open("run.bat", "w") as f:
        f.write(run_script_windows)
    
    print("[SUCCESS] Created run.sh and run.bat")
    return True

def main():
    """Main setup function"""
    print("Krib Host Dashboard Backend Setup")
    print("Setting up FastAPI backend environment")
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    success = True
    
    success &= setup_environment()
    success &= setup_environment_file()
    success &= check_supabase_connection()
    success &= initialize_database()
    success &= test_ai_services()
    success &= test_storage_service()
    success &= create_run_script()
    
    print("\n" + "="*50)
    if success:
        print("[SETUP COMPLETE]")
        print("\nNext steps:")
        print("1. Update .env file with your API keys")
        print("2. Run the server:")
        print("   Unix/macOS: ./run.sh")
        print("   Windows: run.bat")
        print("   Manual: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print("\n3. API documentation: http://localhost:8000/docs")
        print("4. Update frontend to use backend at http://localhost:8000")
    else:
        print("[SETUP COMPLETE WITH WARNINGS]")
        print("Check error messages above and resolve issues")
        print("Run this script again after fixing problems")
    
    print("="*50)

if __name__ == "__main__":
    main()
