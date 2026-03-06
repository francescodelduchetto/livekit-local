
import logging
import asyncio
import numpy as np
import librosa
import mlx_whisper
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, stt
from livekit.plugins import openai, silero
from PiperTTSPlugin import PiperTTSPlugin 

load_dotenv()
logger = logging.getLogger("voice-agent")



# ==========================================
# CUSTOM MLX-WHISPER STT PLUGIN
# ==========================================
class MLXWhisperSTT(stt.STT):
    def __init__(self, model: str = "mlx-community/whisper-base-mlx"):
        # Tell LiveKit we process chunks (which tells it to use _recognize_impl)
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )
        self._model = model

    async def _recognize_impl(
        self, 
        buffer: rtc.AudioBuffer, 
        *, 
        language: str | None = None, 
        **kwargs
    ) -> stt.SpeechEvent:
        
        # 1. Get raw PCM16 audio bytes from LiveKit's VAD chunk
        raw_data = buffer.data.tobytes() if hasattr(buffer.data, "tobytes") else bytes(buffer.data)
        
        # 2. Convert to float32 (required by Whisper)
        audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # 3. Resample to 16kHz if necessary
        orig_sr = buffer.sample_rate
        if orig_sr != 16000:
            audio_np = librosa.resample(y=audio_np, orig_sr=orig_sr, target_sr=16000)

        # 4. Run MLX Whisper on your M4 Pro GPU in a background thread
        def run_mlx():
            return mlx_whisper.transcribe(audio_np, path_or_hf_repo=self._model)
        
        result = await asyncio.to_thread(run_mlx)
        text = result.get("text", "").strip()
        
        if text:
            logger.info(f"🎤 You said: {text}")

        # 5. Return the transcript back to the AgentSession
        return stt.SpeechEvent(
            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
            alternatives=[stt.SpeechData(text=text, language="en")]
        )
# ==========================================


class LocalAssistant(Agent):
    def __init__(self):
        super().__init__(instructions=(
                "You are a highly intelligent, helpful AI voice assistant running privately on the user's MacBook. "
                "Respond to the user's spoken questions concisely and directly. "
                "Do NOT act like a local tour guide, and do NOT recommend restaurants, food, or places to visit unless the user explicitly asks for them. "
                "If the user says nothing or the transcription is empty, just say 'I am listening'."
            )
        )

async def entrypoint(ctx: agents.JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect()

    session = AgentSession(
        # VAD tells MLX when to start and stop listening
        vad=silero.VAD.load(),
        
        # Our custom Apple Silicon STT!
        stt=MLXWhisperSTT(model="mlx-community/whisper-base-mlx"), 
        
        llm=openai.LLM.with_ollama(
            model="llama3.1", 
            base_url="http://127.0.0.1:11434/v1"
        ),
        tts=PiperTTSPlugin(model="models/en_GB-alan-medium.onnx"), 
    )
    
    await session.start(room=ctx.room, agent=LocalAssistant())
    
    # Greet the user
    await session.generate_reply(
        instructions="Greet the user warmly."
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint)) 