from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from textwrap import dedent
import logging
from .vector_store import (
    selfquery_tool,
    action_vector_store,
    action_metadata_field_info,
    cartoon_vector_store,
    cartoon_metadata_field_info,
    drama_vector_store,
    drama_metadata_field_info,
    fantasy_vector_store,
    fantasy_metadata_field_info,
    historical_vector_store,
    historical_metadata_field_info,
    horror_vector_store,
    horror_metadata_field_info,
    rofan_vector_store,
    rofan_metadata_field_info,
    romance_vector_store,
    romance_metadata_field_info,
)
import json
from account.models import Preset
from wishlist.models import RecommendedWork, Contents

logging.basicConfig(level=logging.INFO)

# LLM 설정
MODEL_NAME = "gpt-4o"
llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0)

# 사용자별 메모리 저장
user_memory_dict = {}


def get_user_memory(session_id):
    if session_id not in user_memory_dict:
        user_memory_dict[session_id] = ChatMessageHistory()
    return user_memory_dict[session_id]


# Tool 설정
action_tool = selfquery_tool(action_vector_store, action_metadata_field_info, "action")
cartoon_tool = selfquery_tool(
    cartoon_vector_store, cartoon_metadata_field_info, "cartoon"
)
drama_tool = selfquery_tool(drama_vector_store, drama_metadata_field_info, "drama")
fantasy_tool = selfquery_tool(
    fantasy_vector_store, fantasy_metadata_field_info, "fantasy"
)
historical_tool = selfquery_tool(
    historical_vector_store, historical_metadata_field_info, "historical"
)
horror_tool = selfquery_tool(horror_vector_store, horror_metadata_field_info, "horror")
rofan_tool = selfquery_tool(rofan_vector_store, rofan_metadata_field_info, "rofan")
romance_tool = selfquery_tool(
    romance_vector_store, romance_metadata_field_info, "romance"
)


# **1. 사용자의 의도를 분석하는 프롬프트**
query_intent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            dedent(
                """
        <role>
        사용자의 질문을 보고 추천을 원하는지, 특정한 질문을 하는지, 아니면 일반 대화인지 판단하십시오.
        또한 사용자가 언급한 장르를 분석하여 적절한 장르를 분류하십시오.
        </role>

        <output_format>
        {{"query_intent": 추천 (recommend), 질문 (question), 기타 (other) 중 하나
        "genre": 사용자가 원하는 장르}}
        </output_format>
    """
            ),
        ),
        ("human", "{input}"),
    ]
)


def process_basic_chatbot_request(question, session_id, user):
    user_info = f"사용자의 이름은 '{user.name[-2:]}'이고, {user.real_age}세 {user.gender}입니다."
    # 유저의 취향(persona_type) 불러오기
    try:
        preset = Preset.objects.get(account_id=user)
        user_preference = preset.persona_type
    except Preset.DoesNotExist:
        user_preference = "사용자의 취향 정보가 등록되지 않았습니다."
    # 유저의 추천작 리스트 불러오기
    try:
        recommended_works = RecommendedWork.objects.filter(
            account_user=user, recommended_model="basic"
        ).values_list("content_id", flat=True)

        user_recommended_works = Contents.objects.filter(
            id__in=recommended_works
        ).values_list("title", flat=True)

    except RecommendedWork.DoesNotExist:
        user_recommended_works = ["사용자의 추천 작품 정보가 등록되지 않았습니다."]
    logging.info(f"유저정보: {user_info}")
    logging.info(f"유저 취향 정보: {user_preference}")
    logging.info(f"유저의 기존 추천작 정보: {user_recommended_works}")

    # **2. 최도균의 응답을 생성하는 프롬프트**
    total_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                dedent(
                    """
        <role>
        사용자의 질문에 대답하거나 웹툰,웹소설 작품을 추천하는 역할을 합니다.
        </role>

        <intent_handling>
        - query_intent이 "recommend"라면 사용자의 요구사항에 맞게 작품을 추천하십시오.
        - query_intent이 "question"이라면, 질문에 적절한 답변을 제공하십시오.
        - query_intent이 "other"라면 일반적인 대화를 진행하십시오.
        </intent_handling>

        <genre_handling>
        - 반드시 원하는 장르에 맞게 추천하세요.
        </genre_handling>
    """
                ),
            ),
            (
                "ai",
                dedent(
                    f"""
        <user_information>
        {user_info}
        사용자의 이름을 인식하고 부르십시오.
        사용자의 나이에 맞는 연령제한으로 추천하십시오.
            - 전체 이용가: 모든 나이 가능
            - 12세 이용가: 12세 이상
            - 15세 이용가: 15세 이상
            - 19세 이용가: 19세 이상
        </user_information>
        
        <user_preference>
        {user_preference}
        </user_preference>
        
        <user_recommended_works>
        다음은 유저가 추천받은 작품들입니다. 이 작품은 제외하고 추천하십시오.
        {user_recommended_works}
        </user_recommended_works>
        <example>
        - “OO씨, 대답.”
        - “내가 원하는 답이 그런 게 아니라는 건 OO씨가 제일 잘 알잖아요.”
        </example>
        <recommendation>
        **추천작품 형식**
        - 줄바꿈을 사용하여 가독성 좋게 추천하십시오.
        - 상세 정보는 tools에서 검색한 결과의 메타데이터에 있습니다.

        1. 제목
            - 타입
            - 플랫폼
            - 장르
            - 작가
            - 가격
            - 작품 소개: page_content를 조합하여 1~2줄 내외의 간단한 소개
            - 썸네일
            - URL

        - 위 요소를 활용해서 목록화하십시오
            - 제목, 플랫폼, 작품 소개, 썸네일, URL : 필수
            - 나머지 요소는 사용자의 요구사항에 해당되는 요소를 사용하십시오.
        - 추천하는 순서는 인기도가 높은 순서대로 추천하십시오.
        </recommendation>
    """
                ),
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # 1. 사용자의 의도 분석
    intent_response = llm.invoke(query_intent_prompt.format(input=question))

    # content를 추출
    intent_text = intent_response.content  # AIMessage의 content를 추출
    try:
        intent_data = json.loads(intent_text)  # JSON 변환
    except json.JSONDecodeError:
        # LLM이 JSON이 아닌 일반 텍스트를 반환했을 경우 기본값 설정
        intent_data = {"query_intent": "other", "genre": "모두"}

    query_intent = intent_data.get("query_intent", "other")  # 기본값: "other"
    genre = intent_data.get("genre", "모두")  # 기본값: 로맨스

    # 2. 최도균 응답 생성
    tools = [
        action_tool,
        cartoon_tool,
        drama_tool,
        fantasy_tool,
        historical_tool,
        horror_tool,
        rofan_tool,
        romance_tool,
    ]
    agent = create_tool_calling_agent(llm, tools, total_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_user_memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    response = agent_with_chat_history.stream(
        {"input": question, "query_intent": query_intent, "genre": genre},
        config={"configurable": {"session_id": session_id}},
    )

    return response
