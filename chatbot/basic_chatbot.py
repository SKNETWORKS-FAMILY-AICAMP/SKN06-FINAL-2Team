from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from textwrap import dedent
import logging
from .vector_store import selfquery_tool
import json


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
romance_tool = selfquery_tool("로맨스", "romance")
bl_tool = selfquery_tool("BL", "bl")
rofan_tool = selfquery_tool("로판, 로맨스 판타지", "rofan")
drama_tool = selfquery_tool("드라마, 라이트노벨", "drama")
historical_tool = selfquery_tool("무협/사극, 무협, 액션/무협", "historical")
cartoon_tool = selfquery_tool("코믹/일상, 일상, 개그, 감성", "cartoon")
horror_tool = selfquery_tool("공포/스릴러, 스릴러, 미스터리", "horror")
action_tool = selfquery_tool("액션, 스포츠", "action")
fantasy_tool = selfquery_tool(
    "판타지 드라마, 판타지, 현판, 학원/판타지", "fantasy"
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
                """
        <example>
        - “OO씨, 대답.”
        - “내가 원하는 답이 그런 게 아니라는 건 OO씨가 제일 잘 알잖아요.”
        </example>
    """
            ),
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


def process_basic_chatbot_request(question, session_id, user):
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
        romance_tool,
        rofan_tool,
        drama_tool,
        historical_tool,
        cartoon_tool,
        horror_tool,
        action_tool,
        fantasy_tool,
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
