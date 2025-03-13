from django.db import connection
from .models import RecommendedWork
import re
import logging


def extract_title_platform_pairs(response_text):
    """
    AI 응답에서 추천된 작품 제목과 플랫폼을 추출하는 함수.
    - response_text: AI 챗봇의 응답 (Markdown 형식 포함 가능)
    - return: 추천된 작품 제목-플랫폼 쌍 리스트
    """
    # 정규 표현식을 사용하여 제목과 플랫폼 추출
    title_pattern = r"\d+\.\s*\*\*([^*]+)\*\*"  # "1. **제목**" 형식의 작품명 추출
    platform_pattern = (
        r"\*?\*?플랫폼\*?\*?:\*?\*?\s*([가-힣]+\s?[가-힣]+)"  # 플랫폼 추출
    )

    titles = re.findall(title_pattern, response_text)
    platforms = re.findall(platform_pattern, response_text)

    # 제목-플랫폼 쌍으로 묶기
    title_platform_pairs = list(zip(titles, platforms))
    logging.info(f"title_platform_pairs: {title_platform_pairs}")
    return title_platform_pairs


def save_recommended_works(user, title_platform_pairs, model_name):
    """
    추천된 작품을 추천 기록 테이블에 저장하는 함수
    :param user: 추천을 받은 사용자
    :param title_platform_pairs: 추천된 작품 제목-플랫폼 쌍 리스트
    :param model_name: 추천 모델명 (romance, fantasy 등)
    """
    if not title_platform_pairs:
        logging.info("추천된 작품 정보 없음")
        return

    with connection.cursor() as cursor:
        # 추천된 작품 ID 가져오기
        conditions = " OR ".join(
            f"(title = %s AND platform = %s)"
            for title, platform in title_platform_pairs
        )
        query = f"SELECT id FROM contents WHERE {conditions}"
        params = [param for pair in title_platform_pairs for param in pair]
        cursor.execute(query, params)

        results = cursor.fetchall()
        logging.info(f"results: {results}")

        # 추천 데이터 저장
        for content_id in results:
            RecommendedWork.objects.create(
                account_user=user,
                content_id=content_id[0],
                recommended_model=model_name,
            )
            logging.info(f"content_id: {content_id[0]} 저장완료")
    logging.info("추천 데이터 저장 완료")
