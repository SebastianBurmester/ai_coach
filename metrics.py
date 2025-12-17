import json
import os

METRICS_FILE = "user_metrics.json"

def load_metrics():
    """Reads the full metrics file."""
    if not os.path.exists(METRICS_FILE):
        return {}
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)

def save_metrics(data):
    """Writes data back to the file."""
    with open(METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# --- TOOLS FOR THE AGENT ---

def get_my_status():
    """
    Returns the user's current fitness metrics, goals, and upcoming races.
    Use this to answer questions like "What is my FTP?" or "When is my next race?"
    """
    data = load_metrics()
    return json.dumps(data, indent=2)

def update_fitness_metric(metric_name: str, value: float):
    """
    Updates a specific fitness metric in the profile.
    metric_name options: 'ftp', 'vo2max', 'weight_kg', 'resting_hr'.
    """
    data = load_metrics()
    
    # Ensure profile section exists
    if "profile" not in data:
        data["profile"] = {}
        
    data["profile"][metric_name] = value
    save_metrics(data)
    return f"Updated {metric_name} to {value}."

def add_race_goal(name: str, date: str, distance_km: float, goal_desc: str):
    """
    Adds a new race to the list.
    date format: 'YYYY-MM-DD'
    """
    data = load_metrics()
    
    if "races" not in data:
        data["races"] = []
        
    new_race = {
        "name": name,
        "date": date,
        "distance_km": distance_km,
        "goal": goal_desc
    }
    data["races"].append(new_race)
    save_metrics(data)
    return f"Added race: {name} on {date}."

def update_goal(goal_name: str, value: float):
    """
    Updates a numeric goal.
    goal_name examples: 'ftp_goal', 'weight_goal'.
    """
    data = load_metrics()
    if "goals" not in data:
        data["goals"] = {}
        
    data["goals"][goal_name] = value
    save_metrics(data)
    return f"Updated goal {goal_name} to {value}."