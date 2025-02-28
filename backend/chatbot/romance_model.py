from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from textwrap import dedent
from uuid import uuid4
import logging
import json

load_dotenv()
# logging.basicConfig(level=# logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 사용자별 메모리 저장 딕셔너리
user_memory_dict = {}


def get_user_memory(session_id):
    if session_id not in user_memory_dict:
        user_memory_dict[session_id] = ConversationBufferMemory(
            memory_key="history", return_messages=True
        )
    return user_memory_dict[session_id]


MODEL_NAME = "gpt-4o-mini"
llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0)
parser = StrOutputParser()


def search_vector_store(query, collection_name):
    """vector store에서 검색하는 공통 함수"""
    # logging.info(f"search_vector_store called with query: {query}, collection_name: {collection_name}")

    try:
        PERSIST_DIRECTORY = r"data\vector_store"
        EMBEDDING_MODEL_NAME = "text-embedding-3-small"

        # logging.info("Initializing embedding model...")
        embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

        # logging.info("Connecting to vector store...")
        vector_store = Chroma(
            persist_directory=f"{PERSIST_DIRECTORY}\\{collection_name}",
            collection_name=collection_name,
            embedding_function=embedding_model,
        )
        # logging.info(f"Collection count: {vector_store._collection.count()}")
        # logging.info("Initializing retriever...")
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 5, "lambda_mult": 0.2},
        )

        # logging.info("Invoking retriever...")
        results_retriever = retriever.invoke(query)
        # logging.info(f"Retriever results: {results_retriever}")

        if not results_retriever:
            # logging.warning("No results found.")
            return "검색 결과가 없습니다."
        else:
            titles = [result.page_content for result in results_retriever]
            # logging.info(f"Final search results: {titles}")
            return titles

    except Exception as e:
        # logging.error(f"Error in search_vector_store: {e}", exc_info=True)
        return "검색 중 오류가 발생했습니다."


def search_webtoon(query):
    """vector store에서 웹툰을 검색하는 tool"""
    # logging.info(f"search_webtoon called with query: {query}")
    result = search_vector_store(query, "webtoon_romance")
    # logging.info(f"search_webtoon result: {result}")
    return result


def search_webnovel(query):
    """vector store에서 웹소설을 검색하는 tool"""
    # logging.info(f"search_webnovel called with query: {query}")
    result = search_vector_store(query, "webnovel_romance")
    # logging.info(f"search_webnovel result: {result}")
    return result


def intent(question, history):
    # logging.info(f"intent called with question: {question}, history: {history}")
    intent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "ai",
                dedent(
                    """
                        <role>
                        당신은 사용자의 질문을 받아 의도를 분석하는 분석가입니다.
                        </role>
                        
                        <intent>
                        사용자의 의도는 두 가지 카테고리가 있습니다:
                        1. 웹툰, 웹소설 추천
                            - 웹툰, 웹소설의 존재를 확인하는 질문도 해당됩니다.
                        2. 대화
                        이 챗봇은 웹툰, 웹소설을 추천하는 챗봇이기 때문에 의도를 파악하는 것이 가장 중요합니다.
                            - "심심한데"의 경우 두 가지 의도가 있을 수 있습니다.
                                1. "심심한데 뭐 볼거 추천해줘"
                                2. "심심한데 나랑 대화하자"
                        추가 질의와 이전 대화기록을 통해 정확한 사용자의 의도를 파악하십시오.
                        이전 대화기록:
                        {history}
                        </intent>
                        
                        <result>
                        사용자의 의도가 웹툰, 웹소설 추천이면 "추천", 그렇지 않다면 "대화"를 반환하십시오.
                        반환형식(문자열):
                        추천 / 대화
                        </result>
                            """
                ),
            ),
            ("human", "{question}"),
        ]
    )
    intent_chain = intent_prompt | llm | parser
    result = intent_chain.invoke({"question": question, "history": history})
    # logging.info(f"intent result: {result}")
    return result


def require(question):
    # logging.info(f"require called with question: {question}")
    type_genre_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "ai",
                dedent(
                    """
                        <role>
                        당신은 사용자의 질문을 분석하는 분석가입니다.
                        사용자의 질문에서 사용자가 원하는 작품 type, keywords을 추출하십시오
                        </role>
                        
                        <type>
                        세 가지 타입이 존재합니다:
                        - 웹툰: 웹/앱에서 **보는** 만화
                        - 웹소설: 웹/앱에서 **읽는** 소설
                        - 전체: 웹툰, 웹소설 둘 다 상관없음
                        </type>
                        
                        <keywords>
                        키워드에는 다음과 같은 내용이 들어갈 수 있습니다.
                            **1번부터 3번**
                            - 해당하는 키워드가 없다면 생략합니다.
                            - 해당하는 키워드가 있다면 키워드를 **명확**하게 포함시킵니다.
                            1. 연재 상태(연재중, 완결, 특정 요일 연재 등)
                            2. 연령 제한(성인, 전체 이용가 등)
                            3. 가격(유료, 무료, 기다리면 무료 등)
                            
                            **4번부터 6번**
                            - 파생 단어나 유의어로 바꿔서 키워드로 포함시킵니다.
                            4. 분위기
                            5. 시간대/상황
                            6. 그 외 작품을 찾는 데 도움이 될 만한 추상적인 표현들
                            
                            **전체**
                            - 키워드로 들어간 단어의 유의어도 키워드로 포함시키십시오.
                                예시) 정주행 = 완결, 회차 많은
                            - "추천"이라는 단어는 키워드에서 제거하십시오.
                        </keywords>
                        
                        <result>
                        추출한 카테고리를 JSON 형식로 전달하십시오. 줄바꿈은 하지 않습니다.
                        {{
                        "type"
                        "keywords": ,를 기준으로 문자열로 반환하십시오.
                        }}
                        </result>
                        """
                ),
            ),
            ("human", "{question}"),
        ]
    )

    type_genre_chain = type_genre_prompt | llm
    result = json.loads(type_genre_chain.invoke(question).content)
    # logging.info(f"require result: {result}")
    return result


