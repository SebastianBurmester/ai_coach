import os
import sys
import json
from dotenv import load_dotenv

# NEW IMPORT SYNTAX
from google import genai
from google.genai import types

# Import your tools
from metrics import get_my_status, update_fitness_metric, add_race_goal, update_goal
from garminconnect import Garmin

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
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Error: GEMINI_API_KEY not found.")
            sys.exit(1)
            
        # Initialize the NEW Client
        self.client = genai.Client(api_key=self.api_key)
        
        # Configure the chat with tools
        # We use 'gemini-1.5-flash' as it is stable and fast
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=tools_list,
                temperature=0.7,
                system_instruction="""
                You are a smart cycling and running coach. 
                You have read/write access to the user's 'metrics' file and Garmin data.
                
                Rules:
                1. If the user asks about stats, use 'get_my_status'.
                2. If the user provides new stats, use 'update_fitness_metric'.
                3. If the user announces a race, use 'add_race_goal'.
                4. Always confirm when you have updated a file.
                """
            )
        )

    def send_message(self, user_text):
        """
        Handles the conversation loop:
        User Input -> Model -> (Maybe Function Call) -> Execute -> Model -> Response
        """
        # Send user message
        response = self.chat.send_message(user_text)
        
        # Loop to handle function calls (The model might want to call multiple tools)
        while response.function_calls:
            for call in response.function_calls:
                print(f" > [Agent Tool Request]: {call.name}({call.args})")
                
                # 1. Execute the Python function
                func = tool_map.get(call.name)
                if func:
                    # Pass the arguments from the model to the function
                    result = func(**call.args)
                else:
                    result = f"Error: Tool {call.name} not found."
                
                # 2. Give the result back to the model
                # In the new SDK, we send the result back as a tool response
                response = self.chat.send_message(
                    types.Part.from_function_response(
                        name=call.name,
                        response={"result": result}
                    )
                )
                
        return response.text

# --- 4. Main Loop ---
if __name__ == "__main__":
    agent = Agent()
    print("--- New GenAI Agent Ready (v2.0) ---")
    print("Type 'quit' to exit.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            reply = agent.send_message(user_input)
            print(f"Coach: {reply}")
            
        except Exception as e:
            print(f"An error occurred: {e}")