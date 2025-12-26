import asyncio
import json
import os
from fastmcp import Client
from dotenv import load_dotenv

from src.agents.season_planner_agent import Agent as SeasonAgent
from src.agents.season_planner_verification_agent import SeasonContentCheckerAgent

season_coach_name = "Tom"
season_coach_2_name = "Lars"

class OverallPlanner:
    def __init__(self, mcp_session):
        self.mcp_session = mcp_session
        # Initialize specialized agents
        # self.health_specialist = HealthSpecialistAgent(mcp_session)
        # self.longterm_performance_analyst = LongTermPerformanceAgent(mcp_session)
        self.season_coach = SeasonAgent(mcp_session, coach_name=season_coach_name)
        self.season_checker = SeasonContentCheckerAgent()
        # self.weekly_coach = WeeklyAgent(mcp_session)

    async def orchestrate_planning(self):
        """
        The main workflow: Gather Status Quo Analysis -> Season Plan -> Weekly Plan -> Finalization
        """
        print("\n--- Gathering Athlete History Summary ---")
        history = {} # Placeholder for history gathering logic

        with open("memory/master_season_plan.json", "r") as f:
            season_json = json.loads(f.read())   # REMOVE THIS LINE AFTER TESTING

        print(f"--- [Step 1] Macrocycle Planning with Coach {season_coach_name} ---")
        #season_json = await self.run_season_phase()
        
        if not season_json:
            print("Planning cancelled or failed.")
            return

        print(f"\n--- [Step 2] {season_coach_2_name} is verifying the plan ---")
        validation = await self.season_checker.check_plan(season_json, history)

        if not validation["is_valid"]:
            print(f"❌ Safety Issue Detected: {validation['flags']}")
            print(f"Advice: {validation['recommendation']}")
            # Here you would loop back to Coach Tom with this feedback
            return None

        print("✅ Plan Verified. Safe to proceed.")
        return season_json
    
    
    async def run_season_phase(self):
        """Manages the interactive loop for season planning."""
        response = await self.season_coach.plan_season()
        
        while True:
            # Check if we have a valid JSON plan
            if self._is_json(response):
                print("\n✅ Macrocycle Finalized:")
                print(response)
                return json.loads(response)
            
            # If not JSON, it's Coach Tom asking for info
            print(f"\n[{season_coach_name}]: {response}")
            user_msg = input("You: ")
            
            if user_msg.lower() in ["exit", "quit", "cancel"]:
                return None
                
            response = await self.season_coach.plan_season(user_msg)
    
    def _is_json(self, text):
        try:
            json.loads(text)
            return True
        except:
            return False
        


# --- Main Entry Point for the Overall System ---
async def main():
    load_dotenv()
    SERVER_FILE = r"C:\Users\sburm\ai_coach\src\mcp_server.py"

    async with Client(SERVER_FILE) as mcp_client:
        planner = OverallPlanner(mcp_client.session)
        final_plan = await planner.orchestrate_planning()
        
        # Save the master plan to a file for other agents to use
        if final_plan:
            with open("memory/master_season_plan.json", "w") as f:
                json.dump(final_plan, f, indent=4)
            print("\nMaster Plan saved to memory/master_season_plan.json")

if __name__ == "__main__":
    asyncio.run(main())