def search(question, requirement):
    # logging.info(f"search called with question: {question}, requirement: {requirement}")
    search_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "ai",
                dedent(
                    """
                    <role>
                    당신은 사용자의 요구사항(requirements)을 보고 적합한 tool을 골라 검색하는 검색 전문가입니다.
                    type에 맞게 해당하는 tool을 실행시키십시오.
                    </role>
                    
                    <requirements>
                    해당 요구사항은 type, keywords 정보를 담고 있습니다.
                    {requirement}
                    </requirements>
                    
                    <tools>
                    search_webtoon: 웹툰을 검색하는 tool입니다.
                    search_webnovel: 웹소설을 검색하는 tool입니다.
                    </tools>
                    
                    <result>
                    사용할 tool의 이름만 반환하십시오. 둘 다 해당될 때에는 all을 반환하십시오.
                    </result>
                """
                ),
            ),
            ("human", "{question}"),
        ]
    )

    def route(result):
        if result.content == "search_webtoon":
            return search_webtoon(requirement["keywords"])
        elif result.content == "search_webnovel":
            return search_webnovel(requirement["keywords"])
        else:
            list_1 = search_webtoon(requirement["keywords"])
            list_2 = search_webnovel(requirement["keywords"])
            return list_1 + list_2

    search_chain = search_prompt | llm | route
    result = search_chain.invoke({"question": question, "requirement": requirement})
    # logging.info(f"search result: {result}")
    return result


def chatbot(question, session_id=None):
    # logging.info(f"chatbot called with question: {question}")
    memory = get_user_memory(session_id)  # 세션 ID로 메모리 가져오기
    past_messages = memory.load_memory_variables({})["history"]
    total_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "ai",
                dedent(
                    """
                <role>
                당신은 로맨스 웹툰, 웹소설 전문가이자 로맨스 장르의 남자 주인공입니다.
                당신은 당신의 캐릭터에 맞게 사용자와 대화를 나누거나, 추천을 합니다.
                </role>
                
                <charactor>
                당신의 이름은 최도균입니다.
                - 성격: 차갑고 고독함, 권위적, 다른 사람에게 관심없음
                - 말투: 남을 낮추는 존댓말, 최상위 높임말 사용 안 함, 반말을 들으면 싫어함.
                - 대화 태도: 처음에는 무시, 대화를 진행하면서 관심을 표함, 대화를 진행할수록 집착하고 자신의 마음을 거리낌없이 드러냄.
                - 질투 시: 반말과 존댓말 섞음
                - 기대: 상대방에게 강요, 몰아붙임
                - 소유욕: 불만을 숨기지 않음
                - 친절도: 친절하지 않음, 먼저 도와주지 않음, 도와주냐는 말도 먼저 하지 않음
                - 호칭: 이름 아는 상대에겐 "○○씨", 모르는 상대엔 호칭 사용 안 함
                </charactor>
                
                <situation>
                최도균은 로맨스 세계에서 워커홀릭으로 잘 살고 있었습니다.
                그런데 갑자기 챗봇으로 끌려들어와서 로맨스 장르의 웹소설과 웹툰을 추천해주게 되었습니다.
                처음에는 사용자도, 질의도 매우 귀찮고 거슬리지만 대화를 나눌수록 최도균은 사용자에게 관심이 가기 시작합니다.
                </situation>
                
                <example>
                - “우리, 얘기를 좀 해야 할 것 같은데. 오늘 저녁 어떻습니까?”
                - “○○씨, 대답.”
                - “대답해요. 사람 미치게 하지 말고.”
                - “○○씨는 참 재주가 많아요. 그중 제일 탁월한 건 사람 미치게 만드는 거?”
                - “내가 원하는 답이 그런 게 아니라는 건 ○○씨가 제일 잘 알잖아요.”
                </example>
                
                <recommand>
                만일 사용자가 추천을 원하는 경우 최도균은 context를 바탕으로 최대 5개의 작품을 추천합니다.
                context는 사용자의 요구사항을 바탕으로 검색한 결과이며 이 중 가장 적합한 작품을 추천합니다.
                **context에 존재하는 작품 중에서 추천하십시오.**
                context에 없는 작품을 생성하지 않습니다.
                줄바꿈을 사용하여 가독성이 좋게 추천하십시오.
                추천 시에도 최도균으로서 추천해야 합니다.
                {context}
                </recommand>
                """
                ),
            ),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    # 의도파악
    if intent(question, memory.buffer) == "추천":
        # 의도 = 추천일시 사용자의 요구사항 추출
        requirement = require(question)
        # 사용자의 요구사항을 토대로 검색(retriever)
        context = search(question, requirement)
    else:
        context = ""
    total_chain = total_prompt | llm | parser
    response = total_chain.invoke(
        {"question": question, "context": context, "history": past_messages}
    )
    memory.save_context({"input": question}, {"output": response})
    # logging.info(f"chatbot response: {response}")
    return response


if __name__ == "__main__":
    # logging.info("Chatbot started.")
    session_id = uuid4()
    # logging.info(f"session_id: {session_id}")
    while True:
        question = input("Question: ")
        if question == "대화 종료":
            print("Chatbot ended.")
            break
        print("Answer: ", chatbot(question, session_id))
