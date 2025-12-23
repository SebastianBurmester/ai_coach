import logging
from fastmcp import Context

from garminconnect import Garmin
import os

from garth import client

from datetime import date
import json

METRICS_FILE = "memory/goals.json"
# Helper functions (internal to the server)
def load_metrics():
    if not os.path.exists(METRICS_FILE):
        return {}
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)

def save_metrics(data):
    with open(METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

logger = logging.getLogger(__name__)

def register_goal_tools(mcp):
    """
    Registers all goal tools to the provided MCP server instance.
    """
    @mcp.tool()
    def get_user_goals() -> str:
        """Returns the user's current fitness goals and upcoming races."""
        data = load_metrics()
        return json.dumps(data, indent=2)
    
    @mcp.tool()
    def update_user_goals(data: dict) -> str:
        """Updates the user's fitness goals."""
        save_metrics(data)
        return "User goals updated successfully."

    @mcp.tool()
    def add_race_goal(name: str, priority: int, date: str, distance_km: float, goal_desc: str) -> str:
        """Adds a new race (YYYY-MM-DD) to the user's calendar."""
        data = load_metrics()
        if "races" not in data: data["races"] = []
        new_race = {"name": name, "priority": priority, "date": date, "distance_km": distance_km, "goal": goal_desc}
        data["races"].append(new_race)
        save_metrics(data)
        return f"Added race: {name} on {date}."

