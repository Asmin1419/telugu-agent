import logging
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, sarvam

load_dotenv()
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

class VoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
                You are a helpful Telugu voice assistant named Aditya.
                When someone greets you, respond warmly in Telugu.
                Always be friendly and helpful.
            """,
            
            stt=sarvam.STT(
                language="te-IN",
                model="saaras:v3",
                mode="transcribe",
                flush_signal=True
            ),
            
            llm=openai.LLM(model="gpt-4o"),
            
            tts=sarvam.TTS(
                target_language_code="te-IN",
                model="bulbul:v3",
                speaker="aditya"
            ),
        )
    
    async def on_user_speech_committed(self, message):
        logger.info(f"🎤 User said: {message.content}")
        
    async def on_agent_speech_committed(self, message):
        logger.info(f"🔊 Agent responding: {message.content}")
    
    async def on_enter(self):
        """Called when user joins"""
        logger.info("Agent entered, generating greeting")
        # Fix: Use generate_reply() without arguments
        await self.session.generate_reply()
        
        # OR use say() for a specific message:
        # await self.session.say("నమస్కారం! నేను ఆదిత్య, మీ వాయిస్ అసిస్టెంట్. ఈరోజు మీకు ఎలా సహాయం చేయగలను?")

async def entrypoint(ctx: JobContext):
    logger.info(f"User connected to room: {ctx.room.name}")
    
    session = AgentSession(
        turn_detection="stt",
        min_endpointing_delay=0.07
    )
    
    await session.start(
        agent=VoiceAgent(),
        room=ctx.room
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
