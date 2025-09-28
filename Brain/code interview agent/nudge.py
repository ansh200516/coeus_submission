"""
Sophisticated AI Interview Nudge System

This module implements an intelligent interviewer that monitors code editor activity,
provides contextual assistance, and conducts sophisticated technical interviews.

Configuration Parameters (Modifiable):
- INACTIVITY_THRESHOLD: Time in seconds before triggering nudge (default: 25)
- POLLING_INTERVAL: How often to check editor content in seconds (default: 5)
- MAX_INTERVIEW_DURATION: Maximum interview time in seconds (default: 120)

Author: AI Assistant
Date: September 2025
"""

import os
import time
import json
import asyncio
import threading
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pyaudio
import websockets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import our existing modules
import sys
sys.path.append('../lda/rstt')
sys.path.append('../lda/rtts')
sys.path.append('.')

from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()

# ========== CONFIGURATION PARAMETERS ==========
# These can be modified to adjust the system behavior

# Time thresholds (in seconds)
INACTIVITY_THRESHOLD = 10  # Time before triggering nudge
POLLING_INTERVAL = 5       # How often to check editor content
MAX_INTERVIEW_DURATION = 600  # Maximum interview duration

# Browser configuration
BROWSER_HEADLESS = False   # Set to True to run browser in background
REACT_APP_URL = "http://localhost:5173"  # Default Vite dev server URL

# Audio configuration
STT_MODEL = "nova-3"       # Deepgram STT model
TTS_MODEL = "aura-2-thalia-en"  # Deepgram TTS model
SAMPLE_RATE = 24000        # Audio sample rate

# Logging configuration
LOG_LEVEL = logging.DEBUG  # Changed to DEBUG for troubleshooting
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ========== SOPHISTICATED INTERVIEWER PROMPTS ==========

SYSTEM_PROMPT = """You are a senior principal engineer conducting a high-stakes technical interview at a FAANG company. You are known for your rigorous standards and ability to identify top-tier talent through challenging questions.

Your interviewing philosophy:
1. NEVER give away solutions or direct hints
2. Push candidates to their limits through probing questions
3. Test depth of understanding, not just surface knowledge
4. Identify weaknesses in approach and challenge them
5. Maintain professional but intense pressure throughout

Your questioning strategy:
- Ask "What if..." scenarios to test edge case thinking
- Challenge their approach: "Why did you choose this method?"
- Press on time/space complexity: "Can you do better?"
- Test system design thinking: "How would this scale?"
- Question their assumptions: "Are you sure about that?"
- Use Socratic method: lead them to discover issues themselves

Tone and behavior:
- Be respectful but demanding
- Show skepticism when appropriate
- Ask for justification of every decision
- Point out potential issues without giving solutions
- Keep responses brief and focused (20-30 seconds max)
- Make them work for every insight

Remember: You're evaluating for a senior position. The bar is HIGH."""

NUDGE_PROMPTS = {
    "initial_inactivity": """The candidate has been silent for {duration} seconds on this problem:
    Question: {question}
    Their current solution attempt: {candidate_code}
    Solution analysis: {solution_status}
    Previous interactions: {conversation_history}
    
    IMPORTANT: The candidate is only responsible for implementing the solution function/method. All test code and boilerplate is pre-written.
    
    Apply pressure. Ask a probing question about their approach or challenge a potential weakness you see. Don't give hints - make them think harder.""",
    
    "prolonged_inactivity": """The candidate has been stuck for {duration} seconds:
    Question: {question}
    Their solution attempt: {candidate_code}
    Solution progress: {solution_status}
    Previous conversation: {conversation_history}
    
    IMPORTANT: Focus only on their solution implementation, not the boilerplate code.
    
    Time to intensify. Point out a potential issue without solving it. Ask "What if" questions. Challenge their current direction. Make them justify their approach.""",
    
    "code_analysis": """The candidate just made changes to their solution:
    Question: {question}
    Current solution: {candidate_code}
    Previous solution: {previous_candidate_code}
    Progress analysis: {solution_status}
    What they changed: {candidate_progress}
    Interview history: {conversation_history}
    
    IMPORTANT: Only analyze their solution implementation, ignore any boilerplate/test code changes.
    
    Analyze their progress critically. If they're on the right track, push for optimization. If they made an error, guide them to discover it themselves. Ask about edge cases, complexity, or alternative approaches.""",
    
    "follow_up": """The candidate just said: "{candidate_response}"
    Current code: {code}
    Question: {question}
    Full conversation: {conversation_history}
    
    Respond as a tough but fair interviewer. Challenge their response, ask follow-up questions, or point out gaps in their reasoning. Don't let them off easy.""",
    
    "progress_check": """Time check - {elapsed_time} seconds elapsed:
    Current code: {code}
    Question: {question}
    Solution progress: {progress_analysis}
    Conversation so far: {conversation_history}
    
    Assess their progress with high standards. Are they moving efficiently? Missing key insights? Time to add pressure or redirect their focus.""",
    
    "candidate_claims_done": """The candidate claims they are finished:
    Question: {question}
    Their solution: {candidate_code}
    Solution analysis: {solution_status}
    What they said: "{candidate_response}"
    Interview history: {conversation_history}
    
    IMPORTANT: They haven't submitted yet. Encourage them to click "Submit Solution" to run the test cases. Be supportive but remind them testing is crucial.""",
    
    "test_results_feedback": """The candidate just submitted their solution:
    Question: {question}
    Their solution: {candidate_code}
    Test Results: {test_results_summary}
    Score: {score_summary}
    Interview history: {conversation_history}
    
    IMPORTANT: Provide feedback based on their actual test results. If they passed all tests, congratulate them and ask about optimization. If they failed, guide them to debug without giving away the solution."""
}

# ========== TEXT CLEANING UTILITIES ==========

