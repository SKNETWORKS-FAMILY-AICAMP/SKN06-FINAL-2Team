import logging
import markdown2
import time
from wishlist.utils import extract_title_platform_pairs, save_recommended_works
from account.models import Preset
from wishlist.models import RecommendedWork, Contents, UserPreference


def get_user_preset(user, model_type):
    """사용자의 모델 타입에 맞는 선호도를 가져오는 함수"""
    try:
        preset = Preset.objects.get(account=user, model_type=model_type)
        return preset
    except Preset.DoesNotExist:
        return f"사용자의 {model_type} 취향 정보가 등록되지 않았습니다."


def get_user_preference(user, model_type):
    """사용자의 모델 타입에 맞는 선호도를 가져오는 함수"""
    preference_field = f"{model_type}_preference"

    try:
        user_pref = UserPreference.objects.get(account=user)
        preference = getattr(user_pref, preference_field, None)  # 필드값 가져오기
        return (
            preference
            if preference
            else f"사용자의 {model_type} 취향 정보가 등록되지 않았습니다."
        )
    except UserPreference.DoesNotExist:
        return f"사용자의 {model_type} 취향 정보가 등록되지 않았습니다."


def get_user_recommended_works(user, model_type):
    try:
        recommended_works = RecommendedWork.objects.filter(
            account_user=user, recommended_model=model_type
        ).values_list("content_id", flat=True)

        user_recommended_works = Contents.objects.filter(
            id__in=recommended_works
        ).values_list("title", flat=True)

        return user_recommended_works
    except RecommendedWork.DoesNotExist:
        return "사용자의 추천 작품 정보가 등록되지 않았습니다."


def process_chatbot_request(chatbotrequest, model_name):
    """LangChain 스트리밍 응답을 최적화하는 함수 (Tool 실행 단계 감지)"""
    response, user = chatbotrequest
    tool_message = 0
    search_message = 0
    for step in response:
        logging.info(step)
        if "output" in step.keys():
            clean_message = step["output"]
            recommended_titles = extract_title_platform_pairs(clean_message)
            if recommended_titles:
                logging.info(recommended_titles)
                save_recommended_works(user, recommended_titles, model_name)
            yield {"message": clean_message}
        elif "messages" in step.keys():
            if isinstance(step["messages"], list):
                message = step["messages"][0]
                if not (
                    message.content.startswith("컨텐츠_타입")
                    or message.content.startswith("컨텐츠타입")
                    or message.content == ""
                ):
                    clean_message = message.content
                    yield {"message": clean_message}
                elif message.content == "":
                    if tool_message == 0:
                        model_messages = {
                            "basic": "지금 검색 중입니다. 잠시만 기다려 주세요!😊 필요한 정보를 찾고 있어요!",
                            "romance": "잠시만 기다려요. 내가 원하는 정보를 찾고 있으니까.",
                            "rofan": "영애, 잠시만 기다려 주십시오. 북부의 눈보라 속에서도 찾을 수 있는 보석 같은 이야기를 찾아보겠습니다.",
                            "fantasy": "잠시만 기다려줘! 신비로운 숲 속에서 마법의 책을 펼쳐서 멋진 판타지 작품을 찾아볼게. 곧 돌아올 테니 조금만 기다려줘!",
                            "historical": "잠시 기다려 주시오. 강호의 깊은 곳에서 그대에게 맞는 이야기를 찾고 있소. 곧 돌아오겠소.",
                        }
                        clean_message = model_messages[model_name]
                        tool_message += 1
                        yield {"message": clean_message}
                else:
                    if search_message == 0:
                        model_messages = {
                            "basic": "검색이 완료되었고, 이제 답변을 정리하고 있습니다. 곧 결과를 알려드릴게요!",
                            "romance": "하... 필요한 정보를 정리하고 있으니까 기다려요.",
                            "rofan": "이제 곧 당신께 어울리는 이야기를 정리하여 드리겠습니다. 잠시만 더 기다려 주십시오. 북부의 차가운 바람 속에서도 따뜻한 이야기를 찾고 있으니 말입니다.",
                            "fantasy": "마법의 책에서 멋진 이야기를 찾았어! 이제 그 이야기를 정리해서 곧바로 들려줄게. 조금만 기다려줘, 기대해도 좋아!",
                            "historical": "이제 곧 그대에게 어울리는 이야기를 전해드릴 준비가 되었소. 잠시만 더 기다려 주시오. 곧 강호의 비밀을 풀어드리겠소.",
                        }
                        clean_message = model_messages[model_name]
                        search_message += 1
                        yield {"message": clean_message}


def event_stream(chatbotrequest, model_name):
    response = process_chatbot_request(chatbotrequest, model_name)
    """AI 응답을 스트리밍 방식으로 마크다운을 HTML로 변환하여 전송"""
    try:
        for message in response:
            message["message"] = message["message"].replace("\n", "<br>")

            markdown_text = markdown2.markdown(message["message"])
            yield f"data: {markdown_text}\n\n"
            time.sleep(0.2)
        yield "data: [DONE]\n\n"
    except GeneratorExit:
        logging.info("🔌 클라이언트 연결이 끊어졌습니다.")
    except Exception as e:
        logging.error(f"🚨 스트리밍 오류 발생: {e}")
