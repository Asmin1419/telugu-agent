import os
import logging
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import sarvam
from flask import Flask
from flask_cors import CORS  # This is for CORS support in Flask

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-agent")

# Flask App Setup with CORS
app = Flask(__name__)

# Allow only requests from your frontend (Vercel URL)
CORS(app, resources={r"/*": {"origins": "https://your-frontend.vercel.app"}})

class TeluguVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are Bhavik, a Telugu voice assistant. Always respond in Telugu in a friendly way."
        )

        # Sarvam STT
        self.stt = sarvam.STT(
            api_key=os.getenv("SARVAM_API_KEY"),
            language="te-IN",
        )

        # Sarvam TTS
        self.tts = sarvam.TTS(
            api_key=os.getenv("SARVAM_API_KEY"),
            voice="telugu_female",
        )


async def entrypoint(ctx: JobContext):
    logger.info(f"🔥 Job started for room: {ctx.room.name}")

    agent = TeluguVoiceAgent()

    session = AgentSession(
        room=ctx.room,
        stt=agent.stt,
        tts=agent.tts,
        turn_detection="stt",
        min_endpointing_delay=0.2,
    )

    await session.start()

    # Force first speech
    await session.generate_reply(
        instructions="వినిపిస్తుందా? నేను తెలుగు భావిక్. మాట్లాడండి."
    )


if __name__ == "__main__":
    # Run the agent
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

    # For Flask server (if you use it, e.g., to serve API or for testing)
    app.run(debug=True, host="0.0.0.0", port=5000)  # Adjust as needed