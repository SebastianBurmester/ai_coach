import os
import sys
import json
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Import your tools
from metrics import get_my_status, update_fitness_metric, add_race_goal, update_goal
from garminconnect import Garmin

from history_manager import PersistentHistoryManager

load_dotenv()

# --- 1. Define the Garmin Tool (Same logic, just wrapped) ---
def get_latest_activity_stats(activity_type: str = "running"):
    """
    Fetches the distance and duration of the user's latest activity 
    for a specific sport type (running, cycling, etc.).
    """
    try:
        email = os.getenv("GARMIN_EMAIL")
        password = os.getenv("GARMIN_PASSWORD")
        if not email or not password:
            return "Error: Garmin credentials not found in .env"
            
        client = Garmin(email, password)
        client.login()

        activities = client.get_activities(0, 10)
        for act in activities:
            if act['activityType']['typeKey'] == activity_type:
                dist_km = round(act['distance'] / 1000, 2)
                duration_min = round(act['duration'] / 60, 2)
                date = act['startTimeLocal']
                return json.dumps({
                    "date": date,
                    "type": activity_type,
                    "distance_km": dist_km,
                    "duration_minutes": duration_min
                })
        return "No recent activity found for that type."
    except Exception as e:
        return f"Error fetching data: {str(e)}"

# --- 2. Tool Mapping ---
# We map the functions to a dictionary so the agent can execute them
tool_map = {
    'get_latest_activity_stats': get_latest_activity_stats,
    'get_my_status': get_my_status,
    'update_fitness_metric': update_fitness_metric,
    'add_race_goal': add_race_goal,
    'update_goal': update_goal
}

# List of functions to give the model
tools_list = [
    get_latest_activity_stats,
    get_my_status,
    update_fitness_metric,
    add_race_goal,
    update_goal
]

# --- 3. The New Agent Class ---
class Agent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: sys.exit("Error: GEMINI_API_KEY missing.")
        
        self.client = genai.Client(api_key=api_key)
        
        # Initialize History Manager
        self.memory = PersistentHistoryManager(self.client, max_messages=3)
        
        # Create Chat with loaded history
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            history=self.memory.get_loadable_history(),
            config=types.GenerateContentConfig(
                tools=tools_list,
                temperature=0.7,
                system_instruction="""
                You are a smart fitness coach. You have access to the user's files and Garmin data.
                Always confirm when you read or write data.
                """
            )
        )

    def run_turn(self, user_input):
        # 1. Add User Input to Memory
        self.memory.add_message("user", user_input)
        
        # 2. Send to Model
        response = self.chat.send_message(user_input)
        
        # 3. Handle Tool Calls
        while response.function_calls:
            for call in response.function_calls:
                print(f" > [Tool Call]: {call.name}")
                func = tool_map.get(call.name)
                result = func(**call.args) if func else "Error: Tool not found"
                
                # Send result back
                response = self.chat.send_message(
                    types.Part.from_function_response(
                        name=call.name,
                        response={"result": result}
                    )
                )
        
        # 4. Add Final Model Response to Memory
        self.memory.add_message("model", response.text)
        return response.text

# --- 4. Main Loop ---
if __name__ == "__main__":
    agent = Agent()
    print("--- Fitness Coach (v2.1 with Memory) ---")
    
    while True:
        try:
            u_in = input("\nYou: ")
            if u_in.lower() in ['quit', 'exit']: break
            
            print(f"Coach: {agent.run_turn(u_in)}")
            
        except Exception as e:
            print(f"Error: {e}")