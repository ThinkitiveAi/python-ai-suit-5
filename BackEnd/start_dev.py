#!/usr/bin/env python3
"""
Development server with relaxed rate limits for testing.
"""
import os
import shutil
import uvicorn
from pathlib import Path

def setup_dev_environment():
    """Setup development environment with relaxed rate limits."""
    
    # Backup current .env if it exists
    env_file = Path(".env")
    env_dev_file = Path(".env.development")
    env_backup = Path(".env.backup")
    
    if env_file.exists() and not env_backup.exists():
        shutil.copy2(env_file, env_backup)
        print("📋 Backed up current .env to .env.backup")
    
    # Copy development config
    if env_dev_file.exists():
        shutil.copy2(env_dev_file, env_file)
        print("🔧 Using development configuration with relaxed rate limits")
        print("   Rate limit: 50 requests per hour (vs 5 in production)")
    
    print("🚀 Starting development server...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🧪 Testing: Use Swagger UI for easy testing")
    print("=" * 50)

def restore_production_env():
    """Restore production environment."""
    env_file = Path(".env")
    env_backup = Path(".env.backup")
    
    if env_backup.exists():
        shutil.copy2(env_backup, env_file)
        env_backup.unlink()
        print("✅ Restored production configuration")

if __name__ == "__main__":
    try:
        setup_dev_environment()
        
        # Start the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development server...")
        restore_production_env()
    except Exception as e:
        print(f"❌ Error: {e}")
        restore_production_env()
