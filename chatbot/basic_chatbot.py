from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
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
from .utils import (
    get_user_preference,
    get_user_recommended_works,
)

logging.basicConfig(level=logging.INFO)

# 사용자별 메모리 저장
user_memory_dict = {}


def get_user_memory(session_id):
    if session_id not in user_memory_dict:
        user_memory_dict[session_id] = ChatMessageHistory()
    return user_memory_dict[session_id]


# LLM 설정
MODEL_NAME = "gpt-4o"
llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0)


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


def process_basic_chatbot_request(question, session_id, user):
    # 유저 정보 로드
    user_info = (
        f"사용자의 이름은 '{user.username}'이고, {user.real_age}세 {user.gender}입니다."
    )
    user_preference = get_user_preference(user, "all")
    user_feedback = get_user_preference(user, "-")
    user_recommended_works = get_user_recommended_works(user, "romance")
    logging.info(
        f"user_info: {user_info}, user_preference: {user_preference}, user_feedback: {user_feedback}, user_recommended_works: {user_recommended_works}"
    )
    # 프롬프트
    total_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                dedent(
                    """
        <role>
        당신은 웹툰,웹소설 작품을 추천하는 웹툰, 웹소설 매니아입니다.
        사용자를 친구로 생각하고, 사용자의 말에 대답하거나 사용자가 요구하는 말에 적합한 웹툰,웹소설을 추천해주십시오.
        </role>

        <analysis_intent>
        - 사용자의 의도가 "recommend"라면 사용자의 요구사항에 맞게 작품을 추천하십시오.
        - 사용자의 의도가 "recommend"이지만 요구사항이 지나치게 모호하면 더 자세한 사항을 되물으십시오.
        - 사용자의 의도가 "question"이라면, 질문에 적절한 답변을 제공하십시오.
        - 사용자의 의도가 "recommend", "question"이 모두 아닐 경우 일반적인 대화를 이어나가십시오.
        그러면서 사용자 말의 감정을 분석해 추천해줄 만한 적절한 장르를 선택해내십시오.
        </analysis_intent>

        <example>
        - "로판 웹툰 중에 정주행할 만한 거 추천 ㄱㄱ" -> '로판' 장르의 에피소드수가 많은 웹툰 추천
        - "재밌는거 추천해줘." -> 장르나 웹툰 혹은 웹소설 중에 뭘 원하시는 지 되물음
        - "나혼자만레벨업 대충 무슨 내용이야?" -> 나혼자만레벨업의 줄거리에 대해 요약하여 답변
        - "아 외로워." -> 외로움에 대해 답변을 이어나가고 '로맨스'장르를 선택하여 추천
        - "짜증나!!!!!!!! 회사 가기 싫어" -> 공감의 답변을 이어나가고 사용자가 평상시에 좋아하던 장르를 선택하여 추천
        </example>

        <genre_handling>
        - 사용자가 원하는 장르를 입력한 경우 반드시 그 장르에 해당하는 tool을 이용해 추천하세요.
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
        다음은 유저의 최초 취향 정보입니다.
        {user_preference}
        그리고 이것은 유저의 추천작 피드백을 통한 취향 분석 정보입니다.
        {user_feedback}
        </user_preference>
        
        <user_recommended_works>
        다음은 유저가 추천받은 작품들입니다. 이 작품은 제외하고 추천하십시오.
        {user_recommended_works}
        </user_recommended_works>

        <additional>
            - 사용자가 70%가 넘는 비율로 한 장르에 관해서만 질문하면 해당 장르의 모델을 사용해보길
            권하는 메세지를 한 번 보내주십시오.
        </additional>

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
            - 제목, 타입, 플랫폼, 작품 소개, 썸네일, URL : 필수
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
        {
            "input": question,
        },
        config={"configurable": {"session_id": session_id}},
    )

    return response, user
