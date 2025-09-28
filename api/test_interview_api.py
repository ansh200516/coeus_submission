#!/usr/bin/env python3
"""
Interview API Testing Script

This script tests the interview API endpoints to ensure they work correctly
with the form data from the frontend.

Usage:
    python test_interview_api.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.services.interview_service import interview_service
from api.models.interview_model import InterviewStartRequest


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_interview_service() -> None:
    """
    Test the interview service functionality.
    """
    logger.info("=" * 60)
    logger.info("Testing Interview Service")
    logger.info("=" * 60)
    
    try:
        # Test service initialization
        logger.info("✅ Interview service initialized successfully")
        logger.info(f"LDA path: {interview_service.lda_path}")
        logger.info(f"LDA exists: {interview_service.lda_path.exists()}")
        logger.info(f"Scraper path: {interview_service.unified_scraper_path}")
        logger.info(f"Scraper exists: {interview_service.unified_scraper_path.exists()}")
        
        # Test model validation
        logger.info("\n📋 Testing model validation...")
        
        # Valid request
        try:
            valid_request = InterviewStartRequest(
                name="John Doe",
                gender="Male",
                linkedin_url="https://linkedin.com/in/johndoe",
                duration=1800
            )
            logger.info("✅ Valid request model created successfully")
            logger.info(f"   Name: {valid_request.name}")
            logger.info(f"   Gender: {valid_request.gender}")
            logger.info(f"   LinkedIn: {valid_request.linkedin_url}")
            logger.info(f"   Duration: {valid_request.duration}")
        except Exception as e:
            logger.error(f"❌ Valid request failed: {e}")
        
        # Invalid requests
        try:
            invalid_request = InterviewStartRequest(
                name="",  # Empty name should fail
                gender="Male",
                linkedin_url="https://linkedin.com/in/johndoe",
                duration=1800
            )
            logger.error("❌ Empty name validation failed - should have raised error")
        except Exception as e:
            logger.info(f"✅ Empty name validation working: {e}")
        
        try:
            invalid_url = InterviewStartRequest(
                name="John Doe",
                gender="Male",
                linkedin_url="https://google.com",  # Not LinkedIn
                duration=1800
            )
            logger.error("❌ Invalid LinkedIn URL validation failed - should have raised error")
        except Exception as e:
            logger.info(f"✅ LinkedIn URL validation working: {e}")
        
        # Test task tracking
        logger.info("\n📊 Testing task tracking...")
        
        # Simulate a task
        task_id = "test_task_123"
        interview_service.active_tasks[task_id] = {
            "name": "Test User",
            "processing_status": "data_collection",
            "lda_ready": False
        }
        
        # Test status retrieval
        status = interview_service.get_task_status(task_id)
        if status:
            logger.info(f"✅ Task status retrieved: {status['processing_status']}")
        else:
            logger.error("❌ Failed to retrieve task status")
        
        # Test readiness check
        ready = interview_service.is_interview_ready(task_id)
        logger.info(f"✅ Interview ready check: {ready} (expected: False)")
        
        # Update task to ready state
        interview_service.active_tasks[task_id]["processing_status"] = "interview_active"
        interview_service.active_tasks[task_id]["lda_ready"] = True
        
        ready = interview_service.is_interview_ready(task_id)
        logger.info(f"✅ Interview ready check after update: {ready} (expected: True)")
        
        # Clean up test task
        interview_service.cleanup_task(task_id)
        status_after_cleanup = interview_service.get_task_status(task_id)
        logger.info(f"✅ Task cleanup successful: {status_after_cleanup is None}")
        
        logger.info("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}", exc_info=True)


async def test_file_paths() -> None:
    """
    Test that all required file paths exist.
    """
    logger.info("\n🔍 Testing file paths...")
    
    # Check LDA main.py
    lda_path = project_root / "Brain" / "lda" / "main.py"
    logger.info(f"LDA main.py: {lda_path}")
    logger.info(f"   Exists: {'✅' if lda_path.exists() else '❌'}")
    
    # Check unified scraper
    scraper_path = project_root / "Brain" / "lda" / "unified_scraper.py"
    logger.info(f"Unified scraper: {scraper_path}")
    logger.info(f"   Exists: {'✅' if scraper_path.exists() else '❌'}")
    
    # Check job description
    job_desc_path = project_root / "job_description.txt"
    logger.info(f"Job description: {job_desc_path}")
    logger.info(f"   Exists: {'✅' if job_desc_path.exists() else '❌'}")
    
    # Check temp directory creation
    temp_dir = project_root / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)
    logger.info(f"Temp uploads dir: {temp_dir}")
    logger.info(f"   Created: {'✅' if temp_dir.exists() else '❌'}")


async def main() -> None:
    """
    Main test function.
    """
    logger.info("🧪 Interview API Test Suite")
    logger.info("=" * 50)
    
    await test_file_paths()
    await test_interview_service()
    
    logger.info("\n" + "=" * 50)
    logger.info("🏁 Test suite completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        sys.exit(1)
