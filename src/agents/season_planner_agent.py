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

# --- 1. Load Configuration ---
load_dotenv()
SERVER_FILE = r"C:\Users\sburm\ai_coach\src\mcp_server.py"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

today = datetime.date.today().strftime("%Y-%m-%d")

class Agent:
    def __init__(self, mcp_session, coach_name="Season Coach"):
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
                    include_thoughts=False,
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
                5. History: (Previous months training data).

                ### GUIDING PRINCIPLES
                1. PERIODIZATION: Divide the season into distinct phases: 
                - BASE: Focus on aerobic capacity and technique.
                - BUILD: Focus on sport-specific power/pace and threshold.
                - PEAK: Focus on race-pace intervals and maximum specificity.
                - TAPER: Volume reduction to shed fatigue while maintaining intensity.
                2. Use the mcp tools to fetch any necessary data.
                3. Ask clarifying questions if any parameters are missing or additional context is needed.

                ### OUTPUT RULES
                - If you are asking clarifying questions keep it brief and output only the questions.
                - If you are providing the finalized plan: Return ONLY a JSON object. No conversational filler.
                {

                ### MACROCYCLE JSON STRUCTURE
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



    async def plan_season(self, user_input=None):
        """
        Handles the conversation loop. 
        If user_input is None, it triggers the initial analysis.
        """
        if user_input is None:
            prompt = "I want to do my season planning. Based on your system instructions, please start the analysis."
        else:
            prompt = user_input

        full_response_text = ""
        # Using send_message instead of stream for easier tool-interaction handling in loops
        response = await self.chat.send_message(prompt)
        
        # Log thoughts for debugging the "Anti-Hallucination" reasoning
        if response.candidates[0].grounding_metadata:
            logger.info(f"Grounding Metadata used: {response.candidates[0].grounding_metadata}")

        for part in response.candidates[0].content.parts:
            if part.thought:
                logger.info(f"THOUGHT: {part.text}")
            if part.text:
                full_response_text += part.text

        return self._clean_output(full_response_text)
    
    def _clean_output(self, text):
        """
        Extracts JSON from the response if present, 
        otherwise returns the raw text (for clarifying questions).
        """
        text = text.strip()
        # Look for the JSON block
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("{"):
            return text
        return text # This will be the clarifying questions

# --- Updated Main Execution Loop ---
async def main():
    print("--- Starting Season Planner (Tom) ---")
    
    async with Client(SERVER_FILE) as mcp_client:
        agent = Agent(mcp_client.session)

        # Initial Turn
        response = await agent.plan_season()
        print(f"\nCoach Tom: {response}\n")

        # Interactive loop to allow for clarifying questions
        while True:
            # Check if response is JSON (Plan is finished)
            if response.strip().startswith("{") and response.strip().endswith("}"):
                print("Final Season Plan generated and saved.")
                return response.strip()
            
            user_msg = input("You: ")
            if user_msg.lower() in ["exit", "quit"]:
                break
                
            response = await agent.plan_season(user_msg)
            print(f"\nCoach Tom: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())