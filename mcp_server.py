import datetime
import os
from fastmcp import FastMCP, Context

import json
import logging
from dotenv import load_dotenv

from tools.garmin_health_tools import register_garmin_health_tools

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
register_garmin_health_tools(mcp)

if __name__ == "__main__":
    mcp.run()