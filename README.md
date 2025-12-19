Creating a AI Coach to assist primarly in endurance sports. 

- Access to Garmin Data
- Gemini API Agent to interact
- chat history logged and summarized
- user metrics can be read and set by agent


Garmin API:
https://github.com/cyberjunky/python-garminconnect

Google AI Studio:
https://aistudio.google.com/


Setup:
pip install -r requirements.txt

ToDo:
- HITL workflow for planning and analyzing training load and health stats
- API call once a day to log relevant data to be added into context
- Dataframe to save relevant data into model context
