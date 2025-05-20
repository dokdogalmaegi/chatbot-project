from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_ollama import OllamaLLM
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import json
import os

# 1. 문서 로딩 및 벡터 DB 준비
loader = TextLoader("company-source.txt", encoding="utf-8")
documents = loader.load()
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(documents)
embedding = OllamaEmbeddings(model="snowflake-arctic-embed2:568m")
vectorstore = FAISS.from_documents(docs, embedding)

# 2. RetrievalQA 체인 구성
llm = OllamaLLM(model="exaone3.5:7.8b", streaming=True)
retrieval_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# 3. 프롬프트 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 CubeBot입니다. 모든 응답은 'CubeBot입니다. 반갑습니다.'로 시작하며, 반드시 한국어로만 답하세요."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# 4. 체인 정의: RetrievalQA + Prompt 적용
chain: Runnable = prompt | retrieval_chain

# 5. 대화 히스토리 저장 설정
HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)
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

# 6. Memory 를 가진 체인으로 변환
chat_chain = RunnableWithMessageHistory(
    chain,
    lambda session_id: get_session_history(session_id),
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 7. 메인 루프
if __name__ == "__main__":
    session_id = "user-1"

    while True:
        user_input = input("\U0001F64B 사용자: ")

        if user_input.strip().lower() in ["exit", "quit", "종료"]:
            print("\U0001F44B 종료합니다. 안녕히 가세요!")
            history = get_session_history(session_id)
            save_chat_history_to_json(history.messages, os.path.join(HISTORY_DIR, f"{session_id}_history.json"))
            print("대화 기록이 저장되었습니다.")
            break

        print("\U0001F916 CubeBot:", end=' ', flush=True)
        for chunk in chat_chain.stream({"input": user_input}, config={"configurable": {"session_id": session_id}}):
            print(getattr(chunk, "content", str(chunk)), end="", flush=True)
        print()
