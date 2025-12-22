import datetime
import os
from fastmcp import FastMCP, Context

print("Starting MCP Server...")

import json
import logging
from dotenv import load_dotenv

from tools.garmin_health_tools import register_garmin_health_tools
from tools.garmin_activity_tools import register_garmin_activity_tools
from tools.garmin_performance_tools import register_garmin_performance_tools
from tools.generic_tools import register_generic_tools
from tools.goal_tools import register_goal_tools

load_dotenv()

# --- STEP 1: ROBUST LOGGING SETUP ---
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(), # This goes to stderr by default in MCP
        logging.FileHandler("mcp_server_debug.log") # This saves to your folder
    ]
)
logger = logging.getLogger("mcp_server")
logger.info("Server script started initialized.")

# Initialize the MCP Server
mcp = FastMCP("Fitness Coach MCP Server")
print("Registering tools...")
register_garmin_health_tools(mcp)
register_garmin_activity_tools(mcp)
register_garmin_performance_tools(mcp)
register_generic_tools(mcp)
register_goal_tools(mcp)
print("Tools registered.")

if __name__ == "__main__":
    mcp.run()