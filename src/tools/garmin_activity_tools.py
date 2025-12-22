import logging
from fastmcp import Context

from garminconnect import Garmin
import os

logger = logging.getLogger(__name__)

def get_api():
    token_dir = os.path.expanduser("~/.garminconnect")
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    # 1. Initialize and Login
    client = Garmin() # (email, password) if token expired
    client.login(tokenstore=token_dir)
    
    # Save tokens to the default directory (~/.garminconnect)
    token_dir = os.path.expanduser("~/.garminconnect")
    os.makedirs(token_dir, exist_ok=True)
    client.garth.dump(token_dir)

    return client

def register_garmin_activity_tools(mcp):
    """
    Registers all Garmin-Activity-related tools to the provided MCP server instance.
    """
    @mcp.tool()
    def get_activities(start_date: str, end_date: str, ctx: Context) -> str:

