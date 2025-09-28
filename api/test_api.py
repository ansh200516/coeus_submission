#!/usr/bin/env python3
"""
Simple test script for the Interview Task API.

This script tests the basic functionality of the FastAPI application
following the Model-Controller-Service architecture.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.models.task_model import TaskStartRequest, TaskStartResponse
from api.services.task_service import task_service


async def test_models() -> None:
    """Test Pydantic models."""
    print("🧪 Testing Pydantic models...")
    
    # Test valid request
    try:
        request = TaskStartRequest(name="Test Candidate", duration=300)
        print(f"✅ Valid request created: {request.name}, {request.duration}s")
    except Exception as e:
        print(f"❌ Failed to create valid request: {e}")
        return
    
    # Test invalid request
    try:
        invalid_request = TaskStartRequest(name="", duration=-1)
        print(f"❌ Invalid request should have failed: {invalid_request}")
    except Exception as e:
        print(f"✅ Invalid request correctly rejected: {e}")
    
    # Test response model
    try:
        response = TaskStartResponse(
            message="Test message",
            task_id="test_123",
            status="started"
        )
        print(f"✅ Response model created: {response.message}")
    except Exception as e:
        print(f"❌ Failed to create response: {e}")


async def test_service() -> None:
    """Test task service."""
    print("\n🧪 Testing task service...")
    
    # Test script validation
    is_available, message = task_service.validate_script_availability()
    print(f"Script availability: {'✅' if is_available else '❌'} {message}")
    
    if not is_available:
        print("⚠️  Cannot test task execution - script not available")
        return
    
    # Test task execution (dry run)
    print("Testing task execution...")
    try:
        success, message, task_id = task_service.execute_interview_task(
            name="Test Candidate",
            duration=5  # Short duration for testing
        )
        
        if success:
            print(f"✅ Task started successfully: {task_id}")
            print(f"   Message: {message}")
        else:
            print(f"❌ Task failed to start: {message}")
            
    except Exception as e:
        print(f"❌ Task execution error: {e}")


async def main() -> None:
    """Main test function."""
    print("🚀 Interview Task API Test Suite")
    print("=" * 50)
    
    await test_models()
    await test_service()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nTo start the API server:")
    print("  python run.py")
    print("\nTo test the API endpoint:")
    print("  curl -X POST http://localhost:8000/tasks/start \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"name\": \"Test User\", \"duration\": 300}'")


if __name__ == "__main__":
    asyncio.run(main())
