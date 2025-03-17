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
from .utils import (
    get_user_memory,
)

logging.basicConfig(level=logging.INFO)

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

    # 프롬프트
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
            - 전체 이용가: 모든 나이 가능
        </user_information>
        
        
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
            - 제목, 타입, 플x랫폼, 작품 소개, 썸네일, URL : 필수
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
