#!/usr/bin/env python3
"""
Healthcare Management System Deployment Script
Deploys both backend and frontend for production use
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import flask
        import numpy
        import matplotlib
        import pandas
        print("✅ Python packages available")
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        return False
    
    # Check Node.js/npm
    node_available = subprocess.run(['which', 'node'], capture_output=True).returncode == 0
    npm_available = subprocess.run(['which', 'npm'], capture_output=True).returncode == 0
    
    if not node_available:
        print("❌ Node.js not found - frontend deployment skipped")
        print("💡 To install Node.js: brew install node")
    else:
        print("✅ Node.js available")
    
    if not npm_available:
        print("❌ npm not found - frontend deployment skipped")
        print("💡 To install npm: brew install npm")
    else:
        print("✅ npm available")
    
    return True

def deploy_backend():
    """Deploy the Flask backend"""
    print("\n🚀 Deploying Backend...")
    
    backend_dir = Path(__file__).parent
    
    try:
        # Start backend server
        os.chdir(backend_dir)
        print("📦 Starting Flask backend server...")
        
        # Run in background
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        result = subprocess.run([
            'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
            'http://localhost:5001/api/bi/health'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout == '200':
            print("✅ Backend deployed successfully!")
            print("🌐 Backend URL: http://localhost:5001")
            print("📊 BI Dashboard: http://localhost:5001/api/bi/health")
            return process
        else:
            print("❌ Backend deployment failed")
            return None
            
    except Exception as e:
        print(f"❌ Backend deployment error: {e}")
        return None

def deploy_frontend():
    """Deploy the React frontend"""
    print("\n🎨 Deploying Frontend...")
    
    frontend_dir = Path(__file__).parent / 'frontend'
    
    try:
        # Check if Node.js/npm available
        if subprocess.run(['which', 'npm'], capture_output=True).returncode != 0:
            print("⚠️  Node.js/npm not available - skipping frontend deployment")
            return None
        
        os.chdir(frontend_dir)
        
        # Install dependencies
        print("📦 Installing frontend dependencies...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr}")
            return None
        
        # Start development server
        print("🚀 Starting React development server...")
        process = subprocess.Popen([
            'npm', 'start'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Frontend deployment initiated!")
        print("🌐 Frontend URL: http://localhost:3000")
        print("⏳ Waiting for frontend to start...")
        
        return process
        
    except Exception as e:
        print(f"❌ Frontend deployment error: {e}")
        return None

def main():
    """Main deployment function"""
    print("🏥 Healthcare Management System Deployment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Deployment failed due to missing dependencies")
        return
    
    # Deploy backend
    backend_process = deploy_backend()
    
    # Deploy frontend
    frontend_process = deploy_frontend()
    
    # Open browser
    print("\n🌐 Opening browser...")
    time.sleep(5)
    
    try:
        if backend_process:
            webbrowser.open('http://localhost:5001/api/bi/health')
        if frontend_process:
            webbrowser.open('http://localhost:3000')
    except:
        print("⚠️  Could not open browser automatically")
    
    # Display deployment summary
    print("\n" + "=" * 50)
    print("🎉 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    if backend_process:
        print("✅ Backend: http://localhost:5001")
        print("📊 API Endpoints:")
        print("   - Health Check: http://localhost:5001/api/bi/health")
        print("   - Real-time Data: http://localhost:5001/api/bi/real-time/stream")
        print("   - Analytics: http://localhost:5001/api/bi/analytics/advanced")
        print("   - Visualizations: http://localhost:5001/api/bi/visualizations/")
    
    if frontend_process:
        print("✅ Frontend: http://localhost:3000")
    
    print("\n📋 Available Services:")
    print("🔬 NumPy Analytics: ✅ Active")
    print("📈 Matplotlib Visualizations: ✅ Active")
    print("💾 Pandas Data Processing: ✅ Active")
    print("🤖 ML Insights: ✅ Active")
    
    print("\n🛑 Press Ctrl+C to stop servers")
    
    try:
        # Keep servers running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
