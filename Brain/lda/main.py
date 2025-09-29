import asyncio
import datetime
import json
import logging
import os
import random
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
from utils import find_project_root, strip_markdown

load_dotenv()

# ========== LOGGING SETUP ==========
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


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
async def main():
    """Main entry point for the interactive interviewer agent."""
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
        linkedin_file = os.path.join(
            project_root, "logs", "person_Vatsal_Jain_20250923_070456.json"
        )
        resume_file = os.path.join(
            project_root, "logs", "resume_1757659381503_20250923T013457.json"
        )
        knowledge_db.load_from_files(linkedin_file, resume_file)

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
        
        logger.info(f"Interview starting. Max duration: {MAX_INTERVIEW_DURATION} seconds")

        # --- Main Loop ---
        try:
            # 1. Greet the candidate
            candidate_name = knowledge_db.get_candidate_name()
            greeting = f"Hello {candidate_name}, thank you for joining me today. Let's start by talking about your experience. Can you tell me about your role at your most recent position?"
            clean_greeting = strip_markdown(greeting)
            await tts.speak(clean_greeting)
            conversation_history.append({"role": "interviewer", "content": greeting})
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
                    await tts.speak("Are you still there?")
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
                
                logger.info("Interviewer evaluation: %s", action_response.evaluation)
                covered_topics = action_response.updated_covered_topics
                next_action = action_response.next_action

                # 5. ACT: Prioritize nudging over asking the next question
                if analysis_result:
                    lies = [
                        c
                        for c in analysis_result.claims_analyzed
                        if c.lie and c.confidence > LIE_CONFIDENCE_THRESHOLD
                    ]
                    if lies:
                        await interviewer_agent.deliver_nudge(lies[0], tts)
                        await audio_manager.wait_for_playback_to_finish()
                        continue # Skip to listening again after a nudge

                if next_action.action == "end_interview":
                    elapsed_time = asyncio.get_event_loop().time() - start_time
                    logger.info(f"Interview ending early due to agent decision after {elapsed_time:.1f} seconds")
                    clean_text = strip_markdown(next_action.text)
                    await tts.speak(clean_text)
                    await audio_manager.wait_for_playback_to_finish()
                    break
                else:
                    question = next_action.text
                    conversation_history.append({"role": "interviewer", "content": question})
                    clean_question = strip_markdown(question)
                    await tts.speak(clean_question)
                    await audio_manager.wait_for_playback_to_finish()

            else:
                logger.info("Maximum interview duration reached.")
                timeout_reached = True  # Mark that timeout was reached
                # Interview will be closed in finally block, then audio will play
        except Exception as e:
            logger.error("An unexpected error occurred in the main loop: %s", e, exc_info=True)

    except KeyboardInterrupt:
        logger.info("System stopped by user.")

    finally:
        logger.info("Cleaning up and shutting down...")

        # 1. Play timeout audio if needed (before stopping STT and closing audio)
        if timeout_reached and audio_manager:
            logger.info("Playing timeout audio before closing interview...")
            deepgram_audio_path = os.path.join(os.path.dirname(__file__), "deepgram-aura-2-thalia-en.wav")
            logger.info(f"Looking for deepgram audio file at: {deepgram_audio_path}")
            if os.path.exists(deepgram_audio_path):
                try:
                    logger.info("Deepgram audio file found, scheduling playback...")
                    await audio_manager.schedule_playback(deepgram_audio_path)
                    logger.info("Audio scheduled, waiting for playback to finish...")
                    await audio_manager.wait_for_playback_to_finish()
                    logger.info("Deepgram audio playback completed.")
                except Exception as e:
                    logger.error(f"Error playing timeout audio: {e}", exc_info=True)
            else:
                logger.warning("Deepgram audio file not found")

        # 2. Stop STT
        if stt:
            logger.info("Stopping STT...")
            stt.stop()

        # 3. Close audio manager
        if audio_manager:
            logger.info("Closing audio manager...")
            await audio_manager.close()

        # 4. Save interview log
        logger.info("Saving interview log...")
        if conversation_history and knowledge_db and interviewer_agent:
            try:
                # Generate the final summary using an LLM
                final_review = await interviewer_agent.generate_final_review(
                    conversation_history
                )

                # Create the final data structure by dumping existing data
                interview_dump = {
                    "summary": final_review.dict(),
                    "conversation_history": conversation_history,
                    "knowledge_base": knowledge_db.to_dict(),
                }

                # Generate filename and save
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                log_dir = os.path.join(find_project_root(), "logs")
                os.makedirs(log_dir, exist_ok=True)
                filename = os.path.join(log_dir, f"interview_summary_{timestamp}.json")

                with open(filename, "w") as f:
                    json.dump(interview_dump, f, indent=4)
                logger.info("Interview log saved to %s", filename)

            except Exception as e:
                logger.error("Failed to save interview log: %s", e, exc_info=True)

        # 5. Cancel all asyncio tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if tasks:
            logger.info("Cancelling %d background tasks...", len(tasks))
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    from audio import ProvenDeepgramTTS, RealTimeSTT

    if not all([RealTimeSTT, ProvenDeepgramTTS]):
        logger.critical("STT or TTS modules failed to import. Cannot run.")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass
