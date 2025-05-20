from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# 1. 문서 로딩
loader = TextLoader("company-source.txt", encoding="utf-8")
documents = loader.load()

# 2. 문서 분할
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(documents)

# 3. 임베딩 모델 (Ollama snowflake model 사용)
embedding = OllamaEmbeddings(model="snowflake-arctic-embed2:568m")  # 임베딩 가능한 모델 필요

# 4. Vector DB 생성
vectorstore = FAISS.from_documents(docs, embedding)

# 5. LLM + QA 체인
llm = OllamaLLM(model="exaone3.5:7.8b", streaming=True)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# 6. 질의
query = "Item 단위 status 기능과 이슈가 있을만한 부분을 설명해줘"
result = qa_chain.invoke(query)
print(result["result"])
