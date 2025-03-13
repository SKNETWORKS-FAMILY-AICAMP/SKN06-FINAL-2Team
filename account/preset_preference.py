import logging
import openai
from django.db import connection
from django.conf import settings

# OpenAI API 키 설정
openai.api_key = settings.OPENAI_API_KEY  # 환경변수에 저장된 API 키 사용

logger = logging.getLogger(__name__)

def analyze_user_preference(selected_work_ids):
    """
    사용자가 선택한 작품들의 정보를 분석하여 'persona_type'을 생성
    """

    # 선택된 작품들의 상세 정보 가져오기
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT title, type, platform, genre, keywords, synopsis 
            FROM preset_preference_contents 
            WHERE id IN %s
        """, [tuple(selected_work_ids)])
        
        selected_works = cursor.fetchall()

    if not selected_works:
        logger.warning("선택된 작품이 없습니다.")
        return "반드시 2개 이상 선택해주세요."

    # 프롬프트 생성
    prompt_text = """
    다음은 사용자가 선택한 작품들입니다. 사용자가 어떤 타입(웹툰/웹소설), 플랫폼, 장르, 키워드를 선호할지 분석하세요.
    키워드를 분석할 때는 단순히 keywords가 아니라 synopsis를 이해하고 어떤 내용을 선호할지 복합적으로 분석해 도출해내세요.
    단순히 사용자가 선택한 작품의 정보를 합치는 것에서 벗어나 분석하세요.
    """
    for work in selected_works:
        title, work_type, platform, genre, keywords, synopsis = work
        prompt_text += f"- 제목: {title}, 타입: {work_type}, 플랫폼: {platform}, 장르: {genre}, 키워드: {keywords}, 스토리: {synopsis}"

    prompt_text += "이 정보를 바탕으로 사용자의 선호 타입(웹툰/웹소설), 플랫폼(카카오페이지/네이버...), 장르, 키워드등을 한 문장으로 요약해주세요."

    # OpenAI API 호출
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "너는 회원의 선호 작품을 토대로 다음 선택 작품을 맞춰야하는 마케팅 전문가야."},
                {"role": "user", "content": prompt_text}]
    )

    # 응답 처리
    try:
        ai_response = response.choices[0].message.content
        return ai_response  
    except Exception as e:
        logger.error(f"OpenAI API 오류: {e}")
        return None
