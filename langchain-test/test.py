from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_ollama import OllamaLLM
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
import json
import os

# 저장 경로
HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# 프롬프트 정의 (대화 이력 반영을 위한 Placeholder 포함)
template = ChatPromptTemplate.from_messages([
    ("system", "당신은 CubeBot입니다. 모든 응답은 'CubeBot입니다. 반갑습니다.'로 시작하며, 반드시 한국어로만 답하세요."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# 모델 정의
llm = OllamaLLM(model="exaone3.5:7.8b", streaming=True)

# 체인 정의
chain: Runnable = template | llm

# 대화 기록을 메모리에 저장
store = {}

def load_chat_history_from_json(filename: str) -> list[BaseMessage]:
    messages = []
    if not os.path.exists(filename):
        return messages
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        for msg in data:
            if msg["type"] == "human":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["type"] == "ai":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["type"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
    return messages

def save_chat_history_to_json(chat_history: list[BaseMessage], filename: str):
    messages = []
    for msg in chat_history:
        messages.append({
            "type": msg.type,
            "content": msg.content
        })
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        history = InMemoryChatMessageHistory()
        filepath = os.path.join(HISTORY_DIR, f"{session_id}_history.json")
        for msg in load_chat_history_from_json(filepath):
            history.add_message(msg)
        store[session_id] = history
    return store[session_id]

# Memory 를 가진 체인으로 변환
chat_chain = RunnableWithMessageHistory(
    chain,
    lambda session_id: get_session_history(session_id),
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 메인 루프
if __name__ == "__main__":
    session_id = "user-1"  # 임시 고정 (사용자별로 분리 가능)

    while True:
        user_input = input("🙋 사용자: ")

        if user_input.strip().lower() in ["exit", "quit", "종료"]:
            print("👋 종료합니다. 안녕히 가세요!")

            history = get_session_history(session_id)
            save_chat_history_to_json(history.messages, os.path.join(HISTORY_DIR, f"{session_id}_history.json"))
            print("대화 기록이 conversation_history-test.json에 저장되었습니다.")

            break

        print("🤖 CubeBot:", end=' ', flush=True)
        for chunk in chat_chain.stream({"input": user_input}, config={"configurable": {"session_id": session_id}}):
            print(getattr(chunk, "content", str(chunk)), end="", flush=True)
        print()
