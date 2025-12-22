import logging
from fastmcp import Context

from garminconnect import Garmin
import os

from garth import client

from datetime import date

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

def register_generic_tools(mcp):
    """
    Registers all generic tools to the provided MCP server instance.
    """
    @mcp.tool()
    def get_todays_date(ctx: Context) -> str:
        """
        Returns today's date in YYYY-MM-DD format.
        """
        logger.info("Fetching today's date")
        
        today = date.today().strftime("%Y-%m-%d")
        return f"Today's date is {today}."
    
    @mcp.tool()
    def get_user_name(ctx: Context) -> str:
        """
        Returns the user's name from environment variable.
        """
        logger.info("Fetching user's name")

        client = get_api()
        name = client.get_full_name()
        return f"The user's name is {name}."
