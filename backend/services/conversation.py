class Conversation:
    def __init__(self):
        self.chat_history = []

    def add_user_message(self, message):
        """Add user's message to the conversation history."""
        self.chat_history.append({"role": "user", "content": message})

    def add_assistant_message(self, message):
        """Add assistant's message to the conversation history."""
        self.chat_history.append({"role": "assistant", "content": message})

    def get_conversation(self):
        """Get the conversation history."""
        return self.chat_history

    def clear_history(self):
        """Clear the conversation history."""
        self.chat_history = []