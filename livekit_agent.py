import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai, silero

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
        vad=silero.VAD.load(),
        # LLM via Ollama API
        llm=openai.LLM.with_ollama(
            model="llama3:13b", # Match the model from your Ollama run
            base_url="http://localhost:11434/v1"
        ),
        # NOTE: To make this a true "Voice" assistant, you need to add STT and TTS plugins here.
        # The tutorial skipped them in the LiveKit snippet because fully local STT/TTS 
        # requires extra setup in LiveKit (e.g., local Whisper server).
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
