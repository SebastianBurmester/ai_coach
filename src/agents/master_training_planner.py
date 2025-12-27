import asyncio
import json
import os
from fastmcp import Client
from dotenv import load_dotenv

from src.agents.season_planner_agent import Agent as SeasonAgent
from src.agents.season_planner_verification_agent import SeasonContentCheckerAgent
from src.agents.health_specialist import HealthSpecialistAgent

season_coach_name = "Tom"
season_coach_2_name = "Lars"
health_specialist_name = "Lisa"

class OverallPlanner:
    def __init__(self, mcp_session):
        self.mcp_session = mcp_session
        # Initialize specialized agents
        self.health_specialist = HealthSpecialistAgent(mcp_session)
        # self.longterm_performance_analyst = LongTermPerformanceAgent(mcp_session)
        self.season_coach = SeasonAgent(mcp_session, coach_name=season_coach_name)
        self.season_checker = SeasonContentCheckerAgent()

    async def orchestrate_planning(self):
        """
        The main workflow: Gather Status Quo Analysis -> Season Plan -> Weekly Plan -> Finalization
        """
        print(f"\n--- [Appointment 1] Health checkup with {health_specialist_name} ---")
        print(f"Please wait while {health_specialist_name} is analyzing your health data...")
        health_response = await self.health_specialist.analyze_health()
        
        while not self._is_json(health_response):
            print(f"\n[{health_specialist_name}]: {health_response}")
            user_msg = input("You: ")
            health_response = await self.health_specialist.analyze_health(user_msg)

        health_report = json.loads(health_response)
        print(f"\n✅ Health Clearance Report:\n{json.dumps(health_report, indent=4)}")

        history = {"ftp": 290,
                   "vo2max": 60
                   } # Placeholder for history gathering logic

        # initialize season_validation dict
        season_validation = {}
        season_validation["is_valid"] = False 
        season_validation["recommendation"] = ""
        season_planning_attempts = 0
        
        # Start the season planning loop
        while not season_validation["is_valid"]:
            season_planning_attempts += 1
            
            if season_validation["recommendation"] != "":
                print(f"{season_coach_name} is revising the plan based on the feedback...")
                season_json = await self.run_season_phase(season_validation["recommendation"], season_json)
            else:
                print(f"--- [Appointment 2] Macrocycle Planning with Coach {season_coach_name} ---")
                season_json = await self.run_season_phase()

            if not season_json:
                print("Planning cancelled or failed.")
                return
            
            # Save plan to file
            with open("memory/master_season_plan.json", "w") as f:
                json.dump(season_json, f, indent=4)
            print(f"\n--- [Season plan updated] ---")
            

            print(f"\n--- {season_coach_2_name} is verifying the plan ---")
            season_validation = await self.season_checker.check_plan(season_json, history)

            if not season_validation["is_valid"]:
                print(f"❌ Safety Issue Detected: {season_validation['flags']}")
                print(f"Advice: {season_validation['recommendation']}")
                if season_planning_attempts >= 3:
                    print(f"[FAILURE]: Maximum attempts reached. {season_coach_name} and {season_coach_2_name} could not come to an agreement.")
                    return season_json
                continue
            else:
                print("\n--- Season Macrocycle Planning Completed Successfully! ---")
                print(f"Total Planning Loops: {season_planning_attempts}")
                print(f"season_validation Score: {season_validation['safety_score']}/10")
                print(f"Final critical Remarks: {season_validation['flags']}")
                print("\n")
                print("\nPlease revise the Season Plan and submit recommendations if a change is wished.")
                print("Changes can also be done in the json file directly before acceptance.")
                print("\nIf satisfied, type 'accept' to finalize the plan.")
                user_recommendation = input("\n You: ")

                if user_recommendation.lower() == "accept":
                    return season_json
                else:
                    season_planning_attempts = 0
                    season_validation["is_valid"] = False
                    season_validation["recommendation"] = user_recommendation
                    continue 

    
    async def run_season_phase(self, user_input=None, season_json=None):
        """Manages the interactive loop for season planning."""
        response = await self.season_coach.plan_season(user_input, season_json)
        
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

if __name__ == "__main__":
    asyncio.run(main())