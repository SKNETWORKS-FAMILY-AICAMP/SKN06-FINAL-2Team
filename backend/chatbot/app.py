import streamlit as st
from uuid import uuid4

from romance_model import get_user_memory,search_vector_store,search_webtoon,search_webnovel,intent,require,search,chatbot  # chatbot.py에서 함수 가져오기

# Streamlit UI 설정
st.set_page_config(page_title="Pixary", page_icon="🤖")
st.title("Pixary")

# 사이드바 선택 버튼 추가
st.sidebar.title("옵션 선택")
option = st.sidebar.radio(
    "하나를 선택하세요:",
    ("기본 모델", "북부대공", "집착광공", "정파", "폭군")
)
st.sidebar.write(f"선택한 옵션: {option}")

# '집착광공'을 선택했을 때만 챗봇 활성화
if option == "집착광공":
    # 세션 ID 설정
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())

    # 대화 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 사용자와 챗봇 이미지 설정
    USER_AVATAR = "♥️"  # 사용자 아바타 (이모지 또는 이미지 URL 가능)
    BOT_AVATAR = "https://mblogthumb-phinf.pstatic.net/MjAyMjAxMTFfMTQ2/MDAxNjQxODk5MDY0ODg3.6DDSSyEo1M7peuSJWsRtiYlRQxlFoMqMwKqY1bo07y0g.t6yUZTB6yNCTWKBa511teDQAPO-RSYxV9gh85kfyepgg.PNG.animated_dreamer/sis.png?type=w800"

    # 대화 기록 표시 (과거 메시지 먼저 출력)
    for message in st.session_state.messages:
        avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # 사용자 입력 받기
    user_input = st.chat_input("메시지를 입력하세요...")
    if user_input:
        # 사용자 메시지 저장 및 출력
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(user_input)

        # 챗봇 응답 생성
        response = chatbot(user_input, st.session_state.session_id)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 챗봇 메시지 출력
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.markdown(response)