def clean_text_for_speech(text: str) -> str:
    """Clean text to remove markdown formatting and make it speech-friendly"""
    if not text:
        return text
    
    # Remove markdown bold/italic formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__ -> bold
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_ -> italic
    
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # # Header -> Header
    
    # Remove markdown code blocks
    text = re.sub(r'```[^`]*```', 'code block', text, flags=re.DOTALL)  # ```code``` -> code block
    text = re.sub(r'`([^`]+)`', r'\1', text)        # `code` -> code
    
    # Remove markdown links but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [text](url) -> text
    
    # Remove markdown bullet points
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # - item -> item
    
    # Remove markdown numbered lists
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # 1. item -> item
    
    # Remove excessive whitespace and line breaks
    text = re.sub(r'\n+', ' ', text)  # Multiple newlines -> single space
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces -> single space
    
    # Clean up any remaining formatting artifacts
    text = text.replace('**', '').replace('__', '').replace('~~', '')
    
    return text.strip()

# ========== LOGGING SETUP ==========

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# ========== SPEECH-TO-TEXT INTEGRATION ==========

# Import the proven RSTT system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lda', 'rstt'))

try:
    import importlib.util
    rstt_path = os.path.join(os.path.dirname(__file__), '..', 'lda', 'rstt', 'main.py')
    spec = importlib.util.spec_from_file_location("rstt_main", rstt_path)
    rstt_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rstt_module)
    RealTimeSTT = rstt_module.RealTimeSTT
    logger.info("Successfully imported RealTimeSTT from lda/rstt/main.py")
except Exception as e:
    logger.error(f"Could not import RealTimeSTT from lda/rstt/main.py: {e}")
    RealTimeSTT = None

class InterviewSTT:
    """STT wrapper using the proven RSTT implementation"""
    
    def __init__(self):
        self.stt = None
        self.transcription = ""
        self.is_listening = False
        self.collected_transcriptions = []
        
    def setup(self):
        """Setup the STT system"""
        if RealTimeSTT is None:
            logger.error("RealTimeSTT not available")
            return False
            
        def on_transcript(text):
            """Callback for transcript"""
            self.transcription = text
            self.collected_transcriptions.append(text)
            logger.info(f"Transcribed: {text}")
        
        self.stt = RealTimeSTT(process_callback=on_transcript)
        return True
        
    async def start_listening(self) -> bool:
        """Start listening for speech with improved reliability"""
        # Always create a fresh STT instance for reliability
        if not self.setup():
            return False
        
        try:
            # Clear any previous transcriptions
            self.collected_transcriptions = []
            self.transcription = ""
            
            if self.stt.start():
                self.is_listening = True
                logger.info("Started speech recognition using RSTT")
                # Give it a moment to establish connection
                await asyncio.sleep(0.5)
                return True
            else:
                logger.error("Failed to start RSTT")
                return False
                
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return False
    
    def get_transcription(self):
        """Get the latest transcription"""
        result = self.transcription
        # Don't clear here - wait for stop_listening
        return result
    
    def stop_listening(self):
        """Stop listening and return final transcription"""
        if self.stt and self.is_listening:
            try:
                self.stt.stop()
                self.is_listening = False
                logger.info("Stopped speech recognition")
            except Exception as e:
                logger.error(f"Error stopping STT: {e}")
        
        # Return all collected transcriptions joined together
        result = " ".join(self.collected_transcriptions) if self.collected_transcriptions else ""
        
        # Clean up for next use
        self.transcription = ""
        self.collected_transcriptions = []
        self.stt = None  # Force fresh instance next time
        
        return result.strip()

# ========== TEXT-TO-SPEECH INTEGRATION ==========

# Import the proven RTTS system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lda', 'rtts'))

try:
    import importlib.util
    rtts_path = os.path.join(os.path.dirname(__file__), '..', 'lda', 'rtts', 'main.py')
    spec = importlib.util.spec_from_file_location("rtts_main", rtts_path)
    rtts_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rtts_module)
    ProvenDeepgramTTS = rtts_module.DeepgramTTS
    logger.info("Successfully imported DeepgramTTS from lda/rtts/main.py")
except Exception as e:
    logger.error(f"Could not import DeepgramTTS from lda/rtts/main.py: {e}")
    ProvenDeepgramTTS = None

class InterviewTTS:
    """TTS wrapper using the proven RTTS implementation"""
    
    def __init__(self):
        self.tts = None
        
    async def connect(self, model=TTS_MODEL, encoding="linear16", sample_rate=SAMPLE_RATE, retries=3):
        """Connect to Deepgram's TTS WebSocket API with rate limiting handling"""
        if ProvenDeepgramTTS is None:
            logger.error("ProvenDeepgramTTS not available")
            return False
            
        for attempt in range(retries):
            try:
                self.tts = ProvenDeepgramTTS()
                if await self.tts.connect(model=model, encoding=encoding, sample_rate=sample_rate):
                    logger.info(f"Connected to Deepgram TTS with model: {model}")
                    return True
                else:
                    logger.error("Failed to connect to TTS")
                    
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    wait_time = (attempt + 1) * 15  # 15, 30, 45 seconds
                    logger.warning(f"Rate limited by Deepgram. Waiting {wait_time} seconds before retry {attempt + 1}/{retries}")
                    if attempt < retries - 1:  # Don't wait on the last attempt
                        await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"TTS connection error: {e}")
                    
        logger.error("All TTS connection attempts failed due to rate limiting")
        return False

    def setup_audio_playback(self):
        """Setup PyAudio for real-time playback"""
        if self.tts:
            self.tts.setup_audio_playback()

    async def speak(self, text: str):
        """Convert text to speech and play it, or print if TTS unavailable"""
        # Clean the text to remove markdown formatting before speaking
        cleaned_text = clean_text_for_speech(text)
        
        if not self.tts:
            # Fallback to text output when TTS is not available
            logger.info("🎤 INTERVIEWER (TTS unavailable):")
            logger.info(f"   {cleaned_text}")
            print(f"\n🎤 INTERVIEWER: {cleaned_text}\n")
            return True

        try:
            logger.info(f"Speaking: {cleaned_text[:50]}...")
            await self.tts.speak(cleaned_text)
            logger.info("TTS playback completed")
            return True
            
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            # Fallback to text output
            logger.info("🎤 INTERVIEWER (TTS failed):")
            logger.info(f"   {cleaned_text}")
            print(f"\n🎤 INTERVIEWER: {cleaned_text}\n")
            return True

    async def close(self):
        """Close TTS connection"""
        if self.tts:
            await self.tts.close()

