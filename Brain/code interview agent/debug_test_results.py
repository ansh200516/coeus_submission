#!/usr/bin/env python3
"""
Debug script to test test results detection
"""

import time
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(__file__))

from nudge import CodeEditorMonitor


def debug_test_results():
    """Debug test results detection"""
    print("🔍 Debugging Test Results Detection")
    print("=" * 50)

    monitor = CodeEditorMonitor()

    if not monitor.setup_browser():
        print("❌ Browser setup failed")
        return

    try:
        print("✅ Browser setup successful")
        print("Waiting 5 seconds for page to load...")
        time.sleep(5)

        print("\n📊 Now click 'Submit Solution' in the browser and wait for results...")
        print("This script will monitor for 60 seconds...")

        for i in range(12):  # 60 seconds / 5 second intervals
            print(f"\n--- Check {i+1}/12 ---")

            # Check for submission
            submission = monitor.check_for_submission()
            print(f"Submission detected: {submission}")

            # Get test results
            results = monitor.get_test_results()
            print(f"Test results found: {results['has_results']}")

            if results["has_results"]:
                print(f"Score: {results['score']}")
                print(f"All passed: {results['all_passed']}")
                print(f"Test cases: {len(results['test_cases'])}")

                # If we found results, also debug the page
                print("\n🔍 Page content debug:")
                monitor.debug_page_content()
                break

            time.sleep(5)

        print("\n✅ Debug complete")

    except Exception as e:
        print(f"❌ Debug failed: {e}")
    finally:
        monitor.close()


if __name__ == "__main__":
    debug_test_results()
