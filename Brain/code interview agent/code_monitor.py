"""
Code monitoring and browser automation for the Code Interview Agent.

This module handles browser automation to monitor the React code editor,
track code changes, manage test execution, and handle question selection.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException
)
from selenium.webdriver.common.keys import Keys

from config import (
    BROWSER_HEADLESS,
    REACT_APP_URL,
    BROWSER_TIMEOUT,
    POLLING_INTERVAL,
    MIN_CODE_CHANGE_THRESHOLD
)
from utils import analyze_code_complexity, extract_code_changes, safe_json_load

logger = logging.getLogger(__name__)


class CodeEditorMonitor:
    """
    Monitors the React code editor for changes and manages browser automation.
    
    This class handles all browser interactions including code monitoring,
    test execution, and question management through the web interface.
    """

    def __init__(self) -> None:
        """Initialize the code editor monitor."""
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.last_code = ""
        self.last_check_time = datetime.now()
        self.current_question_id: Optional[int] = None
        self.test_results_history: List[Dict[str, Any]] = []
        
        # Browser element selectors for Next.js code-engine
        self.selectors = {
            "code_editor": ".monaco-editor .view-lines",
            "code_textarea": "textarea.inputarea",
            "run_button": "button:contains('Submit')",
            "submit_button": "button:contains('Submit')",
            "test_output": "[data-testrunner]",
            "question_selector": "select",
            "question_title": "h1",
            "test_results": "[data-test-component]",
            "console_output": ".console-output",
            "score_display": "[data-testid='score-display']",
            "test_case_results": "[data-testid='test-case-result']"
        }
        
        logger.info("CodeEditorMonitor initialized")

    def setup_browser(self) -> bool:
        """
        Set up the Chrome browser with appropriate options.
        
        Returns:
            bool: True if browser setup successful, False otherwise
        """
        try:
            chrome_options = Options()
            
            if BROWSER_HEADLESS:
                chrome_options.add_argument("--headless")
            
            # Additional Chrome options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Disable notifications and popups
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, BROWSER_TIMEOUT)
            
            # Navigate to the React app
            logger.info(f"Navigating to React app: {REACT_APP_URL}")
            self.driver.get(REACT_APP_URL)
            
            # Wait for the page to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            
            # Give the React app time to fully initialize
            time.sleep(3)
            
            logger.info("Browser setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            return False

    def get_current_code(self) -> str:
        """
        Get the current code from the Monaco editor.
        
        Returns:
            str: Current code content or empty string if failed
        """
        try:
            if not self.driver:
                logger.error("Browser not initialized")
                return ""
            
            # Try multiple methods to get the code
            code = self._get_code_from_monaco() or self._get_code_from_textarea()
            
            if code and code != self.last_code:
                logger.debug(f"Code change detected: {len(code)} characters")
                self.last_code = code
                self.last_check_time = datetime.now()
            
            return code
            
        except Exception as e:
            logger.error(f"Error getting current code: {e}")
            return ""

    def _get_code_from_monaco(self) -> str:
        """Get code from Monaco editor using JavaScript execution."""
        try:
            # Execute JavaScript to get Monaco editor content
            code = self.driver.execute_script("""
                const editor = window.monaco?.editor?.getModels()?.[0];
                return editor ? editor.getValue() : '';
            """)
            return code if isinstance(code, str) else ""
        except Exception as e:
            logger.debug(f"Failed to get code from Monaco: {e}")
            return ""

    def _get_code_from_textarea(self) -> str:
        """Get code from textarea fallback method."""
        try:
            textarea = self.driver.find_element(By.CSS_SELECTOR, self.selectors["code_textarea"])
            return textarea.get_attribute("value") or ""
        except Exception as e:
            logger.debug(f"Failed to get code from textarea: {e}")
            return ""

    def set_question(self, question_id: int) -> bool:
        """
        Set the current question in the editor.
        
        Args:
            question_id: ID of the question to set
            
        Returns:
            bool: True if question set successfully, False otherwise
        """
        try:
            if not self.driver:
                logger.error("Browser not initialized")
                return False
            
            # Generate a unique session ID for this interview
            import uuid
            session_id = f"interview_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            # Navigate to the coding-engine page with question and session parameters
            new_url = f"{REACT_APP_URL}?question={question_id}&session={session_id}"
            logger.info(f"Setting question {question_id} via URL: {new_url}")
            
            self.driver.get(new_url)
            
            # Wait for page to load and React to initialize
            time.sleep(5)
            
            # Verify the question was set by checking the page title
            try:
                # Wait for the question title to appear
                title_element = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                title_text = title_element.text
                
                if str(question_id) in title_text:
                    self.current_question_id = question_id
                    logger.info(f"Successfully set question ID: {question_id} (Title: {title_text})")
                    return True
                else:
                    logger.warning(f"Question ID {question_id} not found in title: {title_text}")
                    # Still consider it successful if we got to the page
                    self.current_question_id = question_id
                    return True
                    
            except TimeoutException:
                logger.warning("Could not find question title, but page loaded")
                self.current_question_id = question_id
                return True
            
        except Exception as e:
            logger.error(f"Failed to set question {question_id}: {e}")
            return False

    def get_current_question_info(self) -> Dict[str, Any]:
        """
        Get information about the currently selected question.
        
        Returns:
            Dict[str, Any]: Question information or empty dict if failed
        """
        try:
            if not self.driver:
                return {}
            
            question_info = {}
            
            # Get question title
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, self.selectors["question_title"])
                question_info["title"] = title_element.text
            except NoSuchElementException:
                question_info["title"] = "Unknown Question"
            
            # Get question ID from selector
            try:
                selector = self.driver.find_element(By.CSS_SELECTOR, self.selectors["question_selector"])
                from selenium.webdriver.support.ui import Select
                select = Select(selector)
                selected_option = select.first_selected_option
                question_info["id"] = int(selected_option.get_attribute("value"))
            except (NoSuchElementException, ValueError):
                question_info["id"] = self.current_question_id
            
            return question_info
            
        except Exception as e:
            logger.error(f"Error getting question info: {e}")
            return {}

    def run_tests(self) -> Dict[str, Any]:
        """
        Execute tests and return the results.
        
        Returns:
            Dict[str, Any]: Test execution results
        """
        try:
            if not self.driver:
                logger.error("Browser not initialized")
                return {"success": False, "error": "Browser not initialized"}
            
            # Click the run button
            run_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["run_button"]))
            )
            run_button.click()
            
            # Wait for test execution to complete
            time.sleep(3)  # Initial wait
            
            # Wait for results to appear (with timeout)
            start_time = time.time()
            timeout = 30  # 30 second timeout for test execution
            
            while time.time() - start_time < timeout:
                test_results = self._parse_test_results()
                if test_results.get("completed", False):
                    break
                time.sleep(1)
            
            results = self._parse_test_results()
            self.test_results_history.append({
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            
            logger.info(f"Test execution completed: {results.get('passed', 0)}/{results.get('total', 0)} passed")
            return results
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {"success": False, "error": str(e)}

    def _parse_test_results(self) -> Dict[str, Any]:
        """Parse test results from the output section."""
        try:
            results = {
                "success": False,
                "completed": False,
                "passed": 0,
                "total": 0,
                "failures": [],
                "output": "",
                "error": None
            }
            
            # Get test output
            try:
                output_element = self.driver.find_element(By.CSS_SELECTOR, self.selectors["test_output"])
                output_text = output_element.text
                results["output"] = output_text
                results["completed"] = bool(output_text.strip())
            except NoSuchElementException:
                return results
            
            # Parse test results (this will depend on your React app's output format)
            if "All tests passed" in output_text:
                results["success"] = True
                # Extract numbers if available
                import re
                match = re.search(r'(\d+)/(\d+)', output_text)
                if match:
                    results["passed"] = int(match.group(1))
                    results["total"] = int(match.group(2))
                else:
                    results["passed"] = results["total"] = 1
            
            elif "failed" in output_text.lower() or "error" in output_text.lower():
                # Extract failure information
                lines = output_text.split('\n')
                for line in lines:
                    if "failed" in line.lower() or "error" in line.lower():
                        results["failures"].append(line.strip())
                
                # Try to extract test counts
                import re
                match = re.search(r'(\d+)/(\d+)', output_text)
                if match:
                    results["passed"] = int(match.group(1))
                    results["total"] = int(match.group(2))
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing test results: {e}")
            return {"success": False, "error": str(e), "completed": True}

    def get_console_output(self) -> str:
        """
        Get console output from the browser.
        
        Returns:
            str: Console output or empty string
        """
        try:
            if not self.driver:
                return ""
            
            # Get browser console logs
            logs = self.driver.get_log('browser')
            console_output = []
            
            for log in logs:
                if log['level'] in ['INFO', 'WARNING', 'SEVERE']:
                    console_output.append(f"[{log['level']}] {log['message']}")
            
            return '\n'.join(console_output)
            
        except Exception as e:
            logger.error(f"Error getting console output: {e}")
            return ""

    def monitor_activity(self) -> Dict[str, Any]:
        """
        Monitor coding activity and return activity metrics.
        
        Returns:
            Dict[str, Any]: Activity metrics including code changes and timing
        """
        current_time = datetime.now()
        current_code = self.get_current_code()
        
        activity_data = {
            "timestamp": current_time.isoformat(),
            "code_length": len(current_code),
            "time_since_last_check": (current_time - self.last_check_time).total_seconds(),
            "has_changes": False,
            "significant_changes": False,
            "complexity": analyze_code_complexity(current_code)
        }
        
        if current_code != self.last_code:
            activity_data["has_changes"] = True
            changes = extract_code_changes(self.last_code, current_code)
            activity_data["changes"] = changes
            activity_data["significant_changes"] = changes.get("significant_change", False)
        
        return activity_data

    def detect_submit_click(self) -> bool:
        """
        Check if the submit button has been clicked by monitoring for test execution.
        
        Returns:
            bool: True if submit was recently clicked
        """
        try:
            if not self.driver:
                return False
            
            # Check if tests are currently running (submit button shows loading state)
            submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Running...')]")
            
            for button in submit_buttons:
                # Check if button is in loading state or disabled
                if button.get_attribute("disabled") or "Running..." in button.text:
                    return True
                    
            # Also check for loading spinner in the test runner area
            loading_spinners = self.driver.find_elements(By.CSS_SELECTOR, ".animate-spin")
            if loading_spinners:
                return True
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error detecting submit click: {e}")
            return False

    def get_latest_test_results(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest test results from the UI after submission.
        
        Returns:
            Optional[Dict[str, Any]]: Test results or None if not available
        """
        try:
            if not self.driver:
                return None
            
            # Wait for test results to appear
            time.sleep(2)
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "score": {"passed": 0, "total": 0},
                "overall_status": "unknown",
                "test_cases": [],
                "raw_output": ""
            }
            
            # Try to get score from the summary text
            try:
                # Look for text like "3/5 Tests Passed" or "All Tests Passed"
                score_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Tests Passed')]")
                for element in score_elements:
                    score_text = element.text
                    if "All Tests Passed" in score_text:
                        # Need to count the total test cases
                        test_case_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Test Case')]")
                        total_tests = len(test_case_buttons)
                        results["score"]["passed"] = total_tests
                        results["score"]["total"] = total_tests
                        results["overall_status"] = "passed"
                        break
                    elif "/" in score_text and "Tests Passed" in score_text:
                        # Extract score like "3/5 Tests Passed"
                        import re
                        match = re.search(r'(\d+)/(\d+)\s+Tests Passed', score_text)
                        if match:
                            results["score"]["passed"] = int(match.group(1))
                            results["score"]["total"] = int(match.group(2))
                            results["overall_status"] = "passed" if int(match.group(1)) == int(match.group(2)) else "failed"
                            break
            except Exception as e:
                logger.debug(f"Could not extract score: {e}")
            
            # Try to get individual test case results from badges
            try:
                test_case_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Test Case')]")
                for i, button in enumerate(test_case_buttons):
                    try:
                        test_result = {
                            "test_case": i + 1,
                            "status": "unknown"
                        }
                        
                        # Look for ✅ or ❌ symbols in the button text
                        button_text = button.text
                        if "✅" in button_text:
                            test_result["status"] = "passed"
                        elif "❌" in button_text:
                            test_result["status"] = "failed"
                        
                        results["test_cases"].append(test_result)
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Could not extract test case details: {e}")
            
            # Try to get the session data from browser storage
            try:
                # Execute JavaScript to get session data from sessionStorage
                session_data_script = """
                const keys = Object.keys(sessionStorage);
                const interviewKey = keys.find(key => key.startsWith('interview_session_'));
                if (interviewKey) {
                    return sessionStorage.getItem(interviewKey);
                }
                return null;
                """
                session_data_str = self.driver.execute_script(session_data_script)
                if session_data_str:
                    import json
                    session_data = json.loads(session_data_str)
                    if "score" in session_data:
                        results["score"] = session_data["score"]
                    if "results" in session_data:
                        results["raw_output"] = str(session_data["results"])
            except Exception as e:
                logger.debug(f"Could not extract session data: {e}")
            
            # Only return results if we got meaningful data
            if results["score"]["total"] > 0 or results["test_cases"] or results["raw_output"]:
                logger.info(f"Extracted test results: {results['score']['passed']}/{results['score']['total']} passed")
                return results
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting test results: {e}")
            return None

    def wait_for_test_completion(self, timeout: int = 30) -> bool:
        """
        Wait for test execution to complete after submit.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if tests completed, False if timeout
        """
        try:
            if not self.driver:
                return False
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if submit button is no longer in loading state
                try:
                    submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit')]")
                    loading_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Running...')]")
                    loading_spinners = self.driver.find_elements(By.CSS_SELECTOR, ".animate-spin")
                    
                    if submit_buttons and not loading_buttons and not loading_spinners:
                        # Tests completed
                        return True
                        
                except Exception:
                    pass
                
                time.sleep(1)
            
            logger.warning(f"Test completion wait timed out after {timeout}s")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for test completion: {e}")
            return False

    def take_screenshot(self, filepath: str) -> bool:
        """
        Take a screenshot of the current browser state.
        
        Args:
            filepath: Path to save the screenshot
            
        Returns:
            bool: True if screenshot saved successfully
        """
        try:
            if not self.driver:
                return False
            
            return self.driver.save_screenshot(filepath)
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False

    def close(self) -> None:
        """Close the browser and clean up resources."""
        try:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
                self.driver = None
                self.wait = None
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


