# Fully Local AI Voice Assistant (Apple Silicon Optimized)



This repository contains a fully private, real-time voice and text AI assistant optimized for macOS and Apple Silicon (M1/M2/M3/M4). It uses **LiveKit** to handle WebRTC audio streaming, **MLX-Whisper** for hardware-accelerated transcription, **Ollama** for the local LLM brain, and **Piper** for offline Text-to-Speech.

## Features
* **100% Offline & Private:** No API keys, no cloud processing.
* **Hardware Accelerated STT:** Uses Apple's `mlx-whisper` for near-instant transcription on M-Series chips.
* **Low Latency VAD:** Uses `silero` to detect when you start and stop speaking.


## Prerequisites
* **macOS** with an Apple Silicon chip (M1 - M4)
* **Python 3.9+**
* **Node.js** (for the frontend playground)
* **Ollama** ([Download here](https://ollama.com/))
* **LiveKit CLI & Server** (`brew install livekit`)

---

## Step 1: Start the Background Servers
Open two separate terminal windows and run these commands to start the WebRTC and LLM servers. Leave both running in the background.

**Terminal 1 (LiveKit):**
```bash
livekit-server-dev

```

**Terminal 2 (Ollama):**

```bash
ollama serve

```

**Terminal 3 (Pull the LLM):**
*(You only need to run this once to download the model)*

```bash
ollama run llama3.1

```

---

## Step 2: Set Up the Python Agent (Backend)

1. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate

```


2. Install the required dependencies:
```bash
pip install "livekit-agents[openai]~=1.0" python-dotenv livekit-plugins-silero piper-tts mlx-whisper librosa numpy

```


3. Download the Piper TTS voice model to your project folder:
```bash
mkdir -p models
python -m piper.download_voices en_GB-alan-medium --data-dir models
```


1. Run your agent:
```bash
python livekit_agent.py dev

```



---

## Step 3: Set Up the Next.js Frontend (Agents Playground)

To avoid browser security blocks (Mixed Content errors) when testing WebRTC locally, we run the official LiveKit Agents Playground.

1. Clone the playground repository into a new folder:
```bash
git clone https://github.com/livekit/agents-playground.git
cd agents-playground
npm install

```


2. Create a `.env.local` file inside the `agents-playground` folder:
```text
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

```


3. Start the frontend development server:
```bash
npm run dev

```



---

## Step 4: Connect and Chat!

1. Open your web browser and go to **`http://localhost:3000`**.
2. Click the blue **Connect** button.
3. Speak into your microphone! The system will process your voice entirely on your MacBook and reply out loud.

---

## Troubleshooting & LiveKit 1.0 Patches


### 1. Ollama "Model Not Found"

If the script crashes saying it can't find `llama3.1`, or another model of your choice, ensure the model name in your `livekit_agent.py` exactly matches the output of `ollama list` and that the model has already been downloaded using `ollama pull MODEL_NAME`.

