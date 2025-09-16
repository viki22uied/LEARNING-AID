#!/usr/bin/env python3
"""
Startup script for Open Educational Resources Backend
"""

import asyncio
import sys
import os
import uvicorn
import logging

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.utils.logging import setup_logging

def main():
    """Start the application"""
    # Setup logging
    logger = setup_logging()
    
    logger.info("Starting Open Educational Resources Backend...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"API Host: {settings.api_host}")
    logger.info(f"API Port: {settings.api_port}")
    logger.info(f"Database: {settings.database_url[:30]}...")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()
