import datetime
import os
from fastmcp import FastMCP
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

# Initialize the MCP Server
mcp = FastMCP("SimpleGarmin")

def get_api():
    token_dir = os.path.expanduser("~/.garminconnect")
    # 1. Initialize and Login
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    client = Garmin() # (email, password) if token expired
    client.login(tokenstore=token_dir)
    
    # Save tokens to the default directory (~/.garminconnect)
    token_dir = os.path.expanduser("~/.garminconnect")
    os.makedirs(token_dir, exist_ok=True)
    client.garth.dump(token_dir)
    
    return client

@mcp.tool()
def get_hrv_for_date(date_str: str = None) -> dict:
    """
    Fetches HRV (Heart Rate Variability) data for a specific date.
    :param date_str: Date in ISO format (YYYY-MM-DD). Defaults to today.
    """
    if not date_str:
        date_str = datetime.date.today().isoformat()
    
    api = get_api()
    # 'get_hrv_data' is the standard method for daily HRV summaries
    hrv_data = api.get_hrv_data(date_str)
    return hrv_data

if __name__ == "__main__":
    mcp.run()