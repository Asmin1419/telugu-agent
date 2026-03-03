import logging
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, sarvam

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

class VoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Telugu Bhavik, a warm and helpful Telugu voice assistant.
                            Be friendly, concise, and conversational.
                            Speak naturally as if having a real conversation.
                            You can speak in both Telugu and English (Tenglish) as needed.""",

            # Saaras v3 STT - Speech to text
            stt=sarvam.STT(
                language="en-IN",
                model="saaras:v3",
                mode="transcribe"
            ),

            # OpenAI LLM
            llm=openai.LLM(model="gpt-4o"),

            # Bulbul v3 TTS - Text to speech
            tts=sarvam.TTS(
                target_language_code="en-IN",
                model="bulbul:v3",
                speaker="shubh"
            ),
        )
        logger.info("VoiceAgent initialized with STT + LLM + TTS")

    async def on_enter(self):
        """Called when user joins - agent greets the user"""
        logger.info("User joined — generating greeting")
        await self.session.generate_reply(
            instructions="Greet the user warmly and let them know you're ready to help."
        )


async def entrypoint(ctx: JobContext):
    """Main entry point - LiveKit calls this when a user connects"""
    logger.info(f"User connected to room: {ctx.room.name}")

    # Connect the agent to the room first, then wait for a participant
    await ctx.connect()
    await ctx.wait_for_participant()
    logger.info("Participant joined, starting agent session...")

    # Create and start the agent session
    # AgentSession handles routing audio in/out of the LiveKit room automatically
    session = AgentSession()

    await session.start(
        agent=VoiceAgent(),
        room=ctx.room,
    )

    logger.info("AgentSession started — agent is live")


if __name__ == "__main__":
    print("Starting Telugu Bhavik agent...")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))