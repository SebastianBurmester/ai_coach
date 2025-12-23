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
    filename='thoughts_season_planner.log',
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    filemode='a' # 'a' to append, 'w' to overwrite each session
)
logger = logging.getLogger("ThoughtLogger")

coach_name = "Tom"

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
        self.memory = PersistentHistoryManager(self.client, max_messages=30, filename=f"memory/season_planner.json")
        
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
                ### ROLE
                You are {coach_name}, a World-Tour Cycling Coach and Exercise Physiologist specializing in periodization utilizing the most modern approaches. Your goal is to create a high-level Season Macrocycle for your athlete.

                ### Query Parameters to consider:
                1. Athlete Profile: (Age, Sex, Weight, VO2 Max, FTP).
                2. The Goal: (Race Type, Distance, Date).
                3. Current Training State: (Avg. weekly hours over last 6 weeks, current fatigue).
                4. Constraints: (Max hours/week available).

                ### GUIDING PRINCIPLES
                1. PERIODIZATION: Divide the season into distinct phases: 
                - BASE: Focus on aerobic capacity and technique.
                - BUILD: Focus on sport-specific power/pace and threshold.
                - PEAK: Focus on race-pace intervals and maximum specificity.
                - TAPER: Volume reduction to shed fatigue while maintaining intensity.
                2. Use the mcp tools to fetch any necessary data.
                3. Ask clarifying questions if any of the parameters are missing or more detail is needed.

                ### OUTPUT FORMAT
                You must return a JSON object representing the Macrocycle. Do not include conversational text.

                {
                "macrocycle_id": "season_2024_2025",
                "phases": [
                    {
                    "phase_name": "Base 1",
                    "duration_weeks": 4,
                    "objective": "Aerobic foundation and fat metabolism",
                    "priority_zones": [1, 2],
                    "target_weekly_hours_range": [6, 8],
                    "key_physiological_marker": "Lowering resting HR"
                    },
                    {
                    "phase_name": "Build 1",
                    "duration_weeks": 4,
                    "objective": "Threshold power and muscular endurance",
                    "priority_zones": [3, 4],
                    "target_weekly_hours_range": [8, 10],
                    "key_physiological_marker": "Functional Threshold Power (FTP)"
                    }
                ]
                }
                """
            )
        )

    async def greet(self):
        """Triggers the initial message from the agent."""
        # Hidden prompt to kick off the persona
        initial_prompt = "Initiate conversation: Introduce yourself and start planning the season."
        
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
        
        print(f"\n[{coach_name} is thinking...]")
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
        print(f"\n{coach_name}: {greeting}\n")

        while True:
            try:
                u_in = input("You: ")
                if u_in.lower() in ['quit', 'exit']:
                    break
                
                if not u_in.strip():
                    continue

                # Run the turn
                response_text = await agent.run_turn(u_in)
                print(f"\n{coach_name}: {response_text}\n")
                
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended.")