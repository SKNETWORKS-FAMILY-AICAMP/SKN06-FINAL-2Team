import openai
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from .models import RecommendedWork, Contents, UserPreference
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.shortcuts import render

logger = logging.getLogger(__name__)
openai.api_key = settings.OPENAI_API_KEY


@login_required
def wishlist_total_view(request):
    # 현재 로그인한 사용자의 추천 목록 가져오기 (추천일이 있는 항목만)
    recommendations = (
        RecommendedWork.objects.filter(
            account_user=request.user, recommended_date__isnull=False
        )
        .select_related("account_user")
        .order_by("-recommended_date")
    )

    # 추천된 콘텐츠 ID 리스트 추출
    content_ids = recommendations.values_list("content_id", flat=True)

    # 콘텐츠 데이터 조회
    contents = Contents.objects.filter(id__in=content_ids)

    # 콘텐츠를 딕셔너리로 변환 (빠른 조회를 위해)
    content_map = {content.id: content for content in contents}

    # 최종 추천 목록 데이터 구성
    recommendation_data = [
        {
            "work_id": rec.recommended_id,
            "title": content_map[rec.content_id].title,
            "thumbnail": content_map[rec.content_id].thumbnail,
            "feedback": rec.feedback,
            "deleted": rec.recommended_date is None,
            "stars": [5, 4, 3, 2, 1],
        }
        for rec in recommendations
        if rec.content_id in content_map
    ]

    # 한 페이지당 15개씩 표시
    paginator = Paginator(recommendation_data, 15)
    page_number = request.GET.get("page")
    recommendations_paged = paginator.get_page(page_number)

    # 최대 5개의 페이지 링크만 표시하도록 페이지 범위 계산
    total_pages = paginator.num_pages
    current_page = recommendations_paged.number
    num_links = 5  # 표시할 페이지 링크 수
    half = num_links // 2

    # 현재 페이지 기준 시작 페이지와 종료 페이지 계산
    start_page = max(current_page - half, 1)
    end_page = start_page + num_links - 1
    if end_page > total_pages:
        end_page = total_pages
        start_page = max(end_page - num_links + 1, 1)
    page_range = range(start_page, end_page + 1)

    return render(
        request,
        "wishlist/wishlist.html",
        {"recommendations": recommendations_paged, "page_range": page_range},
    )



@login_required
def analyze_and_store_user_preferences(request):
    user = request.user
    user_id = user.id
    logger.info(f"사용자 {user_id}의 선호도 분석 시작.")

    one_year_ago = timezone.now() - timedelta(days=365)
    recommendations = RecommendedWork.objects.filter(
        account_user=user,
        feedback__isnull=False,
        recommended_date__gte=one_year_ago,
    ).values("content_id", "recommended_model", "feedback")

    if not recommendations.exists():
        logger.warning(f"사용자 {user_id}의 유효한 피드백이 없습니다.")
        return JsonResponse({"error": "유효한 피드백이 없습니다."}, status=400)

    grouped_data = {
        model: [] for model in ["basic", "romance", "rofan", "fantasy", "historical"]
    }
    content_ids = set()

    for rec in recommendations:
        model = rec["recommended_model"]
        if model in grouped_data:
            grouped_data[model].append(
                {"content_id": rec["content_id"], "feedback": rec["feedback"]}
            )
            content_ids.add(rec["content_id"])

    if not content_ids:
        logger.warning("해당 모델에 유효한 피드백이 없습니다.")
        return JsonResponse({"error": "유효한 피드백이 없습니다."}, status=400)

    contents = Contents.objects.filter(id__in=content_ids).values(
        "id", "type", "platform", "genre", "keywords", "synopsis"
    )

    content_data = {c["id"]: c for c in contents}

    model_preferences = {}
    for model, rec_list in grouped_data.items():
        if not rec_list:
            logger.warning(
                f"사용자 {user_id}의 {model} 모델 데이터가 없습니다. 기본값으로 대체."
            )
            model_preferences[model] = "분석 결과 없음"
            continue

        llm_input = [
            f"제목: {content_data[rec['content_id']]['type']}, 장르: {content_data[rec['content_id']]['genre']}, "
            f"키워드: {content_data[rec['content_id']]['keywords']}, 피드백: {rec['feedback']}/5"
            for rec in rec_list
            if rec["content_id"] in content_data
        ]

        if llm_input:
            prompt = f"""
            사용자의 작품 선호도를 분석해주세요:\n
            1. 500자 이내로 작성하세요.
            2. 단순한 내용 요약이 아닌, 공통점 및 특이점을 도출하세요.
            3. 주로 선호하는 플랫폼 및 장르를 파악하세요.
            4. 사용자가 좋아하지 않는 요소도 분석해주세요.
            5. 사용자의 피드백(별점)을 고려하여 평가하세요.
            \n
            """ + "\n".join(
                llm_input
            )

            try:
                client = openai.Client()
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 데이터 분석가입니다. 사용자의 작품 선호도를 분석해주세요.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                model_preferences[model] = response.choices[0].message.content
                logger.info(
                    f"LLM 응답 완료 - 모델: {model}, 결과: {model_preferences[model]}"
                )

            except Exception as e:
                logger.error(f"LLM 요청 실패: {str(e)}")
                model_preferences[model] = "분석되지 않음"

    UserPreference.objects.update_or_create(
        account_id=user_id,
        defaults={
            "basic_preference": model_preferences.get("basic", "분석 결과 없음"),
            "romance_preference": model_preferences.get("romance", "분석 결과 없음"),
            "rofan_preference": model_preferences.get("rofan", "분석 결과 없음"),
            "fantasy_preference": model_preferences.get("fantasy", "분석 결과 없음"),
            "historical_preference": model_preferences.get(
                "historical", "분석 결과 없음"
            ),
        },
    )

    logger.info(f"사용자 {user_id}의 선호 작품 분석 완료")
    return JsonResponse({"message": "사용자 선호 분석이 완료되었습니다."})


@login_required
def feedback_update_view(request):
    if request.method == "POST":
        user = request.user
        recommended_works = RecommendedWork.objects.filter(account_user=user)
        update_count = 0

        for work in recommended_works:
            feedback_key = f"rating_{work.recommended_id}"
            delete_key = f"delete_{work.recommended_id}"

            feedback_value = request.POST.get(feedback_key, None)
            delete_value = request.POST.get(delete_key, None)

            logger.info(
                f"작품 {work.recommended_id} - 받은 별점: {feedback_value}, 삭제 여부: {delete_value}"
            )

            if feedback_value is not None:
                work.feedback = feedback_value
                update_count += 1

            if delete_value is not None:
                work.recommended_date = None
                update_count += 1

            work.save()

        logger.info(f"총 {update_count}개 항목 업데이트 완료.")

        # 별점 저장 후 LLM 분석 실행
        logger.info("LLM 분석 실행 시작")
        analyze_and_store_user_preferences(request)
        logger.info("LLM 분석 실행 완료")

        return redirect("wishlist:main")

    else:
        logger.warning("잘못된 요청: POST가 아님")
        return HttpResponseBadRequest("잘못된 요청입니다.")
