import asyncio
import os
import sys
from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from google.genai import types
from ..history_manager import PersistentHistoryManager

import datetime

import logging

# Configure logging to save thoughts to a file
logging.basicConfig(
    filename='thoughts_health.log',
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    filemode='a' # 'a' to append, 'w' to overwrite each session
)
logger = logging.getLogger("ThoughtLogger")

# --- 1. Load Configuration ---
load_dotenv()
SERVER_FILE = r"C:\Users\sburm\ai_coach\src\mcp_server.py"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

today = datetime.date.today().strftime("%Y-%m-%d")

class Agent:
    def __init__(self, mcp_session):
        if not GEMINI_API_KEY:
            sys.exit("Error: GEMINI_API_KEY missing.")
        
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.mcp_session = mcp_session
        self.memory = PersistentHistoryManager(self.client, max_messages=30, filename=f"memory/health_memory.json")
        
        # 1. Enable Thinking in the Config
        # include_thoughts=True allows us to see the reasoning parts.
        self.chat = self.client.aio.chats.create(
            model="gemini-2.5-flash",
            history=self.memory.get_loadable_history(),
            config=types.GenerateContentConfig(
                tools=[self.mcp_session],
                temperature=1.0, 
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    # Optional: budget_tokens=1024 # How much it's allowed to "think"
                ),
                system_instruction="""
                Role: World Tour Cycling Team Physician
                Tone: Professional, analytical, decisive, and encouraging but firm.

                Core Identity:
                You are the Chief Medical Officer for a premier UCI World Tour cycling team. You specialize in sports medicine, exercise physiology, and clinical nutrition. Your goal is to monitor rider health stats and manage recovery.
                
                Data Analysis Parameters:
                When reviewing health stats, you must prioritize the following metrics:

                HRV (Heart Rate Variability): To assess autonomic nervous system recovery.

                Resting Heart Rate (RHR): Monitoring for spikes that indicate overtraining or oncoming illness.

                Sleep Quality/Duration: Assessing restorative phases (REM and Deep Sleep).

                Training Load: Comparing physical load to the rider's current recovery capacity.

                Thought Process:
                You are encouraged to ask clarifying questions if data shows unexpected trends.

                Response Structure
                Status Assessment: A brief summary of the rider's current physiological state and a health readiness score from 0 to 100.
                """
            )
        )

    async def greet(self):
        """Triggers the initial message from the agent."""
        # Hidden prompt to kick off the persona
        initial_prompt = "Initiate conversation: Introduce yourself and get into the analytic mindset."
        
        # We don't necessarily want to save the 'initial_prompt' to history, 
        # but we definitely want to save Coach's response.
        stream = await self.chat.send_message_stream(initial_prompt)
        
        full_response_text = ""
        async for chunk in stream:
            for part in chunk.candidates[0].content.parts:
                if part.thought:
                    logger.debug(f"THOUGHT: {part.text.strip()}")
                if part.text and not part.thought:
                    full_response_text += part.text

        # Save the greeting to memory so the AI remembers what it said
        self.memory.add_message("model", full_response_text)
        return full_response_text



    async def run_turn(self, user_input):
        self.memory.add_message("user", user_input)
        
        full_response_text = ""
        
        # 2. Use Streaming to catch thoughts
        # We use await for the stream object, then 'async for' through it.
        stream = await self.chat.send_message_stream(user_input)
        
        print("\n[Coach Thinking...]")
        async for chunk in stream:
            # Check for thought parts (Reasoning)
            for part in chunk.candidates[0].content.parts:
                if part.thought:
                    logger.debug(f"THOUGHT: {part.text.strip()}")
                
                if part.text and not part.thought:
                    # Collect and print the actual response
                    full_response_text += part.text

        self.memory.add_message("model", full_response_text)
        return full_response_text
    


# --- 2. Main Execution Loop ---
async def main():
    print("--- Connecting to Fitness MCP Server ---")
    
    async with Client(SERVER_FILE) as mcp_client:
        agent = Agent(mcp_client.session)
        
        print("--- Fitness Coach (Flash 2.5 + MCP + History) ---")

        greeting = await agent.greet()
        print(f"\nCoach: {greeting}\n")

        while True:
            try:
                u_in = input("You: ")
                if u_in.lower() in ['quit', 'exit']:
                    break
                
                if not u_in.strip():
                    continue

                # Run the turn
                response_text = await agent.run_turn(u_in)
                print(f"\nCoach: {response_text}\n")
                
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended.")