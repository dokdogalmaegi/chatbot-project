import ollama
import json

model = "exaone3.5:7.8b"

# conversation_history.txt 파일 텍스트 load
try:
    with open("conversation_history.json", "r", encoding="utf-8") as f:
        messages = json.load(f)
        print("💬 대화 기록 로드 완료.")
except FileNotFoundError:
    messages = [
        {
            "role": "system",
            "content": "당신의 이름은 이제부터 'CubeBot'입니다. 질문에 답변할 때는 항상 'CubeBot입니다. 반갑습니다.'를 시작으로 대답하세요. 반드시 한국어로만 답하세요."
        }
    ]

print("💬 CubeBot 챗봇에 오신 것을 환영합니다! (그만하려면 'exit' 입력)\n")
while True:
    user_input = input("🙋 사용자: ")
    
    if user_input.strip().lower() in ["exit", "quit", "종료"]:
        print("👋 종료합니다. 안녕히 가세요!")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    print("🤖 CubeBot:", end=' ', flush=True)
    response = ollama.chat(model=model, messages=messages, stream=True)

    full_reply = ""
    for chunk in response:
        token = chunk["message"]["content"]
        full_reply += token
        print(token, end='', flush=True)
    print("\n")

    messages.append({
        "role": "assistant",
        "content": full_reply
    })

    # 대화 기록을 파일에 저장
    with open("conversation_history.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)