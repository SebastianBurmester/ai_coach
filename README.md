# AI Fitness Coach

![Status: Under Construction](https://img.shields.io/badge/status-under--construction-orange?style=for-the-badge)
> 
AI fitness assistant built on the **Gemini API**. Utilizes the **Model Context Protocol (MCP)** to interact directly with your Garmin Connect data.

## Key Features
* **Active Reasoning:** Uses Gemini "Thinking Mode" to analyze your recovery and workout intensity before responding.
* **Garmin Integrated:** MCP Tools to get Garmin Data
* **Persistent Memory:** Remembers your long-term goals and past coaching conversations.
* **Modular MCP Tools:** Easily extendable to fetch data from different platforms.

## Setup
* pip install -r requirements.txt
* add .env file containing
  - GARMIN_EMAIL= "your_email"
  - GARMIN_PASSWORD= "your_password"
  - GEMINI_API_KEY= "your_api_key"

## Sources
Garmin API:
https://github.com/cyberjunky/python-garminconnect

Google AI Studio:
https://aistudio.google.com/

MCP Server:
https://modelcontextprotocol.io/docs/
