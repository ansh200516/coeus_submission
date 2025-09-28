import asyncio
import logging
import os
import sys
import importlib.util
from typing import Any, AsyncGenerator, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# --- Environment and Path Setup ---
project_root = os.path.dirname(os.path.abspath(__file__))
# We still add the project root to the path, as it can help with nested imports
# within the dynamically loaded modules.
sys.path.insert(0, project_root)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_module_from_path(module_name: str, file_path: str) -> Any:
    """Dynamically load a module from a specific file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load spec for module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # Add to sys.modules to handle relative imports
    spec.loader.exec_module(module)
    return module

# --- WebSocket Audio Bridge (code is unchanged) ---
class WebSocketAudioBridge:
    """A bridge to handle audio streams between a WebSocket and an agent."""
    def __init__(self) -> None:
        self.incoming_audio: asyncio.Queue[bytes] = asyncio.Queue()
        self.outgoing_audio: asyncio.Queue[bytes] = asyncio.Queue()
        self.stop_event = asyncio.Event()

    async def receive_from_websocket(self, websocket: WebSocket) -> None:
        try:
            while not self.stop_event.is_set():
                data = await websocket.receive_bytes()
                await self.incoming_audio.put(data)
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected.")
            self.stop_event.set()

    async def send_to_websocket(self, websocket: WebSocket) -> None:
        try:
            while not self.stop_event.is_set():
                data = await self.outgoing_audio.get()
                await websocket.send_bytes(data)
                self.outgoing_audio.task_done()
        except asyncio.CancelledError:
            logger.info("Send-to-websocket task cancelled.")

# --- Agent Adapters ---

# --- LDA Agent Adapter ---
async def run_lda_agent(bridge: WebSocketAudioBridge, interview_type: str, candidate_name: str) -> None:
    """Run the LDA agent logic using dynamic loading and the WebSocket bridge."""
    logger.info(f"Starting LDA agent for interview type: {interview_type}")
    try:
        # Dynamically load LDA modules by path
        lda_path = os.path.join(project_root, "Brain", "lda")
        main_mod = load_module_from_path("lda_main", os.path.join(lda_path, "main.py"))
        agents_mod = load_module_from_path("lda_agents", os.path.join(lda_path, "agents.py"))
        db_mod = load_module_from_path("lda_db", os.path.join(lda_path, "knowledge_db.py"))
        state_mod = load_module_from_path("lda_state", os.path.join(lda_path, "shared_state.py"))
        config_mod = load_module_from_path("lda_config", os.path.join(lda_path, "config.py"))
        utils_mod = load_module_from_path("lda_utils", os.path.join(lda_path, "utils.py"))

        # Re-define the TTS wrapper inside the function to use the loaded module
        class LdaWebSocketTTS(utils_mod.ElevenLabsTTS):
            def __init__(self, bridge: WebSocketAudioBridge, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.bridge = bridge
            def speak(self, text: str) -> None:
                try:
                    audio_generator = self.client.generate(text=text, voice=self.voice, model=self.model, stream=True)
                    for chunk in audio_generator:
                        asyncio.run(self.bridge.outgoing_audio.put(chunk))
                except Exception as e:
                    logger.error(f"Error in LdaWebSocketTTS: {e}")

        shared_state = state_mod.SharedState(candidate_name=candidate_name)
        knowledge_db = db_mod.KnowledgeDatabase()
        from langchain_cerebras import ChatCerebras
        llm_client = ChatCerebras(api_key=os.getenv("CEREBRAS_API_KEY"), model_name="llama-4-maverick-17b-128e-instruct")
        agent = agents_mod.LdaAgent(knowledge_db=knowledge_db, llm_client=llm_client, mode=interview_type)
        tts_adapter = LdaWebSocketTTS(bridge, voice_id=config_mod.ELEVEN_LABS_VOICE_ID, model=config_mod.ELEVEN_LABS_MODEL)

        async def get_audio_input_stream() -> AsyncGenerator[bytes, None]:
            while not bridge.stop_event.is_set():
                yield await bridge.incoming_audio.get()

        await main_mod.main_loop(
            interview_type=interview_type,
            candidate_name=candidate_name,
            shared_state=shared_state,
            knowledge_db=knowledge_db,
            agent=agent,
            tts=tts_adapter,
            audio_input_stream_getter=get_audio_input_stream,
        )
    except Exception as e:
        logger.error(f"Error running LDA agent: {e}", exc_info=True)
    finally:
        bridge.stop_event.set()

# --- Code Interview Agent Adapter ---
async def run_code_interview_agent(bridge: WebSocketAudioBridge, interview_mode: str, candidate_name: str) -> None:
    """Run the Code Interview agent logic using dynamic loading and the WebSocket bridge."""
    logger.info(f"Starting Code Interview agent in mode: {interview_mode}")
    try:
        # Dynamically load Code Interview modules by path
        # Note the directory name with spaces
        cia_path = os.path.join(project_root, "Brain", "code interview agent")
        main_mod = load_module_from_path("cia_main", os.path.join(cia_path, "main.py"))
        audio_mod = load_module_from_path("cia_audio", os.path.join(cia_path, "audio.py"))

        # Re-define wrappers inside the function to use loaded modules
        class CodeInterviewWebSocketTTS(audio_mod.InterviewTTS):
            def __init__(self, bridge: WebSocketAudioBridge, audio_manager: Any) -> None:
                super().__init__(audio_manager)
                self.bridge = bridge
            async def speak(self, text: str, add_filler: bool = True) -> None:
                async for chunk in self._generate_audio(text, add_filler):
                    await self.bridge.outgoing_audio.put(chunk)

        class CodeInterviewWebSocketSTT(audio_mod.InterviewSTT):
            def __init__(self, bridge: WebSocketAudioBridge, audio_state: Any) -> None:
                super().__init__(audio_state)
                self.bridge = bridge
            async def listen(self, timeout: float = 5.0) -> str:
                try:
                    await asyncio.wait_for(self.bridge.incoming_audio.get(), timeout=timeout)
                    logger.warning("CodeInterviewWebSocketSTT.listen is a placeholder!")
                    return "placeholder transcribed text"
                except asyncio.TimeoutError:
                    return ""

        system = main_mod.CodeInterviewSystem(candidate_name=candidate_name, interview_mode=interview_mode)
        await system.initialize()

        system.tts = CodeInterviewWebSocketTTS(bridge, system.audio_manager)
        system.stt = CodeInterviewWebSocketSTT(bridge, system.audio_state)
        logger.info("CodeInterviewSystem audio components overridden for WebSocket.")

        await system.conduct_interview()
    except Exception as e:
        logger.error(f"Error running Code Interview agent: {e}", exc_info=True)
    finally:
        bridge.stop_event.set()

# --- FastAPI Server ---
app = FastAPI()

@app.websocket("/ws/{agent_type}/{interview_mode}")
async def agent_websocket(websocket: WebSocket, agent_type: str, interview_mode: str) -> None:
    """Handle WebSocket connections for different agent types."""
    await websocket.accept()
    candidate_name = websocket.query_params.get("candidate", "Unknown Candidate")
    bridge = WebSocketAudioBridge()

    receive_task = asyncio.create_task(bridge.receive_from_websocket(websocket))
    send_task = asyncio.create_task(bridge.send_to_websocket(websocket))

    agent_task = None
    if agent_type == "lda":
        agent_task = asyncio.create_task(run_lda_agent(bridge, interview_mode, candidate_name))
    elif agent_type == "code_interview":
        agent_task = asyncio.create_task(run_code_interview_agent(bridge, interview_mode, candidate_name))
    else:
        logger.error(f"Unknown agent type: {agent_type}")
        await websocket.close(code=1008, reason="Unknown agent type")
        return

    try:
        await asyncio.gather(receive_task, send_task, agent_task)
    except Exception as e:
        logger.error(f"An error occurred in the main WebSocket handler: {e}")
    finally:
        logger.info("Closing WebSocket connection and cleaning up tasks.")
        for task in [receive_task, send_task, agent_task]:
            if task and not task.done():
                task.cancel()
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close()

@app.get("/")
def read_root() -> Dict[str, str]:
    """Provide a simple health check endpoint."""
    return {"message": "Agent Runner WebSocket server is running."}
