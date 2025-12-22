import json
import os
from google import genai
from google.genai import types

class PersistentHistoryManager:
    def __init__(self, client, filename="memory/agent_memory.json", max_messages=30):
        self.client = client
        self.filename = filename
        self.max_messages = max_messages
        self.history = []  # List of dicts: {'role': 'user'|'model', 'parts': ['text']}
        self.summary = ""
        self.load_memory()

    def add_message(self, role, text):
        """Add a simple text message to history."""
        # Convert 'user'/'model' to the format we want to save
        self.history.append({"role": role, "parts": [text]})
        
        # Check if we need to summarize
        if len(self.history) > self.max_messages:
            self._summarize_oldest()
        
        self.save_memory()

    def _summarize_oldest(self):
        """Summarizes the oldest chunk of conversation."""
        print(" [System]: Summarizing old history to save space...")
        
        # Slice the oldest 10 messages
        chunk = self.history[:10]
        self.history = self.history[10:]
        
        chunk_text = "\n".join([f"{m['role']}: {m['parts'][0]}" for m in chunk])
        
        # Use the client to generate a summary
        prompt = f"""
        Current Memory Summary: "{self.summary}"
        
        Old conversation lines to merge:
        {chunk_text}
        
        Task: Update the summary. Preserve events like illness, injuries or similar data NOT related to goals or performance metrics. Do NOT include specific details about goals or performance metrics since those can be looked up separately.
        Keep it concise. No unnecessary elaboration. Can be empty if no relevant info.
        """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        self.summary = response.text.strip()
        print(" [System]: Memory updated.")

    def get_loadable_history(self):
        """
        Converts our saved history into the format the new SDK expects.
        """
        sdk_history = []
        
        # 1. Inject Summary as the first "System" context (simulated as user message)
        if self.summary:
            sdk_history.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=f"SYSTEM MEMORY SUMMARY: {self.summary}")]
            ))
            sdk_history.append(types.Content(
                role="model",
                parts=[types.Part.from_text(text="Understood. I have the context.")]
            ))
            
        # 2. Add the actual recent message history
        for msg in self.history:
            sdk_history.append(types.Content(
                role=msg['role'],
                parts=[types.Part.from_text(text=msg['parts'][0])] # <--- FIXED HERE
            ))
            
        return sdk_history

    def save_memory(self):
        with open(self.filename, 'w') as f:
            json.dump({"summary": self.summary, "history": self.history}, f, indent=2)

    def load_memory(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.summary = data.get("summary", "")
                    self.history = data.get("history", [])
            except:
                print(" [System]: Error loading memory file. Starting fresh.")