#!/usr/bin/env python3
"""
Setup script for Provider Registration API.
"""
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# Application Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production-please
APP_NAME=Provider Registration API
APP_VERSION=1.0.0

# Database Configuration - Using SQLite
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./providers.db

# Security Settings
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=3600

# Email Configuration (Debug mode - prints to console)
DEBUG_EMAIL=True
FROM_EMAIL=noreply@providerapi.com

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]

# Timezone
TIMEZONE=UTC
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def initialize_database():
    """Initialize SQLite database"""
    print("🗄️  Initializing SQLite database...")
    db_path = "providers.db"
    
    # The database will be created automatically when the app starts
    # But we can verify SQLite is working
    try:
        conn = sqlite3.connect(":memory:")
        conn.close()
        print("✅ SQLite is working")
    except Exception as e:
        print(f"❌ SQLite error: {e}")
        sys.exit(1)

def run_tests():
    """Run basic tests"""
    print("🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"])
        print("✅ All tests passed")
    except subprocess.CalledProcessError:
        print("⚠️  Some tests failed - but setup is complete")
    except FileNotFoundError:
        print("⚠️  pytest not found - skipping tests")

def main():
    """Main setup function"""
    print("🚀 Setting up Provider Registration API")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run setup steps
    check_python_version()
    install_dependencies()
    create_env_file()
    initialize_database()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Review and update the .env file with your settings")
    print("2. Start the server: python3 main.py")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("4. Test the API: python3 test_api.py")
    print("\nFor production deployment:")
    print("- Change SECRET_KEY in .env")
    print("- Set DEBUG=False")
    print("- Use a production database (PostgreSQL/MySQL)")
    print("- Configure proper SMTP settings")
    print("- Set up reverse proxy (nginx)")
    print("- Enable HTTPS")

if __name__ == "__main__":
    main()
