# Local Voice + Text Virtual Assistant (LiveKit, Python & Ollama)

This repository contains a fully local, real-time voice and text AI assistant. It uses **LiveKit** to handle the WebRTC audio streaming, **Python** as the agent backend, and **Ollama** to run the Large Language Model (LLM) entirely on your local machine.

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
* **Python 3.9+**
* **Node.js** (for running the frontend playground)
* **Ollama** ([Download here](https://ollama.com/))
* **LiveKit CLI & Server** (macOS/Linux: `brew install livekit`)

---

## Step 1: Start the LiveKit Server
We use LiveKit's development server to handle real-time audio and text sockets locally.

1. Open a new terminal and run:
   ```bash
   livekit-server-dev

   ```

2. Leave this terminal running in the background.

> **Tip:** If you get an "address already in use" error, a previous instance is stuck in the background. Run `killall livekit-server` to clear it and try again.

---

## Step 2: Start the Local LLM (Ollama)

The assistant relies on Ollama to generate intelligent responses locally without needing internet access or API keys.

1. Open a second terminal and start the Ollama background service:
```bash
ollama serve

```


2. Open a third terminal and download/run your preferred model (we use `llama3:13b` as the default):
```bash
ollama run llama3:13b

```


3. Leave the `ollama serve` terminal running in the background.

---

## Step 3: Set Up the Python Agent (Backend)

This Python script connects to the LiveKit room, listens for users, and bridges the audio/text to Ollama.

1. Navigate to your python agent directory and create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


2. Install the required dependencies:
```bash
pip install "livekit-agents[openai]~=1.0" python-dotenv

```


3. Create a `.env` file in the same folder as your Python script with the following exact values:
```text
LIVEKIT_URL=[http://127.0.0.1:7880](http://127.0.0.1:7880)
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

```


*(Note: We use `http://127.0.0.1` instead of `localhost` or `ws://` to prevent IPv6 resolution bugs and local SSL errors).*
4. Start the Python worker:
```bash
python agent.py dev

```



---

## Step 4: Set Up the Next.js Frontend (Agents Playground)

To avoid browser security blocks (Mixed Content errors) when testing WebRTC locally, we run the official LiveKit Agents Playground locally.

1. Clone the playground repository into a new folder:
```bash
git clone https://github.com/livekit/agents-playground.git
cd agents-playground
npm install

```


2. Create a `.env.local` file inside the `agents-playground` folder. **Crucially, Next.js requires the `NEXT_PUBLIC_` prefix for the URL:**
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

## Step 5: Connect and Chat!

1. Open your web browser and navigate to **`http://localhost:3000`**.
2. Look at the right-hand sidebar under **AGENT**. Make sure the **Agent name** field is **completely blank**.
3. Click the blue **Connect** button in the top right corner of the screen.
4. Your Python terminal should instantly light up saying "Participant connected", and you can now chat with your local AI!

---

## Troubleshooting Common Errors

* **"Could not establish signal connection: Load failed" on the frontend** Double-check that your `.env.local` uses `NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880` and that you restarted the Next.js server (`npm run dev`) after creating/saving the `.env.local` file.
* **`Errno 61` or `Connection Refused` in Python** Ensure your `livekit-server-dev` terminal is actually running and hasn't crashed. If you are on a Mac/Linux machine, ensure your Python `.env` uses `127.0.0.1` instead of `localhost` to avoid IPv6 resolution bugs.
* **`SSL: RECORD_LAYER_FAILURE` in Python** Your Python SDK is trying to force an encrypted connection to a local dev server. Ensure your Python `.env` URL is set to `http://127.0.0.1:7880`. The SDK will gracefully upgrade it to WebSockets automatically without triggering SSL errors.

