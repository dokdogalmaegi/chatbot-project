import os
import json
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from config import HISTORY_DIR

os.makedirs(HISTORY_DIR, exist_ok=True)
store = {}

def load_chat_history_from_json(filename: str) -> list[BaseMessage]:
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [
            HumanMessage(content=m["content"]) if m["type"] == "human" else
            AIMessage(content=m["content"]) if m["type"] == "ai" else
            SystemMessage(content=m["content"])
            for m in data
        ]

def save_chat_history_to_json(messages: list[BaseMessage], filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([{"type": m.type, "content": m.content} for m in messages], f, ensure_ascii=False, indent=2)

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        history = InMemoryChatMessageHistory()
        path = os.path.join(HISTORY_DIR, f"{session_id}_history.json")
        for msg in load_chat_history_from_json(path):
            history.add_message(msg)
        store[session_id] = history
    return store[session_id]