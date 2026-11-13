
import json


class ConversationMemory:

    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns

    def add_interaction(self, question, sql, results):
        """Save a completed question, SQL query and its results."""

        interaction = {
            "question": question,
            "sql": sql,
            "results": {
                "columns": results.get("columns", []),
                "rows": results.get("rows", [])[:20],
                "row_count": results.get("row_count", 0)
            }
        }

        self.history.append(interaction)

        # Keep only the most recent interactions.
        self.history = self.history[-self.max_turns:]

    def get_context(self):
        """Return conversation history as text for the LLM."""

        if not self.history:
            return "No previous conversation."

        return json.dumps(
            self.history,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    def clear(self):
        """Clear conversation history."""
        self.history.clear()
