import json
import os
import google.generativeai as genai

class PersistentHistoryManager:
    def __init__(self, model, filename="agent_memory.json", max_messages=30, summary_batch_size=10):
        self.filename = filename
        self.model = model
        self.max_messages = max_messages
        self.summary_batch_size = summary_batch_size
        
        # Try to load existing memory from file
        self.history = []
        self.summary = ""
        self.load_memory()

    def add_message(self, role, text):
        """Add message, check limits, and SAVE to file immediately."""
        self.history.append({"role": role, "parts": [text]})
        
        if len(self.history) > self.max_messages:
            self._summarize_oldest()
        
        # Save after every turn so we never lose data
        self.save_memory()

    def save_memory(self):
        """Writes the current history and summary to a JSON file."""
        data = {
            "summary": self.summary,
            "history": self.history
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_memory(self):
        """Reads the JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.summary = data.get("summary", "")
                    self.history = data.get("history", [])
                print(f"[System]: Loaded memory from {self.filename}")
            except Exception as e:
                print(f"[System]: Error loading memory: {e}")
        else:
            print("[System]: No previous memory found. Starting fresh.")

    def _summarize_oldest(self):
        """(Same logic as before, but now triggered automatically)"""
        # 1. Slice off oldest
        messages_to_summarize = self.history[:self.summary_batch_size]
        self.history = self.history[self.summary_batch_size:]
        
        # 2. Convert to text
        conversation_text = ""
        for msg in messages_to_summarize:
            role = "User" if msg['role'] == 'user' else "AI"
            conversation_text += f"{role}: {msg['parts'][0]}\n"

        # 3. Ask AI to summarize
        print("[System]: Summarizing old conversations...")
        summary_chat = self.model.start_chat()
        prompt = f"""
        Current Summary: "{self.summary}"
        
        Old conversation lines to merge:
        {conversation_text}
        
        Task: Create a new, updated summary merging the old summary with these new lines.
        Keep it concise but retain specific facts about the user.
        """
        response = summary_chat.send_message(prompt)
        self.summary = response.text.strip()
        print(f"[System]: Summary updated.")

    def get_full_context(self):
        """(Same logic: returns summary + history list)"""
        context_prompt = []
        if self.summary:
            context_prompt.append({
                "role": "user", 
                "parts": [f"SYSTEM NOTE - SUMMARY OF PAST CONVERSATIONS: {self.summary}"]
            })
            context_prompt.append({
                "role": "model",
                "parts": ["Understood."]
            })
        return context_prompt + self.history