import logging
from dotenv import load_dotenv

from PiperTTSPlugin import PiperTTSPlugin

from livekit import agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai, silero
# from livekit.plugins.silero import STT as SileroSTT

from whisperlivekit import STT as WhisperLiveSTT

# Load the LiveKit credentials from your .env file
load_dotenv()
logger = logging.getLogger("voice-agent")

class LocalAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful local assistant. Keep your answers brief."
        )

async def entrypoint(ctx: agents.JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect()

    # Initialize the AgentSession using our local tools
    session = AgentSession(
        vad=silero.VAD.load(),# Connect to your local WLK server running on port 8000
        stt=WhisperLiveSTT(url="ws://127.0.0.1:8000/asr"),
        # LLM via Ollama API
        llm=openai.LLM.with_ollama(
            model="llama3.1", # Match the model from your Ollama run
            base_url="http://127.0.0.1:11434/v1"
        ),
        # Point it to the local model files you downloaded
        tts=PiperTTSPlugin(model="models/en_GB-alan-medium.onnx"), 
    )
    
    # Start the session and greet the user
    await session.start(
        room=ctx.room,
        agent=LocalAssistant()
    )
    await session.generate_reply(
        instructions="Say hello to the user and ask what's on their mind."
    )

if __name__ == "__main__":
    # Run the script as a LiveKit worker app
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
