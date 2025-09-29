import argparse
import asyncio
import datetime
import json
import logging
import os
import random
import subprocess
import sys
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras

from agents import InterviewerAgent, LieDetectionAgent
from audio import AudioManager, InterviewSTT, InterviewTTS
from config import (
    AUDIO_CACHE_DIR,
    LIE_CONFIDENCE_THRESHOLD,
    LISTENING_WINDOW,
    LOG_FORMAT,
    LOG_LEVEL,
    MAX_INTERVIEW_DURATION,
)
from knowledge_db import KnowledgeDatabase
from shared_state import AudioState
from utils import find_project_root, strip_markdown, sanitize_llm_json_output

load_dotenv()

# ========== LOGGING SETUP ==========
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


# ========== SYSTEM AUDIO PLAYBACK ==========
async def _play_system_audio(file_path: str) -> None:
    """Play audio file using system-level audio playback after all processes are closed.
    
    Args:
        file_path: Path to the audio file to play
    """
    try:
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            cmd = ["afplay", file_path]
        elif system == "linux":
            # Try different audio players in order of preference
            for player in ["paplay", "aplay", "mpg123", "cvlc"]:
                if subprocess.run(["which", player], capture_output=True).returncode == 0:
                    if player == "cvlc":
                        cmd = [player, "--intf", "dummy", "--play-and-exit", file_path]
                    else:
                        cmd = [player, file_path]
                    break
            else:
                logger.error("No suitable audio player found on Linux")
                return
        elif system == "windows":
            # Use Windows Media Player or PowerShell
            cmd = ["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync();"]
        else:
            logger.error(f"Unsupported system: {system}")
            return
        
        logger.info(f"Playing audio with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("System audio playback completed successfully")
        else:
            logger.error(f"Audio playback failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("Audio playback timed out")
    except Exception as e:
        logger.error(f"Error in system audio playback: {e}", exc_info=True)


# ========== UNIFIED SCRAPER INTEGRATION ==========
async def run_unified_scraper(linkedin_url: str, resume_pdf_path: str, project_root: str) -> Optional[str]:
    """
    Run the unified scraper to collect candidate data.
    
    Args:
        linkedin_url: LinkedIn profile URL to scrape
        resume_pdf_path: Path to resume PDF file
        project_root: Project root directory
        
    Returns:
        Path to the combined data file if successful, None otherwise
    """
    try:
        unified_scraper_path = os.path.join(project_root, "Brain", "lda", "unified_scraper.py")
        
        if not os.path.exists(unified_scraper_path):
            logger.error(f"Unified scraper not found: {unified_scraper_path}")
            return None
        
        logger.info("🚀 Running unified scraper to collect candidate data...")
        
        # Build command arguments
        cmd = [sys.executable, unified_scraper_path]
        if linkedin_url:
            cmd.extend(["--linkedin-url", linkedin_url])
        if resume_pdf_path:
            cmd.extend(["--resume-pdf", resume_pdf_path])
        
        # Run the unified scraper
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Unified scraper completed successfully")
            
            # Find the latest combined data file
            lda_logs_dir = os.path.join(project_root, "Brain", "lda", "lda_logs")
            if os.path.exists(lda_logs_dir):
                combined_files = [
                    f for f in os.listdir(lda_logs_dir) 
                    if f.startswith("combined_candidate_data_") and f.endswith(".json")
                ]
                if combined_files:
                    latest_file = max(
                        [os.path.join(lda_logs_dir, f) for f in combined_files],
                        key=os.path.getmtime
                    )
                    logger.info(f"📄 Found combined data file: {os.path.basename(latest_file)}")
                    return latest_file
            
            logger.warning("⚠️ Unified scraper completed but no combined data file found")
            return None
        else:
            logger.error(f"❌ Unified scraper failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Unified scraper timed out")
        return None
    except Exception as e:
        logger.error(f"❌ Error running unified scraper: {e}")
        return None


async def prompt_for_candidate_data() -> Dict[str, Optional[str]]:
    """
    Prompt user for candidate data inputs.
    
    Returns:
        Dictionary with candidate_name, gender, linkedin_url and resume_pdf_path
    """
    print("\n" + "="*60)
    print("📋 Please provide candidate information:")
    print("="*60)
    
    # Get candidate name
    candidate_name = input("👤 Candidate Name: ").strip()
    if not candidate_name:
        candidate_name = "Unknown Candidate"
    
    # Get gender
    gender = input("⚧ Gender (or press Enter to skip): ").strip()
    if not gender:
        gender = None
    
    # Get LinkedIn URL
    linkedin_url = input("🔗 LinkedIn Profile URL (or press Enter to skip): ").strip()
    if not linkedin_url:
        linkedin_url = None
    elif not linkedin_url.startswith("https://"):
        linkedin_url = None
        print("⚠️  Invalid LinkedIn URL format. Skipping LinkedIn scraping.")
    
    # Get resume PDF path
    resume_pdf_path = input("📄 Resume PDF file path (or press Enter to skip): ").strip()
    if not resume_pdf_path:
        resume_pdf_path = None
    elif not os.path.exists(resume_pdf_path):
        resume_pdf_path = None
        print(f"⚠️  Resume file not found. Skipping resume parsing.")
    elif not resume_pdf_path.lower().endswith('.pdf'):
        resume_pdf_path = None
        print("⚠️  File is not a PDF. Skipping resume parsing.")
    
    return {
        "candidate_name": candidate_name,
        "gender": gender,
        "linkedin_url": linkedin_url,
        "resume_pdf_path": resume_pdf_path
    }


# ========== FILLER WORD FUNCTION ==========
async def play_random_filler(
    audio_manager: Optional[AudioManager], filler_paths: List[str]
):
    """
    Schedules a random filler word from the cache for playback.
    """
    if not filler_paths or not audio_manager:
        return

    filler_path = random.choice(filler_paths)
    logger.debug("Scheduling filler audio: %s", filler_path)
    try:
        # Schedule the WAV file path for playback. The AudioManager's worker
        # will pick it up and play it from the queue.
        await audio_manager.schedule_playback(filler_path)
    except Exception as e:
        logger.error("Could not schedule filler audio %s: %s", filler_path, e)


# ========== MAIN ORCHESTRATION ==========
async def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the interview agent.")
    parser.add_argument("--candidate-name", type=str, help="Candidate's name")
    parser.add_argument("--gender", type=str, help="Candidate's gender")
    parser.add_argument("--linkedin-url", type=str, help="LinkedIn profile URL")
    parser.add_argument("--resume-pdf", type=str, help="Path to resume PDF")
    return parser.parse_args()


async def main():
    """Main entry point for the interactive interviewer agent."""
    args = await get_args()

    interview_mode = "grilling"  # Can be "friendly" or "grilling"
    logger.info("Initializing %s Interviewer Agent...", interview_mode)

    # --- Filler Words Cache ---
    filler_words_paths = []
    if os.path.exists(AUDIO_CACHE_DIR):
        filler_words_paths = [
            os.path.join(AUDIO_CACHE_DIR, f)
            for f in os.listdir(AUDIO_CACHE_DIR)
            if f.endswith(".wav")
        ]
    if filler_words_paths:
        logger.info("Loaded %d filler words from cache.", len(filler_words_paths))
    else:
        logger.warning(
            "No filler words found in %s. Latency will be more noticeable.",
            AUDIO_CACHE_DIR,
        )

    # --- State accessible in finally block ---
    stt: Optional[InterviewSTT] = None
    audio_manager: Optional[AudioManager] = None
    interviewer_agent: Optional[InterviewerAgent] = None
    knowledge_db: Optional[KnowledgeDatabase] = None
    conversation_history: List[Dict[str, str]] = []

    try:
        project_root = find_project_root()
        if not project_root:
            logger.error("Could not find project root. Cannot locate data files.")
            return

        # --- LLM & Agent Setup ---
        llm_client = ChatCerebras(
            model="gpt-oss-120b",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            temperature=0.8,
            max_tokens=1024, # Increased for potentially longer summaries
        )

        knowledge_db = KnowledgeDatabase()
        
        # Check for LinkedIn credentials first
        linkedin_email = os.getenv("LINKEDIN_EMAIL")
        linkedin_password = os.getenv("LINKEDIN_PASSW")
        
        if not (linkedin_email and linkedin_password):
            print("⚠️  No LinkedIn credentials found in environment variables.")
            print("     Set LINKEDIN_EMAIL and LINKEDIN_PASSW to enable LinkedIn data collection.")
        
        # Always prompt for candidate information at the start
        print("\n🎯 Welcome to the Interview System!")
        print("Let's start by setting up the candidate information.")
        
        # Always collect new candidate data (no existing data prompt)
        print("\n📂 Starting fresh candidate data collection...")
        print("🔄 Collecting new candidate data...")
        
        if args.candidate_name:
            candidate_data = {
                "candidate_name": args.candidate_name,
                "gender": args.gender,
                "linkedin_url": args.linkedin_url,
                "resume_pdf_path": args.resume_pdf,
            }
        else:
            # Prompt for new candidate data
            candidate_data = await prompt_for_candidate_data()
        
        if candidate_data["linkedin_url"] or candidate_data["resume_pdf_path"]:
            if linkedin_email and linkedin_password:
                print("\n🚀 Collecting candidate data...")
                # Run unified scraper with the provided data
                combined_file = await run_unified_scraper(
                    candidate_data["linkedin_url"],
                    candidate_data["resume_pdf_path"],
                    project_root
                )
                
                if combined_file:
                    print(f"✅ Successfully collected candidate data via unified scraper")
                    # Load the newly created combined data
                    knowledge_db.load_combined_candidate_data(combined_file)
                else:
                    print("❌ Failed to collect candidate data via unified scraper")
                    # Try to load any existing files as fallback
                    print("🔄 Trying to load any existing candidate files as fallback...")
                    loaded_files = knowledge_db.auto_load_latest_candidate_data(project_root)
            else:
                print("❌ Cannot collect LinkedIn data without credentials")
                if candidate_data["resume_pdf_path"]:
                    print("📄 Will try to parse resume only...")
                    # TODO: Add resume-only parsing here if needed
        else:
            print("⚠️  No candidate information provided.")
            # Try to load any existing files as fallback
            print("🔄 Trying to load any existing candidate files...")
            loaded_files = knowledge_db.auto_load_latest_candidate_data(project_root)
        
        # Check if we successfully loaded candidate data
        candidate_entries = [entry for entry in knowledge_db.entries if entry.source in ["linkedin", "resume"]]
        if candidate_entries:
            print(f"✅ Loaded {len(candidate_entries)} candidate data entries")
            # Show breakdown
            linkedin_entries = [e for e in candidate_entries if e.source == "linkedin"]
            resume_entries = [e for e in candidate_entries if e.source == "resume"]
            print(f"   📱 LinkedIn: {len(linkedin_entries)} entries")
            print(f"   📄 Resume: {len(resume_entries)} entries")
        else:
            print("⚠️  No candidate data available. Interview will proceed with job description only.")
            print("     The interview may be limited without candidate background information.")

        jd_path = os.path.join(project_root, "job_description.txt")
        if os.path.exists(jd_path):
            await knowledge_db.load_job_description(jd_path)
        else:
            logger.warning("job_description.txt not found, proceeding without it.")

        lie_agent = LieDetectionAgent(knowledge_db, llm_client)
        interviewer_agent = InterviewerAgent(knowledge_db, llm_client, mode=interview_mode)

        # --- Audio Setup ---
        audio_state = AudioState()
        audio_manager = AudioManager(audio_state)
        tts = InterviewTTS(audio_manager)
        stt = InterviewSTT(audio_state)

        # --- Interview State ---
        covered_topics: List[str] = []
        last_response = "(The interview has just begun)"
        start_time = asyncio.get_event_loop().time()
        is_first_turn = True
        timeout_reached = False  # Track if interview ended due to timeout
        lies_detected: List[Dict[str, str]] = []  # Track lies and elaborations
        
        logger.info(f"Interview starting. Max duration: {MAX_INTERVIEW_DURATION} seconds")

        # --- Main Loop ---
        try:
            # 1. Greet the candidate
            candidate_name = knowledge_db.get_candidate_name()
            greeting = f"Hello {candidate_name}, thank you for joining me today. Let's start by talking about your experience. Can you tell me about your role at your most recent position?"
            clean_greeting = strip_markdown(greeting)
            await tts.speak(clean_greeting)
            conversation_history.append({"role": "interviewer", "content": clean_greeting})
            await audio_manager.wait_for_playback_to_finish()

            while (asyncio.get_event_loop().time() - start_time) < MAX_INTERVIEW_DURATION:
                current_time = asyncio.get_event_loop().time()
                elapsed_time = current_time - start_time
                remaining_time = MAX_INTERVIEW_DURATION - elapsed_time
                logger.debug(f"Interview loop: elapsed={elapsed_time:.1f}s, remaining={remaining_time:.1f}s")
                # 2. LISTEN: Get candidate's response to the initial or previous question
                transcript = await stt.listen()
                if not transcript:
                    last_response = "(No response was given.)"
                    timeout_message = "Are you still there?"
                    clean_timeout_message = strip_markdown(timeout_message)
                    await tts.speak(clean_timeout_message)
                    await audio_manager.wait_for_playback_to_finish()
                    continue

                conversation_history.append({"role": "candidate", "content": transcript})
                last_response = transcript

                # Play a filler word to hide latency while we think
                await play_random_filler(audio_manager, filler_words_paths)

                # 3. THINK: Start LLM calls in parallel
                action_task = asyncio.create_task(
                    interviewer_agent.generate_action(
                        conversation_history, covered_topics, last_response
                    )
                )
                
                analysis_task = None
                if not is_first_turn:
                    analysis_task = asyncio.create_task(
                        lie_agent.analyze_transcript_batch(last_response)
                    )
                else:
                    is_first_turn = False # No longer the first turn

                # 4. DECIDE: Wait for analyses to complete
                action_response = await action_task
                analysis_result = None
                if analysis_task:
                    analysis_result = await analysis_task
                    logger.info(f"Lie analysis completed: {len(analysis_result.claims_analyzed) if analysis_result else 0} claims analyzed")
                
                logger.info("Interviewer evaluation: %s", action_response.evaluation)
                covered_topics = action_response.updated_covered_topics
                next_action = action_response.next_action
                
                # Check if interviewer detected a lie in their evaluation (fallback for timeout cases)
                evaluation_text = action_response.evaluation.lower()
                if any(word in evaluation_text for word in ["lie", "lies", "lying", "fabricat", "dishonest", "false"]):
                    logger.warning("Interviewer evaluation indicates potential lie detected")
                    # Create a fallback lie entry if we haven't captured it yet
                    fallback_lie_entry = {
                        "lie": last_response,
                        "explanation_given_by_candidate": "(Interview ended before elaboration could be requested)",
                        "confidence": 0.95,  # High confidence since interviewer flagged it
                        "reasoning": f"Interviewer evaluation: {action_response.evaluation[:200]}...",
                        "category": "experience"
                    }
                    # Only add if we haven't already captured this lie
                    if not any(lie["lie"] == last_response for lie in lies_detected):
                        lies_detected.append(fallback_lie_entry)
                        logger.info("Added fallback lie entry based on interviewer evaluation")

                # 5. ACT: Prioritize nudging over asking the next question
                if analysis_result:
                    lies = [
                        c
                        for c in analysis_result.claims_analyzed
                        if c.lie and c.confidence > LIE_CONFIDENCE_THRESHOLD
                    ]
                    logger.info(f"Lies found above threshold ({LIE_CONFIDENCE_THRESHOLD}): {len(lies)}")
                    if lies:
                        # Record the lie and deliver nudge
                        detected_lie = lies[0]
                        logger.warning(f"Lie detected: '{detected_lie.claim}' (confidence: {detected_lie.confidence:.2f})")
                        await interviewer_agent.deliver_nudge(detected_lie, tts)
                        await audio_manager.wait_for_playback_to_finish()
                        
                        # Listen for elaboration/explanation from candidate
                        elaboration_transcript = await stt.listen()
                        if elaboration_transcript:
                            # Store the lie and elaboration with additional context
                            lies_detected.append({
                                "lie": detected_lie.claim,
                                "explanation_given_by_candidate": elaboration_transcript,
                                "confidence": detected_lie.confidence,
                                "reasoning": detected_lie.reasoning,
                                "category": detected_lie.category
                            })
                            conversation_history.append({"role": "candidate", "content": elaboration_transcript})
                            last_response = elaboration_transcript
                            logger.info(f"Candidate provided elaboration for lie: '{elaboration_transcript[:100]}...'")
                        else:
                            # Store lie with no elaboration given but include context
                            lies_detected.append({
                                "lie": detected_lie.claim,
                                "explanation_given_by_candidate": "(No elaboration provided)",
                                "confidence": detected_lie.confidence,
                                "reasoning": detected_lie.reasoning,
                                "category": detected_lie.category
                            })
                            logger.info("Candidate did not provide elaboration for detected lie")
                        continue # Skip to listening again after a nudge

                if next_action.action == "end_interview":
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    logger.info(f"Interview ending early due to agent decision after {elapsed_time:.1f} seconds")
                    clean_text = strip_markdown(next_action.text)
                    conversation_history.append({"role": "interviewer", "content": clean_text})
                    await tts.speak(clean_text)
                    await audio_manager.wait_for_playback_to_finish()
                    break
                else:
                    question = next_action.text
                    clean_question = strip_markdown(question)
                    conversation_history.append({"role": "interviewer", "content": clean_question})
                    await tts.speak(clean_question)
                    await audio_manager.wait_for_playback_to_finish()

            else:
                logger.info("Maximum interview duration reached.")
                timeout_reached = True  # Mark that timeout was reached
                
                # Final check for any unprocessed lies before ending
                if analysis_result:
                    remaining_lies = [
                        c for c in analysis_result.claims_analyzed
                        if c.lie and c.confidence > LIE_CONFIDENCE_THRESHOLD
                    ]
                    if remaining_lies:
                        logger.warning(f"Interview ended with {len(remaining_lies)} unprocessed lies")
                        for lie in remaining_lies:
                            if not any(existing_lie["lie"] == lie.claim for existing_lie in lies_detected):
                                lies_detected.append({
                                    "lie": lie.claim,
                                    "explanation_given_by_candidate": "(Interview ended before elaboration could be requested)",
                                    "confidence": lie.confidence,
                                    "reasoning": lie.reasoning,
                                    "category": lie.category
                                })
                                logger.info(f"Added unprocessed lie to final log: '{lie.claim[:50]}...'")
                
                # Interview will be closed in finally block, then audio will play
        except Exception as e:
            logger.error("An unexpected error occurred in the main loop: %s", e, exc_info=True)

    except KeyboardInterrupt:
        logger.info("System stopped by user.")

    finally:
        logger.info("Cleaning up and shutting down...")

        # 1. Stop STT
        if stt:
            logger.info("Stopping STT...")
            stt.stop()

        # 2. Close audio manager
        if audio_manager:
            logger.info("Closing audio manager...")
            await audio_manager.close()

        # 3. Save interview log
        logger.info("Saving interview log...")
        if conversation_history and knowledge_db and interviewer_agent:
            try:
                # Generate the final summary using an LLM
                final_review = await interviewer_agent.generate_final_review(
                    conversation_history
                )

                # Create the final data structure by dumping existing data
                interview_dump = {
                    "summary": final_review.model_dump(),
                    "conversation_history": conversation_history,
                    "knowledge_base": knowledge_db.to_dict(),
                    "lies": lies_detected,
                }

                # Generate filename and save
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                log_dir = os.path.join(find_project_root(), "logs")
                os.makedirs(log_dir, exist_ok=True)
                filename = os.path.join(log_dir, f"interview_summary_{timestamp}.json")

                with open(filename, "w") as f:
                    json.dump(interview_dump, f, indent=4)
                logger.info("Interview log saved to %s", filename)
                logger.info(f"Interview summary includes {len(lies_detected)} detected lies")

            except Exception as e:
                logger.error("Failed to save interview log: %s", e, exc_info=True)

        # 4. Cancel all asyncio tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if tasks:
            logger.info("Cancelling %d background tasks...", len(tasks))
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        # 5. Play Deepgram audio after all processes are stopped/closed
        logger.info("Playing Deepgram audio after all processes are stopped...")
        deepgram_audio_path = os.path.join(os.path.dirname(__file__), "deepgram-aura-2-thalia-en.wav")
        logger.info(f"Looking for deepgram audio file at: {deepgram_audio_path}")
        if os.path.exists(deepgram_audio_path):
            try:
                logger.info("Deepgram audio file found, playing with system audio...")
                # Use system-based audio playback since AudioManager is already closed
                await _play_system_audio(deepgram_audio_path)
                logger.info("Deepgram audio playback completed.")
            except Exception as e:
                logger.error(f"Error playing Deepgram audio: {e}", exc_info=True)
        else:
            logger.warning("Deepgram audio file not found")


if __name__ == "__main__":
    from audio import ProvenDeepgramTTS, RealTimeSTT

    if not all([RealTimeSTT, ProvenDeepgramTTS]):
        logger.critical("STT or TTS modules failed to import. Cannot run.")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass
