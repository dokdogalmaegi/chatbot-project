from chatbot import load_history, save_history, generate_response

def main():
    print("💬 CubeBot 챗봇에 오신 것을 환영합니다! (그만하려면 'exit' 입력)\n")
    messages = load_history()

    while True:
        user_input = input("🙋 사용자: ")

        if user_input.strip().lower() in ["exit", "quit", "종료"]:
            print("👋 종료합니다. 안녕히 가세요!")
            break

        messages.append({"role": "user", "content": user_input})
        print("🤖 CubeBot:", end=' ', flush=True)

        reply = generate_response(messages)
        messages.append({"role": "assistant", "content": reply})

        save_history(messages)


if __name__ == "__main__":
    main()
