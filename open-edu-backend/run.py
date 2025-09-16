#!/usr/bin/env python3
"""
Simple run script for the Open Educational Resources Recommendation Backend
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import uvicorn
    from app.config import settings
    
    print("🚀 Starting Open Educational Resources Recommendation Backend...")
    print(f"   - Host: {settings.api_host}")
    print(f"   - Port: {settings.api_port}")
    print(f"   - Environment: Development (Simplified)")
    
    uvicorn.run(
        "app.main_simple:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install the required dependencies:")
    print("   pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
