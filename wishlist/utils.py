from .models import Contents, RecommendedWork
import re
import logging


def extract_title_platform_pairs(response_text):
    """
    AI 응답에서 추천된 작품 제목과 플랫폼을 추출하는 함수.
    - response_text: AI 챗봇의 응답 (Markdown 형식 포함 가능)
    - return: 추천된 작품 제목-플랫폼 쌍 리스트
    """
    # 정규 표현식을 사용하여 제목과 플랫폼 추출
    title_pattern = r"\d+\.\s*\*\*([^*]+)\*\*"
    platform_pattern = r"\*?\*?플랫폼\*?\*?:\*?\*?\s*([가-힣]+\s?[가-힣]+)"
    type_pattern = r"\*?\*?타입\*?\*?:\*?\*?\s*([가-힣]+\s?[가-힣]+)"

    titles = re.findall(title_pattern, response_text)
    platforms = re.findall(platform_pattern, response_text)
    types = re.findall(type_pattern, response_text)

    # 제목-플랫폼 쌍으로 묶기
    title_platform_pairs = list(zip(titles, platforms, types))
    logging.info(f"title_platform_pairs: {title_platform_pairs}")
    return title_platform_pairs


def save_recommended_works(user, title_platform_pairs, model_name):
    """
    추천된 작품을 추천 기록 테이블에 중복 없이 저장하는 함수 (ORM 사용)
    :param user: 추천을 받은 사용자
    :param title_platform_pairs: 추천된 작품 제목-플랫폼-타입 쌍 리스트
    :param model_name: 추천 모델명 (romance, fantasy 등)
    """
    if not title_platform_pairs:
        logging.info("추천된 작품 정보 없음")
        return

    # 🔹 해당 제목, 플랫폼, 타입의 콘텐츠 ID 조회
    content_objects = Contents.objects.filter(
        title__in=[pair[0] for pair in title_platform_pairs],  # title 리스트
        platform__in=[pair[1] for pair in title_platform_pairs],  # platform 리스트
        type__in=[pair[2] for pair in title_platform_pairs],  # type 리스트
    ).values("id")

    content_ids = [content["id"] for content in content_objects]
    logging.info(f"추천된 콘텐츠 ID 목록: {content_ids}")

    # 🔹 이미 존재하는 추천 데이터 조회
    existing_recommendations = set(
        RecommendedWork.objects.filter(
            account_user=user,
            content_id__in=content_ids,
            recommended_model=model_name,
        ).values_list("content_id", flat=True)
    )

    # 🔹 새로운 추천 데이터만 추가
    new_recommendations = [
        RecommendedWork(
            account_user=user, content_id=content_id, recommended_model=model_name
        )
        for content_id in content_ids
        if content_id not in existing_recommendations
    ]

    if new_recommendations:
        RecommendedWork.objects.bulk_create(new_recommendations)
        logging.info(f"새로운 {len(new_recommendations)}개의 추천 데이터 저장 완료")
    else:
        logging.info("새롭게 추가할 추천 데이터 없음")
