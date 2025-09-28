#!/usr/bin/env python3
"""
Test version of nudge.py without TTS to debug the monitoring issue
"""

import os
import time
import asyncio
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
INACTIVITY_THRESHOLD = 10  # seconds
POLLING_INTERVAL = 5  # seconds
REACT_APP_URL = "http://localhost:5173"

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleCodeMonitor:
    """Simplified code monitor for testing"""

    def __init__(self, url: str = REACT_APP_URL):
        self.url = url
        self.driver = None
        self.last_code = ""
        self.last_change_time = datetime.now()

    def setup_browser(self):
        """Setup Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(self.url)
            logger.info(f"Browser setup complete, navigated to {self.url}")

            # Wait for React app to load
            time.sleep(5)

            # Check for Monaco
            try:
                result = self.driver.execute_script(
                    "return typeof window.monaco !== 'undefined'"
                )
                if result:
                    logger.info("Monaco editor detected")
                else:
                    logger.warning("Monaco editor not detected")
            except Exception as e:
                logger.warning(f"Monaco check failed: {e}")

            return True
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return False

    def get_current_code(self) -> str:
        """Get code from editor"""
        try:
            # Try Monaco API first
            code = self.driver.execute_script(
                """
                const editors = window.monaco?.editor?.getEditors();
                if (editors && editors.length > 0) {
                    return editors[0].getValue();
                }
                return '';
            """
            )

            if code and len(code.strip()) > 0:
                logger.debug(f"Got code via Monaco API: {len(code)} chars")
                return code

            # Fallback methods
            selectors = [".monaco-editor .view-lines", ".monaco-editor", "textarea"]

            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = (
                        element.get_attribute("textContent")
                        or element.get_attribute("value")
                        or ""
                    )
                    if text and len(text.strip()) > 0:
                        logger.debug(f"Got code via {selector}: {len(text)} chars")
                        return text
                except NoSuchElementException:
                    continue

            logger.debug("No code found")
            return ""

        except Exception as e:
            logger.error(f"Error getting code: {e}")
            return ""

    def check_for_changes(self) -> dict:
        """Check for code changes"""
        current_code = self.get_current_code()
        now = datetime.now()

        changed = current_code != self.last_code

        if changed:
            logger.info(
                f"CODE CHANGED: {len(self.last_code)} -> {len(current_code)} chars"
            )
            self.last_change_time = now
            self.last_code = current_code

        inactive_duration = (now - self.last_change_time).total_seconds()

        return {
            "code": current_code,
            "changed": changed,
            "inactive_duration": inactive_duration,
            "timestamp": now,
        }

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


async def test_monitoring():
    """Test the monitoring system"""
    print(
        f"""
    🧪 Testing Nudge Monitoring System
    ==================================
    
    Configuration:
    - Inactivity Threshold: {INACTIVITY_THRESHOLD} seconds
    - Polling Interval: {POLLING_INTERVAL} seconds
    - React App URL: {REACT_APP_URL}
    
    Starting test...
    """
    )

    monitor = SimpleCodeMonitor()

    if not monitor.setup_browser():
        print("❌ Browser setup failed!")
        return

    try:
        start_time = datetime.now()

        print("🔍 Monitoring for changes... (edit code in the browser)")
        print(f"Will nudge after {INACTIVITY_THRESHOLD} seconds of inactivity\n")

        while True:
            status = monitor.check_for_changes()

            elapsed = (datetime.now() - start_time).total_seconds()

            print(
                f"[{elapsed:6.1f}s] Inactive: {status['inactive_duration']:5.1f}s | "
                f"Changed: {str(status['changed']):5s} | "
                f"Code: {len(status['code']):4d} chars"
            )

            # Check if nudge should trigger
            if status["inactive_duration"] >= INACTIVITY_THRESHOLD:
                print(
                    f"\n🎯 NUDGE TRIGGERED! (inactive for {status['inactive_duration']:.1f}s)"
                )
                print(f"Current code preview: {status['code'][:100]}...")
                print("In real system, AI would analyze and speak here.\n")

                # Reset the timer to avoid continuous nudging
                monitor.last_change_time = datetime.now()

            await asyncio.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        monitor.close()


if __name__ == "__main__":
    asyncio.run(test_monitoring())