class QuestionManager:
    """
    Manages coding questions and their metadata.
    
    This class handles question selection, difficulty progression,
    and question-specific configuration.
    """

    def __init__(self, questions_file: Optional[str] = None) -> None:
        """
        Initialize the question manager.
        
        Args:
            questions_file: Path to questions JSON file
        """
        self.questions: List[Dict[str, Any]] = []
        self.current_question: Optional[Dict[str, Any]] = None
        
        # Load questions from file or use defaults
        if questions_file and os.path.exists(questions_file):
            self.load_questions_from_file(questions_file)
        else:
            # Try to load from React app's questions file first
            react_questions_path = self._get_react_questions_path()
            if react_questions_path and os.path.exists(react_questions_path):
                self.load_questions_from_file(react_questions_path)
            else:
                self.load_default_questions()
        
        logger.info(f"QuestionManager initialized with {len(self.questions)} questions")

    def _get_react_questions_path(self) -> Optional[str]:
        """
        Get the path to the Next.js app's questions.json file.
        
        Returns:
            Optional[str]: Path to Next.js questions file or None
        """
        try:
            # Get the current script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigate to the Next.js app's questions file
            react_questions_path = os.path.join(
                script_dir, "..", "..", "coeus-frontend", 
                "src", "data", "questions.json"
            )
            return os.path.abspath(react_questions_path)
        except Exception as e:
            logger.error(f"Error getting Next.js questions path: {e}")
            return None

    def load_questions_from_file(self, filepath: str) -> bool:
        """
        Load questions from a JSON file.
        
        Args:
            filepath: Path to the questions file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            questions_data = safe_json_load(filepath)
            if questions_data:
                # Handle both formats: direct array or wrapped in "questions" key
                if isinstance(questions_data, list):
                    self.questions = questions_data
                elif isinstance(questions_data, dict) and "questions" in questions_data:
                    self.questions = questions_data["questions"]
                else:
                    logger.warning(f"Invalid questions file format: {filepath}")
                    return False
                    
                logger.info(f"Loaded {len(self.questions)} questions from {filepath}")
                return True
            else:
                logger.warning(f"Empty or invalid questions file: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error loading questions from {filepath}: {e}")
            return False

    def load_default_questions(self) -> None:
        """Load default questions if no file is provided."""
        self.questions = [
            {
                "id": 1,
                "title": "Two Sum",
                "difficulty": "Easy",
                "description": "Find two numbers that add up to a target sum",
                "estimated_time": 15,
                "tags": ["array", "hash-table"],
                "complexity": {"time": "O(n)", "space": "O(n)"}
            },
            {
                "id": 2,
                "title": "Valid Parentheses",
                "difficulty": "Easy",
                "description": "Check if parentheses are balanced",
                "estimated_time": 10,
                "tags": ["stack", "string"],
                "complexity": {"time": "O(n)", "space": "O(n)"}
            },
            {
                "id": 3,
                "title": "Maximum Subarray",
                "difficulty": "Medium",
                "description": "Find the contiguous subarray with maximum sum",
                "estimated_time": 20,
                "tags": ["array", "dynamic-programming"],
                "complexity": {"time": "O(n)", "space": "O(1)"}
            }
        ]

    def select_question_by_difficulty(self, difficulty: str) -> Optional[Dict[str, Any]]:
        """
        Select a question by difficulty level.
        
        Args:
            difficulty: Desired difficulty level ("Easy", "Medium", "Hard")
            
        Returns:
            Optional[Dict[str, Any]]: Selected question or None
        """
        matching_questions = [
            q for q in self.questions 
            if q.get("difficulty", "").lower() == difficulty.lower()
        ]
        
        if matching_questions:
            import random
            selected = random.choice(matching_questions)
            self.current_question = selected
            logger.info(f"Selected {difficulty} question: {selected['title']}")
            return selected
        
        logger.warning(f"No questions found for difficulty: {difficulty}")
        return None

    def get_question_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific question by ID.
        
        Args:
            question_id: Question ID to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Question data or None
        """
        for question in self.questions:
            if question.get("id") == question_id:
                self.current_question = question
                return question
        
        logger.warning(f"Question not found: {question_id}")
        return None

    def get_next_difficulty_question(self, current_difficulty: str) -> Optional[Dict[str, Any]]:
        """
        Get the next difficulty level question for progression.
        
        Args:
            current_difficulty: Current difficulty level
            
        Returns:
            Optional[Dict[str, Any]]: Next difficulty question or None
        """
        difficulty_order = ["Easy", "Medium", "Hard"]
        
        try:
            current_index = difficulty_order.index(current_difficulty.title())
            if current_index < len(difficulty_order) - 1:
                next_difficulty = difficulty_order[current_index + 1]
                return self.select_question_by_difficulty(next_difficulty)
        except ValueError:
            pass
        
        return None

    def get_available_questions(self) -> List[Dict[str, Any]]:
        """
        Get all available questions.
        
        Returns:
            List[Dict[str, Any]]: List of all questions
        """
        return self.questions.copy()

    def get_question_summary(self, question_id: int) -> str:
        """
        Get a summary string for a question.
        
        Args:
            question_id: Question ID
            
        Returns:
            str: Question summary
        """
        question = self.get_question_by_id(question_id)
        if question:
            return f"{question['title']} ({question['difficulty']}) - Est. {question.get('estimated_time', 'N/A')} min"
        return "Unknown Question"
