import ollama
import json
import os

MODEL_NAME = "exaone3.5:7.8b"
HISTORY_FILE = "conversation_history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
        print("💬 대화 기록 로드 완료.")
    else:
        messages = [{
            "role": "system",
            "content": (
                "당신의 이름은 이제부터 'CubeBot'입니다. "
                "질문에 답변할 때는 항상 'CubeBot입니다. 반갑습니다.'를 시작으로 대답하세요. "
                "반드시 한국어로만 답하세요."
            )
        }]
    return messages


def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def generate_response(messages):
    response = ollama.chat(model=MODEL_NAME, messages=messages, stream=True)
    full_reply = ""
    for chunk in response:
        token = chunk["message"]["content"]
        full_reply += token
        print(token, end='', flush=True)
    print("\n")
    return full_reply
