from langchain_core.runnables.history import RunnableWithMessageHistory
from chains import build_retrieval_chain
from history import get_session_history, save_chat_history_to_json
import os

if __name__ == "__main__":
    session_id = "user-1"
    chain = build_retrieval_chain()
    chat_chain = RunnableWithMessageHistory(
        chain,
        lambda session_id: get_session_history(session_id),
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    while True:
        user_input = input("\U0001F64B 사용자: ")
        if user_input.strip().lower() in ["exit", "quit", "종료"]:
            print("\U0001F44B 종료합니다. 안녕히 가세요!")
            history = get_session_history(session_id)
            save_chat_history_to_json(history.messages, os.path.join("history", f"{session_id}_history.json"))
            print("대화 기록이 저장되었습니다.")
            break

        print("\U0001F916 CubeBot:", end=' ', flush=True)
        response = chat_chain.invoke({"input": user_input}, config={"configurable": {"session_id": session_id}})
        print(response["result"])
        print()