import openai
import logging
from django.db import connection
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from .models import RecommendedWork

logger = logging.getLogger(__name__)
openai.api_key = settings.OPENAI_API_KEY


@login_required
def wishlist_total_view(request):
    recommendations = RecommendedWork.objects.filter(
        account_user=request.user, recommended_date__isnull=False
    )

    content_ids = [rec.content_id for rec in recommendations]

    content_map = {}
    if content_ids:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, thumbnail FROM contents WHERE id IN %s",
                [tuple(content_ids)],
            )
            for content_id, title, thumbnail in cursor.fetchall():
                content_map[content_id] = {"title": title, "thumbnail": thumbnail}

    recommendation_data = [
        {
            "work_id": rec.recommended_id,
            "title": content_map[rec.content_id]["title"],
            "thumbnail": content_map[rec.content_id]["thumbnail"],
            "feedback": rec.feedback,
            "deleted": rec.recommended_date is None,
        }
        for rec in recommendations
        if rec.content_id in content_map
    ]

    return render(
        request, "wishlist/wishlist.html", {"recommendations": recommendation_data}
    )


from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import logging
import openai
from .models import RecommendedWork, UserPreference

logger = logging.getLogger(__name__)


@login_required
def analyze_and_store_user_preferences(request):
    user = request.user
    user_id = user.id
    logger.info(f"사용자 {user_id}의 선호도 분석 시작.")

    # 최근 1년 내 추천 + feedback 존재하는 데이터만 가져오기
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT content_id, recommended_model, feedback 
            FROM wishlist_recommendedwork 
            WHERE account_user_id = %s 
            AND feedback IS NOT NULL
            AND recommended_date >= NOW() - INTERVAL 1 YEAR
        """,
            [user_id],
        )
        recommendations = cursor.fetchall()

    if not recommendations:
        logger.warning(f"사용자 {user_id}의 유효한 피드백이 없습니다.")
        return JsonResponse({"error": "유효한 피드백이 없습니다."}, status=400)

    # 추천 모델별 데이터 그룹화
    grouped_data = {
        model: [] for model in ["basic", "romance", "rofan", "fantasy", "historical"]
    }
    content_ids = set()

    for content_id, model, feedback in recommendations:
        if model in grouped_data:
            grouped_data[model].append({"content_id": content_id, "feedback": feedback})
            content_ids.add(content_id)

    if not content_ids:
        logger.warning("해당 모델에 유효한 피드백이 없습니다.")
        return JsonResponse({"error": "유효한 피드백이 없습니다."}, status=400)

    # contents 테이블에서 작품 정보 가져오기
    content_data = {}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, type, platform, genre, keywords, synopsis 
            FROM contents 
            WHERE id IN (%s)
        """
            % ",".join(["%s"] * len(content_ids)),
            tuple(content_ids),
        )

        for row in cursor.fetchall():
            content_data[row[0]] = {
                "type": row[1],
                "platform": row[2],
                "genre": row[3],
                "keywords": row[4],
                "synopsis": row[5],
            }

    # LLM 분석 수행
    model_preferences = {}
    for model, rec_list in grouped_data.items():
        if not rec_list:
            logger.warning(
                f"사용자 {user_id}의 {model} 모델 데이터가 없습니다. 기본값으로 대체."
            )
            model_preferences[model] = "분석 결과 없음"
            continue

        llm_input = []
        for rec in rec_list:
            if rec["content_id"] in content_data:
                content_info = content_data[rec["content_id"]]
                llm_input.append(
                    f"제목: {content_info['type']}, 장르: {content_info['genre']}, 키워드: {content_info['keywords']}, 피드백: {rec['feedback']}/5"
                )
            else:
                llm_input.append("데이터 없음")

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

    # UserPreference 테이블에 저장
    UserPreference.objects.update_or_create(
        account=user,
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