# ========== CEREBRAS AI INTEGRATION ==========

class CerebrasInterviewer:
    """AI-powered sophisticated interviewer using Cerebras"""
    
    def __init__(self):
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))
        self.conversation_history = []
        self.code_evolution = []  # Track how code changes over time
        self.interaction_count = 0
        self.start_time = datetime.now()
        self.last_code = ""
    
    def track_code_evolution(self, code: str, question: str):
        """Track how the code evolves over time"""
        if code != self.last_code:
            self.code_evolution.append({
                "timestamp": datetime.now(),
                "code": code,
                "question": question,
                "length": len(code),
                "lines": len(code.split('\n')) if code else 0
            })
            self.last_code = code
    
    def get_progress_analysis(self, code: str) -> str:
        """Analyze the candidate's progress over time"""
        if len(self.code_evolution) < 2:
            return "Initial attempt"
        
        current = self.code_evolution[-1]
        previous = self.code_evolution[-2]
        
        progress_notes = []
        
        # Check if they're making progress
        if current["length"] > previous["length"]:
            progress_notes.append("expanding solution")
        elif current["length"] < previous["length"]:
            progress_notes.append("simplifying approach")
        else:
            progress_notes.append("refining logic")
        
        # Check iteration count
        iterations = len(self.code_evolution)
        if iterations > 5:
            progress_notes.append("multiple iterations - may be struggling")
        elif iterations > 3:
            progress_notes.append("iterating steadily")
        
        return f"Iteration {iterations}: {', '.join(progress_notes)}"
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation so far"""
        if not self.conversation_history:
            return "No previous conversation"
        
        recent_interactions = self.conversation_history[-3:]  # Last 3 interactions
        summary = []
        
        for i, interaction in enumerate(recent_interactions, 1):
            summary.append(f"Exchange {len(self.conversation_history) - len(recent_interactions) + i}: {interaction['response'][:100]}...")
        
        return " | ".join(summary)
    
    def _create_solution_status(self, analysis: Dict[str, Any]) -> str:
        """Create a human-readable solution status summary"""
        if not analysis:
            return "No solution analysis available"
            
        status_parts = []
        
        if analysis.get("candidate_lines", 0) == 0:
            return "No solution implemented yet - only placeholder code"
        
        status_parts.append(f"{analysis['candidate_lines']} lines of solution code")
        
        if analysis.get("has_logic"):
            status_parts.append("contains logic")
        else:
            status_parts.append("minimal logic")
            
        if analysis.get("has_return_statement"):
            status_parts.append("has return statement")
        else:
            status_parts.append("no return statement yet")
            
        features = []
        if analysis.get("has_loops"):
            features.append("loops")
        if analysis.get("has_conditionals"):
            features.append("conditionals")
        if analysis.get("has_data_structures"):
            features.append("data structures")
            
        if features:
            status_parts.append(f"uses: {', '.join(features)}")
            
        complexity = analysis.get("complexity_indicators", [])
        if complexity:
            status_parts.append(f"complexity indicators: {', '.join(complexity)}")
            
        return " | ".join(status_parts)
    
    def _detect_completion_claim(self, response: str) -> bool:
        """Detect if candidate claims to be done"""
        completion_keywords = [
            "done", "finished", "complete", "ready", "submit", 
            "i'm done", "i think it's done", "that should work",
            "ready to submit", "finished coding", "completed",
            "i believe this is correct", "this should be right"
        ]
        
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in completion_keywords)
    
    def _create_test_results_summary(self, test_results: Dict[str, Any]) -> str:
        """Create a summary of test results for the interviewer"""
        if not test_results or not test_results.get("has_results"):
            return "No test results available"
        
        score = test_results.get("score", {})
        passed = score.get("passed", 0)
        total = score.get("total", 0)
        
        summary_parts = [f"Score: {passed}/{total} tests passed"]
        
        if passed == total:
            summary_parts.append("ALL TESTS PASSED ✅")
        else:
            summary_parts.append(f"{total - passed} tests FAILED ❌")
        
        # Add test case details if available
        test_cases = test_results.get("test_cases", [])
        if test_cases:
            failed_cases = [case["name"] for case in test_cases if not case["passed"]]
            if failed_cases:
                summary_parts.append(f"Failed cases: {', '.join(failed_cases)}")
        
        return " | ".join(summary_parts)

    def analyze_situation(self, code: str, question: str, context: Dict[str, Any]) -> str:
        """Analyze the current situation and generate sophisticated interviewer response"""
        
        # Track code changes
        self.track_code_evolution(code, question)
        self.interaction_count += 1
        
        prompt_type = context.get("type", "code_analysis")
        prompt_template = NUDGE_PROMPTS.get(prompt_type, NUDGE_PROMPTS["code_analysis"])
        
        # Get solution analysis if available
        solution_analysis = context.get("solution_analysis", {})
        candidate_code = solution_analysis.get("candidate_code", "No solution implemented yet")
        
        # Create solution status summary
        solution_status = self._create_solution_status(solution_analysis)
        
        # Prepare enhanced context with memory and progress
        format_args = {
            "code": code,
            "candidate_code": candidate_code,
            "question": question,
            "solution_status": solution_status,
            "conversation_history": self.get_conversation_summary(),
            "progress_analysis": self.get_progress_analysis(code),
            "elapsed_time": (datetime.now() - self.start_time).total_seconds(),
            "interaction_count": self.interaction_count
        }
        
        # Add specific context for code analysis
        if prompt_type == "code_analysis":
            if len(self.code_evolution) >= 2:
                format_args["previous_code"] = self.code_evolution[-2]["code"]
            else:
                format_args["previous_code"] = ""
                
            # Add candidate-specific progress information
            changes = context.get("changes", {})
            format_args["previous_candidate_code"] = changes.get("previous_candidate_code", "")
            format_args["candidate_progress"] = changes.get("candidate_progress", "No progress data")
        
        # Add test results feedback context
        elif prompt_type == "test_results_feedback":
            test_results = context.get("test_results", {})
            format_args["test_results_summary"] = self._create_test_results_summary(test_results)
            score = test_results.get("score", {})
            format_args["score_summary"] = f"{score.get('passed', 0)}/{score.get('total', 0)} tests passed"
        
        # Add context items, but don't override our enhanced args
        for key, value in context.items():
            if key not in format_args:
                format_args[key] = value
        
        # Safety check: ensure all required variables have default values
        required_defaults = {
            "changes": "No changes detected",
            "duration": 0,
            "candidate_response": "",
            "previous_code": ""
        }
        
        for key, default_value in required_defaults.items():
            if key not in format_args:
                format_args[key] = default_value
        
        try:
            user_prompt = prompt_template.format(**format_args)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            # Fallback to a simple prompt
            user_prompt = f"Analyze this code situation: {code[:200]}... for question: {question}"
        
        try:
            # Build messages with conversation history for context
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add recent conversation for context (last 2 exchanges)
            recent_history = self.conversation_history[-2:]
            for hist in recent_history:
                messages.append({"role": "assistant", "content": hist["response"]})
            
            # Add current prompt
            messages.append({"role": "user", "content": user_prompt})
            
            stream = self.client.chat.completions.create(
                messages=messages,
                model="gpt-oss-120b",
                stream=True,
                max_completion_tokens=150,  # Shorter responses for tougher interviewing
                temperature=0.8,  # Slightly more creative for challenging questions
                top_p=0.9
            )
            
            response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                response += content
            
            # Store in conversation history with full context
            self.conversation_history.append({
                "timestamp": datetime.now(),
                "context": context,
                "code": code,
                "response": response.strip(),
                "interaction_count": self.interaction_count
            })
            
            logger.info(f"Interviewer response ({self.interaction_count}): {response.strip()[:100]}...")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Cerebras API Error: {e}")
            return "Interesting approach. What's your reasoning behind this direction? Are you considering the time complexity implications here?"

# ========== CODE EDITOR MONITORING ==========

class CodeEditorMonitor:
    """Monitor React code editor for changes"""
    
    def __init__(self, url: str = REACT_APP_URL):
        self.url = url
        self.driver = None
        self.last_code = ""
        self.last_change_time = datetime.now()
        self.current_question = ""
        self.boilerplate_patterns = self._init_boilerplate_patterns()
        self.last_test_results = None
        self.submission_detected = False
        
    def _init_boilerplate_patterns(self):
        """Initialize patterns to identify boilerplate code"""
        return {
            "common_markers": [
                "// Test code - DO NOT MODIFY",
                "# Test code - DO NOT MODIFY", 
                "// DO NOT MODIFY",
                "# DO NOT MODIFY",
                "if __name__ == \"__main__\":",
                "public static void main(",
                "const readline = require('readline');",
                "import sys",
                "import json",
                "BufferedReader br = new BufferedReader",
                "Console.ReadLine()",
                "file_get_contents('php://stdin')"
            ],
            "placeholder_patterns": [
                "// Write your solution here",
                "# Write your solution here", 
                "pass",
                "return new int[]{}",
                "return [];",
                "return false;",
                "return null;",
                "throw new UnsupportedOperationException();"
            ],
            "comment_patterns": [
                r"^//.*",  # Single line comments starting with //
                r"^#.*",   # Single line comments starting with #
                r"/\*.*?\*/",  # Multi-line comments /* */
            ]
        }
    
    def extract_candidate_code(self, full_code: str) -> str:
        """Extract only the candidate's solution code, filtering out boilerplate"""
        import re
        
        lines = full_code.split('\n')
        candidate_lines = []
        in_test_section = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines and pure comments at the start
            if not line_stripped:
                continue
                
            # Check if we've hit the test code section
            if any(marker in line for marker in self.boilerplate_patterns["common_markers"]):
                in_test_section = True
                continue
                
            # Skip everything after test code marker
            if in_test_section:
                continue
                
            # Skip problem description comments
            if (line_stripped.startswith('//') and 
                any(keyword in line_stripped.lower() for keyword in ['given', 'return', 'assume', 'problem'])):
                continue
                
            if (line_stripped.startswith('#') and 
                any(keyword in line_stripped.lower() for keyword in ['given', 'return', 'assume', 'problem'])):
                continue
            
            # Include the line if it's not a pure boilerplate element
            candidate_lines.append(line)
        
        candidate_code = '\n'.join(candidate_lines).strip()
        
        # Remove placeholder patterns
        for placeholder in self.boilerplate_patterns["placeholder_patterns"]:
            candidate_code = candidate_code.replace(placeholder, "")
        
        return candidate_code.strip()
    
    def analyze_solution_progress(self, code: str) -> Dict[str, Any]:
        """Analyze the candidate's actual solution progress"""
        candidate_code = self.extract_candidate_code(code)
        
        analysis = {
            "candidate_code": candidate_code,
            "total_lines": len(code.split('\n')) if code else 0,
            "candidate_lines": len(candidate_code.split('\n')) if candidate_code else 0,
            "has_logic": False,
            "has_return_statement": False,
            "has_loops": False,
            "has_conditionals": False,
            "has_data_structures": False,
            "complexity_indicators": []
        }
        
        if candidate_code:
            lower_code = candidate_code.lower()
            
            # Check for actual logic implementation
            analysis["has_logic"] = len(candidate_code.strip()) > 20 and any(
                keyword in lower_code for keyword in ['for', 'while', 'if', 'return', '=', 'def', 'function']
            )
            
            # Check for return statements (actual solutions)
            analysis["has_return_statement"] = 'return' in lower_code and 'return;' not in lower_code
            
            # Check for control structures
            analysis["has_loops"] = any(keyword in lower_code for keyword in ['for', 'while', 'do'])
            analysis["has_conditionals"] = any(keyword in lower_code for keyword in ['if', 'else', 'elif', 'switch'])
            
            # Check for data structures
            analysis["has_data_structures"] = any(
                ds in lower_code for ds in ['dict', 'map', 'set', 'list', 'array', '{}', '[]', 'hashmap']
            )
            
            # Complexity indicators
            if 'for' in lower_code and lower_code.count('for') > 1:
                analysis["complexity_indicators"].append("nested_loops")
            if any(ds in lower_code for ds in ['map', 'dict', 'hashmap', '{}']):
                analysis["complexity_indicators"].append("hash_table")
            if 'sort' in lower_code:
                analysis["complexity_indicators"].append("sorting")
                
        return analysis
    
    def get_test_results(self) -> Dict[str, Any]:
        """Extract test results from the UI if available with detailed debugging"""
        test_results = {
            "has_results": False,
            "score": {"passed": 0, "total": 0},
            "all_passed": False,
            "test_cases": [],
            "submission_time": None
        }
        
        try:
            # Multiple strategies to find test results
            logger.debug("Attempting to extract test results from UI...")
            
            # Strategy 1: Look for score text with multiple selectors
            score_selectors = [
                "//text()[contains(., 'Score:')]/..",
                "//*[contains(text(), 'Score:')]",
                "//*[contains(text(), 'Score')]",
                "//*[contains(text(), '/')]",  # Look for X/Y pattern
                "//div[contains(@class, 'score')]",
                "//span[contains(text(), '/')]"
            ]
            
            for selector in score_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text.strip()
                        logger.debug(f"Found potential score element: '{text}'")
                        
                        # Parse various score formats
                        if "Score:" in text:
                            score_part = text.split("Score:")[1].strip().split()[0]
                            if "/" in score_part:
                                passed, total = map(int, score_part.split("/"))
                                test_results["score"] = {"passed": passed, "total": total}
                                test_results["has_results"] = True
                                test_results["all_passed"] = passed == total
                                test_results["submission_time"] = datetime.now()
                                logger.info(f"Found score: {passed}/{total}")
                                break
                        elif "/" in text and text.count("/") == 1:
                            # Direct X/Y format
                            try:
                                parts = text.strip().split("/")
                                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                                    passed, total = int(parts[0]), int(parts[1])
                                    test_results["score"] = {"passed": passed, "total": total}
                                    test_results["has_results"] = True
                                    test_results["all_passed"] = passed == total
                                    test_results["submission_time"] = datetime.now()
                                    logger.info(f"Found score format X/Y: {passed}/{total}")
                                    break
                            except:
                                continue
                    
                    if test_results["has_results"]:
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Strategy 2: Look for PASSED/FAILED badges
            if not test_results["has_results"]:
                try:
                    badge_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'PASSED') or contains(text(), 'FAILED')]")
                    for badge in badge_elements:
                        text = badge.text.strip()
                        if "PASSED" in text or "FAILED" in text:
                            test_results["has_results"] = True
                            test_results["all_passed"] = "PASSED" in text
                            logger.info(f"Found result badge: {text}")
                            break
                except:
                    pass
            
            # Strategy 3: Look for progress bar or percentage
            if not test_results["has_results"]:
                try:
                    progress_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '%') or contains(@class, 'progress')]")
                    for element in progress_elements:
                        text = element.text.strip()
                        if "%" in text:
                            logger.debug(f"Found progress indicator: {text}")
                            test_results["has_results"] = True
                            # Try to extract percentage
                            try:
                                percentage = float(text.replace("%", "").strip())
                                test_results["all_passed"] = percentage == 100.0
                            except:
                                pass
                            break
                except:
                    pass
            
            # Strategy 4: Look for individual test case results
            test_case_selectors = [
                "//button[contains(text(), 'Test Case')]",
                "//*[contains(text(), 'Test Case')]",
                "//div[contains(@class, 'accordion')]//button",
                "//*[contains(text(), 'PASS') or contains(text(), 'FAIL')]"
            ]
            
            for selector in test_case_selectors:
                try:
                    test_case_elements = self.driver.find_elements(By.XPATH, selector)
                    for element in test_case_elements:
                        text = element.text.strip()
                        if "Test Case" in text or "PASS" in text or "FAIL" in text:
                            case_info = {
                                "name": text,
                                "passed": "PASS" in text and "FAIL" not in text
                            }
                            test_results["test_cases"].append(case_info)
                            logger.debug(f"Found test case: {text}")
                    
                    if test_results["test_cases"]:
                        test_results["has_results"] = True
                        passed_count = sum(1 for case in test_results["test_cases"] if case["passed"])
                        total_count = len(test_results["test_cases"])
                        if test_results["score"]["total"] == 0:  # Only update if we haven't found score elsewhere
                            test_results["score"] = {"passed": passed_count, "total": total_count}
                            test_results["all_passed"] = passed_count == total_count
                        break
                except Exception as e:
                    logger.debug(f"Test case selector {selector} failed: {e}")
                    continue
            
            # Log final results
            if test_results["has_results"]:
                logger.info(f"Successfully extracted test results: {test_results['score']}")
            else:
                logger.debug("No test results found in UI")
                
            return test_results
            
        except Exception as e:
            logger.error(f"Error getting test results: {e}")
            return {"has_results": False, "score": {"passed": 0, "total": 0}, "all_passed": False, "test_cases": []}
    
    def check_for_submission(self) -> bool:
        """Check if a submission/test run was triggered with detailed debugging"""
        try:
            logger.debug("Checking for submission...")
            
            # Strategy 1: Look for submit button states
            submit_selectors = [
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Running')]",
                "//button[contains(text(), 'Loading')]",
                "//*[contains(@aria-label, 'submit') or contains(@aria-label, 'Submit')]"
            ]
            
            for selector in submit_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        text = button.text.strip()
                        classes = button.get_attribute("class") or ""
                        aria_label = button.get_attribute("aria-label") or ""
                        
                        logger.debug(f"Found button: text='{text}', classes='{classes}', aria='{aria_label}'")
                        
                        if ("Running" in text or "Loading" in text or 
                            "loading" in classes or "disabled" in classes or
                            button.get_attribute("disabled")):
                            logger.info("Found submission in progress")
                            return True
                except Exception as e:
                    logger.debug(f"Submit selector {selector} failed: {e}")
                    continue
            
            # Strategy 2: Check for new test results since last check
            current_results = self.get_test_results()
            
            if current_results["has_results"]:
                logger.debug(f"Found test results: {current_results['score']}")
                
                # Compare with last results
                if not self.last_test_results:
                    logger.info("First time seeing test results - submission detected")
                    self.last_test_results = current_results
                    return True
                elif (current_results["submission_time"] and 
                      self.last_test_results.get("submission_time") and
                      current_results["submission_time"] != self.last_test_results["submission_time"]):
                    logger.info("New test results detected - submission occurred")
                    self.last_test_results = current_results  
                    return True
                elif (current_results["score"] != self.last_test_results.get("score", {})):
                    logger.info("Score changed - new submission detected")
                    self.last_test_results = current_results
                    return True
            
            # Strategy 3: Look for any indication of test execution
            execution_indicators = [
                "//text()[contains(., 'Running')]",
                "//text()[contains(., 'test')]",
                "//*[contains(@class, 'spinner') or contains(@class, 'loading')]",
                "//div[contains(@class, 'progress')]"
            ]
            
            for selector in execution_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text.strip().lower()
                        if ("running" in text and "test" in text) or "executing" in text:
                            logger.info(f"Found execution indicator: {text}")
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for submission: {e}")
            return False
    
    def debug_page_content(self):
        """Debug method to print all text content on the page"""
        try:
            logger.info("=== DEBUGGING PAGE CONTENT ===")
            
            # Get all text elements
            all_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
            
            for i, element in enumerate(all_elements[:50]):  # Limit to first 50 elements
                try:
                    text = element.text.strip()
                    tag = element.tag_name
                    classes = element.get_attribute("class") or ""
                    
                    if text and len(text) > 0:
                        logger.info(f"{i}: <{tag} class='{classes}'>{text}</{tag}>")
                except:
                    continue
                    
            logger.info("=== END PAGE CONTENT ===")
            
        except Exception as e:
            logger.error(f"Error debugging page content: {e}")
        
    def setup_browser(self):
        """Setup Chrome browser for monitoring"""
        chrome_options = Options()
        if BROWSER_HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(self.url)
            logger.info(f"Browser setup complete, navigated to {self.url}")
            
            # Wait for the React app to fully load
            logger.info("Waiting for React app to load...")
            time.sleep(5)  # Give React time to initialize
            
            # Wait for Monaco editor to be available
            wait = WebDriverWait(self.driver, 30)
            try:
                # Wait for Monaco to be loaded in the global scope
                wait.until(lambda driver: driver.execute_script("return typeof window.monaco !== 'undefined'"))
                logger.info("Monaco editor detected")
            except TimeoutException:
                logger.warning("Monaco editor not detected, will try alternative methods")
            
            return True
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return False
    
    def get_current_code(self) -> str:
        """Extract current code from Monaco editor"""
        try:
            # Wait for Monaco editor to load
            wait = WebDriverWait(self.driver, 5)
            
            # First try the most direct approach with Monaco API
            try:
                code = self.driver.execute_script("""
                    const editors = window.monaco?.editor?.getEditors();
                    if (editors && editors.length > 0) {
                        return editors[0].getValue();
                    }
                    return '';
                """)
                
                if code and len(code.strip()) > 0:
                    logger.debug(f"Got code via Monaco API: {len(code)} chars")
                    return code
                else:
                    logger.debug("Monaco API returned empty code")
                    
            except Exception as e:
                logger.debug(f"Monaco API failed: {e}")
            
            # Try multiple selectors for Monaco editor
            selectors = [
                ".monaco-editor .view-lines",
                ".monaco-editor-background", 
                "[data-testid='monaco-editor']",
                ".monaco-editor"
            ]
            
            for selector in selectors:
                try:
                    editor_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.debug(f"Found element with selector: {selector}")
                    
                    # Try getting the text content
                    text = editor_element.get_attribute("textContent") or ""
                    if text and len(text.strip()) > 0:
                        logger.debug(f"Got code via {selector}: {len(text)} chars")
                        return text
                        
                except TimeoutException:
                    logger.debug(f"Timeout for selector: {selector}")
                    continue
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            logger.warning("Could not extract code from any selector")
            return ""
                
        except Exception as e:
            logger.error(f"Error getting code: {e}")
            return ""
    
    def get_current_question(self) -> str:
        """Extract current question being worked on"""
        try:
            # Look for question title or content
            selectors = [
                "[data-testid='question-title']",
                ".question-title",
                "h1", "h2", "h3"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and len(text) > 10:  # Reasonable question length
                        return text
                except NoSuchElementException:
                    continue
            
            return "Unknown Problem"
            
        except Exception as e:
            logger.error(f"Error getting question: {e}")
            return "Unknown Problem"
    
    def check_for_changes(self) -> Dict[str, Any]:
        """Check if code has changed and return status with candidate-only analysis"""
        current_code = self.get_current_code()
        current_question = self.get_current_question()
        
        now = datetime.now()
        changed = current_code != self.last_code
        
        # Analyze candidate's actual solution progress
        solution_analysis = self.analyze_solution_progress(current_code)
        
        # Check for test submissions and results
        submission_detected = self.check_for_submission()
        test_results = self.get_test_results() if submission_detected else None
        
        if changed:
            self.last_change_time = now
            previous_analysis = self.analyze_solution_progress(self.last_code)
            
            changes = {
                "previous": self.last_code,
                "current": current_code,
                "previous_candidate_code": previous_analysis.get("candidate_code", ""),
                "current_candidate_code": solution_analysis.get("candidate_code", ""),
                "diff_length": len(current_code) - len(self.last_code),
                "candidate_progress": {
                    "lines_added": solution_analysis["candidate_lines"] - previous_analysis["candidate_lines"],
                    "logic_improved": solution_analysis["has_logic"] and not previous_analysis["has_logic"],
                    "new_structures": len(solution_analysis["complexity_indicators"]) - len(previous_analysis["complexity_indicators"])
                }
            }
            self.last_code = current_code
        else:
            changes = None
        
        inactive_duration = (now - self.last_change_time).total_seconds()
        
        return {
            "code": current_code,
            "question": current_question,
            "changed": changed,
            "changes": changes,
            "inactive_duration": inactive_duration,
            "timestamp": now,
            "solution_analysis": solution_analysis,  # New: candidate-specific analysis
            "submission_detected": submission_detected,  # New: submission detection
            "test_results": test_results  # New: test results if available
        }
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

# ========== MAIN NUDGE SYSTEM ==========

class InterviewNudgeSystem:
    """Main system orchestrating the interview nudging"""
    
    def __init__(self):
        self.monitor = CodeEditorMonitor()
        self.stt = InterviewSTT()
        self.tts = InterviewTTS()
        self.interviewer = CerebrasInterviewer()
        self.is_running = False
        self.start_time = None
        self.interaction_count = 0
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Interview Nudge System...")
        
        # Setup browser monitoring
        if not self.monitor.setup_browser():
            logger.error("Failed to setup browser monitoring")
            return False
        
        # Setup TTS with fallback
        tts_connected = await self.tts.connect()
        if tts_connected:
            self.tts.setup_audio_playback()
            logger.info("TTS connected successfully")
        else:
            logger.warning("TTS failed to connect - continuing with text-only mode")
            self.tts = None  # Disable TTS for this session
        
        logger.info("System initialization complete")
        return True
    
    async def start_interview(self):
        """Start the interview nudging system"""
        if not await self.initialize():
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("Starting interview monitoring...")
        
        # Start initial greeting 
        greeting_text = "Hello! I'm your AI interviewer. I'll be monitoring your progress and providing assistance as needed. Good luck!"
        
        if self.tts:
            # Try TTS first
            try:
                await asyncio.wait_for(
                    self.tts.speak(greeting_text), 
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                logger.warning("Initial greeting timed out, continuing with monitoring...")
            except Exception as e:
                logger.error(f"Initial greeting failed: {e}, continuing with monitoring...")
        else:
            # TTS unavailable, just print the greeting
            print(f"\n🎤 INTERVIEWER: {greeting_text}\n")
        
        logger.info("Starting main monitoring loop...")
        
        try:
            while self.is_running:
                await self._monitoring_cycle()
                await asyncio.sleep(POLLING_INTERVAL)
                
                # Check total time limit
                elapsed = (datetime.now() - self.start_time).total_seconds()
                if elapsed > MAX_INTERVIEW_DURATION:
                    await self._end_interview("time_limit")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Interview interrupted by user")
        except Exception as e:
            logger.error(f"Interview error: {e}")
        finally:
            await self.cleanup()
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        status = self.monitor.check_for_changes()
        
        # DEBUG: Log the status every cycle
        logger.info(f"Monitor Status - Inactive: {status['inactive_duration']:.1f}s, Changed: {status['changed']}, Code Length: {len(status['code'])}, Submission: {status['submission_detected']}")
        
        # Check for test results first (highest priority)
        if status["submission_detected"] and status["test_results"]:
            should_nudge = True
            nudge_type = "test_results_feedback"
            context = {
                "type": nudge_type,
                "code": status["code"],
                "question": status["question"],
                "solution_analysis": status["solution_analysis"],
                "test_results": status["test_results"]
            }
            
            logger.info(f"TEST RESULTS AVAILABLE: {status['test_results']['score']['passed']}/{status['test_results']['score']['total']} passed")
        
        # Debug: If submission detected but no test results, debug the page
        elif status["submission_detected"] and not status["test_results"]:
            logger.warning("Submission detected but no test results found - debugging page content")
            self.monitor.debug_page_content()
        
        # Determine if we need to intervene for other reasons
        else:
            should_nudge = False
            nudge_type = None
            context = {}
        
        if status["inactive_duration"] >= INACTIVITY_THRESHOLD:
            should_nudge = True
            if status["inactive_duration"] < INACTIVITY_THRESHOLD * 2:
                nudge_type = "initial_inactivity"
            else:
                nudge_type = "prolonged_inactivity"
            
            context = {
                "type": nudge_type,
                "duration": status["inactive_duration"],
                "code": status["code"],
                "question": status["question"],
                "solution_analysis": status["solution_analysis"]
            }
            
            logger.info(f"NUDGE TRIGGERED: {nudge_type} after {status['inactive_duration']:.1f}s")
        
        elif status["changed"]:
            # Check if there's meaningful candidate code change (not just boilerplate)
            candidate_lines = status["solution_analysis"].get("candidate_lines", 0)
            if candidate_lines > 0 or len(status["code"]) > 50:
                should_nudge = True
                nudge_type = "code_analysis"
                context = {
                    "type": nudge_type,
                    "code": status["code"],
                    "question": status["question"],
                    "changes": status["changes"],
                    "solution_analysis": status["solution_analysis"]
                }
                
                logger.info(f"CODE ANALYSIS TRIGGERED: Candidate solution changed, {candidate_lines} lines of solution code")
        
        if should_nudge:
            await self._provide_assistance(context)
    
    async def _provide_assistance(self, context: Dict[str, Any]):
        """Provide AI-powered assistance"""
        self.interaction_count += 1
        
        logger.info(f"Providing assistance (interaction #{self.interaction_count})")
        
        # Generate AI response
        response = self.interviewer.analyze_situation(
            context["code"],
            context["question"],
            context
        )
        
        # Speak the response
        await self.tts.speak(response)
        
        # Listen for candidate response
        await self._listen_for_response()
    
    async def _listen_for_response(self):
        """Listen for candidate's verbal response"""
        logger.info("Listening for candidate response...")
        
        try:
            # Start listening with shorter window to avoid timeouts
            if await self.stt.start_listening():
                # Listen for 8 seconds (reduced from 10 to avoid timeout issues)
                logger.info("Listening for 8 seconds...")
                await asyncio.sleep(8)
                
                # Stop listening and get final transcription
                response = self.stt.stop_listening()
                
                if response and len(response.strip()) > 0:
                    logger.info(f"Candidate said: '{response}'")
                    
                    # Check if candidate claims they're done
                    if self.interviewer._detect_completion_claim(response):
                        context = {
                            "type": "candidate_claims_done",
                            "candidate_response": response,
                            "code": self.monitor.get_current_code(),
                            "question": self.monitor.get_current_question(),
                            "solution_analysis": self.monitor.analyze_solution_progress(self.monitor.get_current_code())
                        }
                        logger.info("CANDIDATE CLAIMS DONE - encouraging submission")
                    else:
                        # Regular follow-up to maintain interview pressure
                        context = {
                            "type": "follow_up",
                            "candidate_response": response,
                            "code": self.monitor.get_current_code(),
                            "question": self.monitor.get_current_question(),
                            "solution_analysis": self.monitor.analyze_solution_progress(self.monitor.get_current_code())
                        }
                    
                    follow_up = self.interviewer.analyze_situation(
                        context["code"],
                        context["question"],
                        context
                    )
                    
                    await self.tts.speak(follow_up)
                else:
                    logger.info("No response from candidate - continuing monitoring")
                    
        except Exception as e:
            logger.error(f"Error listening for response: {e}")
            # Continue monitoring even if STT fails
    
    async def _end_interview(self, reason: str):
        """End the interview"""
        self.is_running = False
        
        if reason == "time_limit":
            message = "Time's up! Thank you for participating in this coding interview."
        else:
            message = "Interview completed. Thank you for your time!"
        
        await self.tts.speak(message)
        logger.info(f"Interview ended: {reason}")
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.monitor:
            self.monitor.close()
        
        if self.tts:
            await self.tts.close()
        
        if self.stt:
            self.stt.stop_listening()

# ========== TESTING FUNCTIONS ==========

def test_text_cleaning():
    """Test text cleaning functionality"""
    print("Testing text cleaning for speech...")
    
    test_cases = [
        ("**Bold text** and *italic text*", "Bold text and italic text"),
        ("# Header\nSome content", "Header Some content"),
        ("Here's some `code` and a ```code block```", "Here's some code and a code block"),
        ("Check this [link](http://example.com) out", "Check this link out"),
        ("- First item\n- Second item", "First item Second item"),
        ("1. First step\n2. Second step", "First step Second step"),
        ("**Topic**: What if you need to optimize this?", "Topic: What if you need to optimize this?"),
        ("Are you considering the time complexity? **O(n²)** vs **O(n log n)**", "Are you considering the time complexity? O(n²) vs O(n log n)"),
        ("```python\ndef solution():\n    pass\n```", "code block"),
    ]
    
    print("Testing various markdown patterns:")
    all_passed = True
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = clean_text_for_speech(input_text)
        passed = result == expected
        status = "✅" if passed else "❌"
        
        print(f"{status} Test {i}: {passed}")
        print(f"   Input:    '{input_text}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{result}'")
        print()
        
        if not passed:
            all_passed = False
    
    if all_passed:
        print("🎉 All text cleaning tests passed!")
    else:
        print("⚠️  Some text cleaning tests failed")
    
    return all_passed

def test_browser_monitoring():
    """Test browser monitoring functionality"""
    print("Testing browser monitoring...")
    
    monitor = CodeEditorMonitor()
    if not monitor.setup_browser():
        print("❌ Browser setup failed")
        return False
    
    try:
        print("✅ Browser setup successful")
        print("Waiting 5 seconds for page to load...")
        time.sleep(5)
        
        # Test code extraction
        code = monitor.get_current_code()
        question = monitor.get_current_question()
        
        print(f"📝 Code extracted: {len(code)} characters")
        print(f"🎯 Question: {question}")
        
        if len(code) > 0:
            print("✅ Code extraction working")
            print(f"First 100 chars: {code[:100]}...")
        else:
            print("❌ Code extraction failed - no code found")
        
        # Test change detection
        print("\nTesting change detection for 30 seconds...")
        for i in range(6):
            status = monitor.check_for_changes()
            print(f"Cycle {i+1}: Inactive for {status['inactive_duration']:.1f}s, Changed: {status['changed']}, Code length: {len(status['code'])}")
            time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        monitor.close()

# ========== MAIN EXECUTION ==========

async def main():
    """Main entry point"""
    print(f"""
    🎯 AI Interview Nudge System
    ================================
    
    Configuration:
    - Inactivity Threshold: {INACTIVITY_THRESHOLD} seconds
    - Polling Interval: {POLLING_INTERVAL} seconds  
    - Max Duration: {MAX_INTERVIEW_DURATION} seconds
    - React App URL: {REACT_APP_URL}
    
    Starting system...
    """)
    
    system = InterviewNudgeSystem()
    await system.start_interview()

if __name__ == "__main__":
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("🧪 Running browser monitoring test...")
            test_browser_monitoring()
        elif sys.argv[1] == "test-text":
            print("🧪 Running text cleaning test...")
            test_text_cleaning()
        elif sys.argv[1] == "test-all":
            print("🧪 Running all tests...")
            print("\n1. Testing text cleaning:")
            text_result = test_text_cleaning()
            print(f"\n2. Testing browser monitoring:")
            browser_result = test_browser_monitoring()
            print(f"\n📋 Test Results:")
            print(f"   Text Cleaning: {'✅ PASSED' if text_result else '❌ FAILED'}")
            print(f"   Browser Monitoring: {'✅ PASSED' if browser_result else '❌ FAILED'}")
        else:
            print("Available test commands:")
            print("  python nudge.py test           - Test browser monitoring")
            print("  python nudge.py test-text      - Test text cleaning")
            print("  python nudge.py test-all       - Run all tests")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n\nSystem stopped by user")
        except Exception as e:
            print(f"System error: {e}")
            logger.error(f"Fatal error: {e}")
