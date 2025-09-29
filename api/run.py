#!/usr/bin/env python3
"""
FastAPI Application Runner

Simple script to run the FastAPI application with uvicorn.
This follows the Model-Controller-Service architecture pattern.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn


def main() -> None:
    """
    Main entry point for running the FastAPI application.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting FastAPI Interview Task API...")
    logger.info("Architecture: Model-Controller-Service")
    logger.info("Server: uvicorn")
    logger.info("Host: 0.0.0.0:8001")
    
    try:
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
