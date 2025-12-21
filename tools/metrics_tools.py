METRICS_FILE = "memory/user_metrics.json"

# Helper functions (internal to the server)
def load_metrics():
    if not os.path.exists(METRICS_FILE):
        return {}
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)

def save_metrics(data):
    with open(METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@mcp.tool()
def get_my_status() -> str:
    """Returns the user's current fitness metrics, goals, and upcoming races."""
    data = load_metrics()
    return json.dumps(data, indent=2)

@mcp.tool()
def update_fitness_metric(metric_name: str, value: float) -> str:
    """Updates a metric like 'ftp', 'vo2max', 'weight_kg', or 'resting_hr'."""
    data = load_metrics()
    if "profile" not in data: data["profile"] = {}
    data["profile"][metric_name] = value
    save_metrics(data)
    return f"Updated {metric_name} to {value}."

@mcp.tool()
def add_race_goal(name: str, date: str, distance_km: float, goal_desc: str) -> str:
    """Adds a new race (YYYY-MM-DD) to the user's calendar."""
    data = load_metrics()
    if "races" not in data: data["races"] = []
    new_race = {"name": name, "date": date, "distance_km": distance_km, "goal": goal_desc}
    data["races"].append(new_race)
    save_metrics(data)
    return f"Added race: {name} on {date}."

