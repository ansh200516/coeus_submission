#!/usr/bin/env python3
"""
LDA (Lie Detection Agent) Subprocess Testing Script

This script runs the LDA interview system as a subprocess and provides
comprehensive logging of the process lifecycle, output, and any errors.

Usage:
    python lda_subprocess.py [candidate_name] [duration]

The script will:
1. Locate the LDA main.py application
2. Start it as a subprocess with comprehensive monitoring
3. Monitor the process for a specified duration
4. Capture and log all output
5. Gracefully terminate the process and report results

The LDA system performs interactive interviews with lie detection capabilities.
"""

import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


# Configure comprehensive logging
def setup_logging() -> logging.Logger:
    """
    Set up comprehensive logging configuration.
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"lda_subprocess_test_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


def stream_output(pipe, stream_name: str, logger: logging.Logger) -> None:
    """
    Stream and log subprocess output in real-time.
    
    Args:
        pipe: Subprocess pipe (stdout or stderr)
        stream_name: Name of the stream for logging
        logger: Logger instance
    """
    try:
        for line in iter(pipe.readline, ''):
            if line:
                line = line.rstrip()
                logger.info(f"[{stream_name}] {line}")
        pipe.close()
    except Exception as e:
        logger.error(f"Error reading {stream_name}: {e}")


def test_lda_subprocess(monitor_duration: int = 300) -> Tuple[bool, Optional[int]]:
    """
    Test the LDA interview system by running it as a subprocess.
    
    Args:
        monitor_duration: How long to monitor the process (seconds, default 5 minutes)
        
    Returns:
        Tuple of (success: bool, exit_code: Optional[int])
    """
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Starting LDA Interview System Subprocess Test")
    logger.info("=" * 60)
    
    # Find the LDA application
    current_dir = Path.cwd()
    logger.info(f"Current working directory: {current_dir}")
    
    # Try multiple possible paths for the LDA main.py
    possible_paths = [
        Path("main.py"),  # Same directory (if running from Brain/lda)
        Path("Brain/lda/main.py"),  # From project root
        Path("../Brain/lda/main.py"),  # From subdirectory
        Path("lda/main.py"),  # From Brain directory
        Path("../lda/main.py"),  # From Brain subdirectory
    ]
    
    agent_path = None
    for path in possible_paths:
        full_path = current_dir / path
        logger.info(f"Checking for agent at: {full_path}")
        if full_path.exists():
            agent_path = full_path
            logger.info(f"✅ Found agent at: {agent_path}")
            break
    
    if not agent_path:
        logger.error("❌ LDA main.py not found in any expected location")
        logger.error("Searched paths:")
        for path in possible_paths:
            logger.error(f"  - {current_dir / path}")
        return False, None
    
    # Get environment information
    logger.info("Environment Information:")
    logger.info(f"  Python executable: {sys.executable}")
    logger.info(f"  Python version: {sys.version}")
    logger.info(f"  Working directory: {os.getcwd()}")
    logger.info(f"  LDA main.py path: {agent_path}")
    
    process = None
    success = False
    exit_code = None
    
    try:
        logger.info("🚀 Starting LDA subprocess...")
        
        # Try different ways to start the subprocess
        # First try with uv run (proper dependency management)
        # Then fallback to direct python execution
        commands_to_try = [
            ["uv", "run", str(agent_path)],
            [sys.executable, str(agent_path)]
        ]
        
        process = None
        last_error = None
        
        for i, cmd in enumerate(commands_to_try):
            try:
                logger.info(f"Attempt {i+1}: Running command: {' '.join(cmd)}")
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=agent_path.parent
                )
                logger.info(f"✅ Successfully started with command: {' '.join(cmd)}")
                break
            except FileNotFoundError as e:
                last_error = e
                logger.warning(f"⚠️  Command not found: {' '.join(cmd)} - {e}")
                continue
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️  Failed to start with command: {' '.join(cmd)} - {e}")
                continue
        
        if process is None:
            raise Exception(f"Failed to start subprocess with any method. Last error: {last_error}")
        
        logger.info(f"✅ Process started with PID: {process.pid}")
        
        # Start threads to monitor output streams
        stdout_thread = threading.Thread(
            target=stream_output,
            args=(process.stdout, "STDOUT", logger),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=stream_output,
            args=(process.stderr, "STDERR", logger),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Monitor the process
        logger.info(f"⏱️  Monitoring process for {monitor_duration} seconds...")
        
        start_time = time.time()
        while True:
            poll_result = process.poll()
            
            if poll_result is not None:
                logger.warning(f"⚠️  Process terminated early with exit code: {poll_result}")
                exit_code = poll_result
                
                # Provide helpful error analysis
                if poll_result == 1:
                    logger.info("🔍 Exit code 1 usually indicates:")
                    logger.info("   - Missing dependencies (try: uv sync)")
                    logger.info("   - Configuration issues")
                    logger.info("   - Import errors")
                    logger.info("   - Check the stderr output above for details")
                elif poll_result == 2:
                    logger.info("🔍 Exit code 2 usually indicates:")
                    logger.info("   - Permission errors (like virtual environment access)")
                    logger.info("   - File system issues")
                    logger.info("   - Try running as administrator or check file permissions")
                    logger.info("   - Check the stderr output above for details")
                elif poll_result > 2:
                    logger.info(f"🔍 Exit code {poll_result} indicates:")
                    logger.info("   - Application-specific error")
                    logger.info("   - Check the stderr output above for details")
                break
            
            # Check if monitoring duration has elapsed
            elapsed = time.time() - start_time
            if elapsed >= monitor_duration:
                logger.info(f"⏰ Monitoring duration ({monitor_duration}s) completed")
                break
            
            # Log periodic status
            elapsed_int = int(elapsed)
            if elapsed_int % 2 == 0 and elapsed_int > 0:
                logger.info(f"📊 Process still running... ({elapsed_int}s elapsed)")
            
            time.sleep(1)
        
        # Check final status
        final_poll = process.poll()
        if final_poll is None:
            logger.info("✅ Process is still running after monitoring period")
            success = True
        else:
            logger.info(f"Process finished with exit code: {final_poll}")
            exit_code = final_poll
            success = (final_poll == 0)
            
    except Exception as e:
        logger.error(f"❌ Error during subprocess execution: {e}")
        logger.exception("Full exception details:")
        
    finally:
        # Cleanup
        if process:
            poll_result = process.poll()
            if poll_result is None:
                logger.info("🛑 Terminating process...")
                try:
                    # Try graceful termination first
                    process.terminate()
                    try:
                        exit_code = process.wait(timeout=5)
                        logger.info(f"✅ Process terminated gracefully with exit code: {exit_code}")
                    except subprocess.TimeoutExpired:
                        logger.warning("⚠️  Process didn't terminate gracefully, forcing...")
                        process.kill()
                        exit_code = process.wait()
                        logger.info(f"🔨 Process force-killed with exit code: {exit_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Error during process cleanup: {e}")
            else:
                exit_code = poll_result
                logger.info(f"Process already terminated with exit code: {exit_code}")
    
    # Final report
    logger.info("=" * 60)
    logger.info("LDA SUBPROCESS TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Success: {'✅ YES' if success else '❌ NO'}")
    logger.info(f"Exit Code: {exit_code}")
    logger.info(f"LDA Path: {agent_path}")
    logger.info(f"Monitor Duration: {monitor_duration}s")
    logger.info("=" * 60)
    
    return success, exit_code


if __name__ == "__main__":
    """
    Main entry point when running script directly.
    
    Command line arguments:
        1. name (optional): Name of the candidate or task identifier
        2. duration (optional): Monitor duration in seconds (default: 300 = 5 minutes)
    """
    print("🎯 LDA Interview System Subprocess Test")
    print("=" * 50)
    
    # Parse command line arguments
    candidate_name = "Unknown Candidate"
    monitor_time = 300  # Default 5 minutes for LDA interviews
    
    if len(sys.argv) > 1:
        candidate_name = sys.argv[1]
        print(f"Candidate name: {candidate_name}")
    
    if len(sys.argv) > 2:
        try:
            monitor_time = int(sys.argv[2])
            print(f"Using custom monitor duration: {monitor_time} seconds")
        except ValueError:
            print(f"Invalid monitor time '{sys.argv[2]}', using default: {monitor_time} seconds")
    else:
        print(f"Using default monitor duration: {monitor_time} seconds")
    
    print(f"Starting LDA interview for: {candidate_name}")
    print(f"Duration: {monitor_time} seconds")
    print("-" * 50)
    
    # Run the test
    success, exit_code = test_lda_subprocess(monitor_duration=monitor_time)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
