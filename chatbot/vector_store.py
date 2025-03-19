from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.tools import Tool, tool
from langchain_community.tools import TavilySearchResults
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("chromadb.telemetry").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers.SentenceTransformer").setLevel(logging.WARNING)
embedding_function = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")


def load_vector_store(GENRE, PERSIST_DIRECTORY):
    # 벡터스토어 설정
    vector_store = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        collection_name=GENRE,
        embedding_function=embedding_function,
    )

    metadata_field_info = [
        AttributeInfo(name="title", description="작품의 제목", type="string"),
        AttributeInfo(
            name="type", description="작품의 타입 (웹툰 또는 웹소설)", type="string"
        ),
        AttributeInfo(
            name="platform",
            description="작품의 연재처 (카카오페이지, 네이버웹툰, 카카오웹툰, 네이버시리즈)",
            type="string",
        ),
        AttributeInfo(
            name="genre",
            description="작품의 장르 (로맨스, BL, 로판, 판타지, 현판 등)",
            type="string",
        ),
        AttributeInfo(
            name="status",
            description="작품의 연재 상태 (연재, 완결, 휴재)",
            type="string",
        ),
        AttributeInfo(
            name="update_days",
            description="작품의 연재 요일 (월, 화, 수 등 또는 해당 없음)",
            type="string",
        ),
        AttributeInfo(
            name="age_rating",
            description="작품의 연령 제한 (전체 이용가, 12세 이용가 등)",
            type="string",
        ),
        AttributeInfo(
            name="score",
            description="작품의 인기도 점수)",
            type="float",
        ),
        AttributeInfo(
            name="author",
            description="작품의 작가",
            type="string",
        ),
        AttributeInfo(
            name="price",
            description="작품의 가격",
            type="string",
        ),
        AttributeInfo(
            name="episode",
            description="작품의 총 회차 수",
            type="integer",
        ),
    ]
    return vector_store, metadata_field_info


action_vector_store, action_metadata_field_info = load_vector_store(
    "action", "data/vector_store/action"
)
cartoon_vector_store, cartoon_metadata_field_info = load_vector_store(
    "cartoon", "data/vector_store/cartoon"
)
drama_vector_store, drama_metadata_field_info = load_vector_store(
    "drama", "data/vector_store/drama"
)
fantasy_vector_store, fantasy_metadata_field_info = load_vector_store(
    "fantasy", "data/vector_store/fantasy"
)
historical_vector_store, historical_metadata_field_info = load_vector_store(
    "historical", "data/vector_store/historical"
)
horror_vector_store, horror_metadata_field_info = load_vector_store(
    "horror", "data/vector_store/horror"
)
rofan_vector_store, rofan_metadata_field_info = load_vector_store(
    "rofan", "data/vector_store/rofan"
)
romance_vector_store, romance_metadata_field_info = load_vector_store(
    "romance", "data/vector_store/romance"
)


def selfquery_tool(vector_store, metadata_field_info, tool_name):
    """
    특정 장르에 대한 SelfQueryRetriever 기반의 Tool을 생성
    :param vector_store: Chroma VectorStore
    :param genre: 필터링할 장르 (예: '로맨스', '판타지', 'BL')
    :param tool_name: Tool의 이름
    :return: LangChain Tool
    """
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vector_store,
        document_contents="웹소설 및 웹툰 데이터",
        metadata_field_info=metadata_field_info,
        search_type="similarity",
        search_kwargs={"k": 10},  # 상위 10개 검색
    )

    def search(query):
        """
        검색 수행 후 메타데이터를 포함한 결과 반환
        """
        results = retriever.invoke(query)
        generated_query = retriever.query_constructor.invoke(query)
        logging.info(f"벡터스토어 검색 쿼리: {generated_query}")
        logging.info(f"벡터스토어 검색 결과: {len(results)}개 검색")
        return "\n\n".join(result.page_content for result in results)

    return Tool(
        name=f"{tool_name}_retriever_tool",
        func=search,
        description=f"Use this tool to search {tool_name}.",
    )
