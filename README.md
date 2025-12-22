# AI Fitness Coach

AI fitness assistant built on the **Gemini API**. Utilizes the **Model Context Protocol (MCP)** to interact directly with your Garmin Connect data.

## Key Features
* **Active Reasoning:** Uses Gemini "Thinking Mode" to analyze your recovery and workout intensity before responding.
* **Garmin Integrated:** Live fetching of Resting HR, Sleep, and Stress levels.
* **Persistent Memory:** Remembers your long-term goals and past coaching conversations.
* **Modular MCP Tools:** Easily extendable to fetch data from different platforms.

## Setup
pip install -r requirements.txt

## TODO
- HITL Training plan generation Agent
- Automating Agent to check data and adjust plan daily or weekly

## Sources
Garmin API:
https://github.com/cyberjunky/python-garminconnect

Google AI Studio:
https://aistudio.google.com/

MCP Server:
https://modelcontextprotocol.io/docs/
