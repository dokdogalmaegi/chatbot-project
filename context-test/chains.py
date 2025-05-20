from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from config import TEXT_SOURCE, EMBED_MODEL, LLM_MODEL

def build_retrieval_chain() -> Runnable:
    # 문서 로딩 및 벡터화
    loader = TextLoader(TEXT_SOURCE, encoding="utf-8")
    documents = loader.load()
    docs = CharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)
    embedding = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = FAISS.from_documents(docs, embedding)

    # LLM + QA 체인 구성
    llm = OllamaLLM(model=LLM_MODEL, streaming=True)
    retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )

    # 프롬프트 템플릿 설정
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 CubeBot입니다. 모든 응답은 'CubeBot입니다. 반갑습니다.'로 시작하며, 반드시 한국어로만 답하세요."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    return prompt | retrieval_chain
