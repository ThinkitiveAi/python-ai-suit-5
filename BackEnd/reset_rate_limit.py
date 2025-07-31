#!/usr/bin/env python3
"""
Utility to reset rate limits for testing purposes.
This restarts the server with a fresh rate limiter state.
"""
import os
import sys
import signal
import psutil
import subprocess
import time

def find_server_process():
    """Find running FastAPI server process."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'main.py' in cmdline and 'python' in cmdline:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def restart_server():
    """Restart the server to reset rate limits."""
    print("🔄 Restarting server to reset rate limits...")
    
    # Find and stop current server
    pid = find_server_process()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 Stopped server (PID: {pid})")
            time.sleep(2)
        except ProcessLookupError:
            print("⚠️  Server was not running")
    
    # Start server with development config
    print("🚀 Starting server with development rate limits...")
    subprocess.Popen([sys.executable, "start_dev.py"])
    
    print("✅ Server restarted with fresh rate limits!")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    restart_server()
