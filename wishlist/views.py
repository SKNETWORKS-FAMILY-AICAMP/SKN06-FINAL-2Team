# import openai
# import logging
# from django.db import connection
# from django.utils.timezone import now
# from datetime import timedelta
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseBadRequest
# from .models import RecommendedWork

# logger = logging.getLogger(__name__)
# openai.api_key = settings.OPENAI_API_KEY  

# @login_required
# def wishlist_total_view(request):
#     recommendations = RecommendedWork.objects.filter(
#         account_user=request.user, recommended_date__isnull=False
#     )

#     content_ids = [rec.content_id for rec in recommendations]

#     content_map = {}
#     if content_ids:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT id, title, thumbnail FROM contents WHERE id IN %s",
#                 [tuple(content_ids)],
#             )
#             for content_id, title, thumbnail in cursor.fetchall():
#                 content_map[content_id] = {"title": title, "thumbnail": thumbnail}

#     recommendation_data = [
#         {
#             "work_id": rec.recommended_id,
#             "title": content_map[rec.content_id]["title"],
#             "thumbnail": content_map[rec.content_id]["thumbnail"],
#             "feedback": rec.feedback,
#             "deleted": rec.recommended_date is None,
#         }
#         for rec in recommendations
#         if rec.content_id in content_map
#     ]

#     return render(
#         request, "wishlist/wishlist.html", {"recommendations": recommendation_data}
#     )

# @login_required
# def analyze_and_store_user_preferences(request):
#     user_id = request.user.id
#     logger.info(f"사용자 {user_id}의 선호도 분석 시작.")

#     # 최근 1년 내 추천 + feedback 존재하는 데이터만 가져오기
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT content_id, recommended_model, feedback 
#             FROM wishlist_recommendedwork 
#             WHERE account_user_id = %s 
#             AND feedback IS NOT NULL
#             AND recommended_date >= NOW() - INTERVAL 1 YEAR
#         """, [user_id])
#         recommendations = cursor.fetchall()

#     if not recommendations:
#         logger.warning(f"사용자 {user_id}의 유효한 피드백이 없습니다.")
#         return 

#     # 추천 모델별 데이터 그룹화
#     grouped_data = {model: [] for model in ["basic", "romance", "rofan", "fantasy", "historical"]}
#     content_ids = set()

#     for content_id, model, feedback in recommendations:
#         if model in grouped_data:
#             grouped_data[model].append({"content_id": content_id, "feedback": feedback})
#             content_ids.add(content_id)

#     if not content_ids:
#         logger.warning("해당 모델에 유효한 피드백이 없습니다.")
#         return 

#     # contents 테이블에서 작품 정보 가져오기
#     content_data = {}
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT id, type, platform, genre, keywords, synopsis 
#             FROM contents 
#             WHERE id IN (%s)
#         """ % ','.join(['%s'] * len(content_ids)), tuple(content_ids))

#         for row in cursor.fetchall():
#             content_data[row[0]] = {
#                 "type": row[1], "platform": row[2], "genre": row[3],
#                 "keywords": row[4], "synopsis": row[5]
#             }

#     # LLM 분석 수행 
#     model_preferences = {}
#     for model, rec_list in grouped_data.items():
#         if not rec_list:
#             logger.warning(f"사용자 {user_id}의 {model} 모델 데이터가 없습니다. 기본값으로 대체.")
#             model_preferences[model] = "분석 결과 없음"
#             continue
            
#         llm_input = []
#         for rec in rec_list:
#             if rec["content_id"] in content_data:
#                 content_info = content_data[rec["content_id"]]
#                 llm_input.append(f"제목: {content_info['type']}, 장르: {content_info['genre']}, 키워드: {content_info['keywords']}, 피드백: {rec['feedback']}/5")
#             else:
#                 llm_input.append("데이터 없음")

#         if llm_input:
#             prompt = f"""
#             이 사용자가 작품에 대해 선호하는 부분을 분석해줘:\n
#             (가이드라인)
#             1. 500자 이내로 작성하세요
#             2. 단순히 선택된 작품의 결과를 합치는 것이 아니라, 비슷한 키워드나 시놉시스의 내용을 찾아내고 심도있게 분석하세요.
#             3. 주로 선호하는 플랫폼이 있는지 없는지 확인해보세요.
#             4. 에피소드가 긴 작품만 선호하는지 확인해보세요.
#             5. 특별히 선호하지 않는 타입,장르,내용도 분석해서 도출해내세요.

#             \n
#             """ + "\n".join(llm_input)

#             try:
#                 client = openai.Client()
#                 response = client.chat.completions.create(
#                     model="gpt-4",
#                     messages=[
#                         {"role": "system", "content": "당신은 데이터분석가입니다. 데이터들을 분석하여 사용자가 다음에 선택할 작품을 예측할 수 있는데 도움이 되는 값을 만들어내세요."},
#                         {"role": "user", "content": prompt}
#                     ]
#                 )
#                 model_preferences[model] = response.choices[0].message.content  
#                 logger.info(f"LLM 응답 완료 - 모델: {model}, 결과: {model_preferences[model]}")

#             except Exception as e:
#                 logger.error(f"LLM 요청 실패: {str(e)}")
#                 model_preferences[model] = "분석되지 않음"

#     # user_preference 테이블에 저장
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             INSERT INTO user_preference (account_id, basic_preference, romance_preference, rofan_preference, fantasy_preference, historical_preferencecol)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             ON DUPLICATE KEY UPDATE
#                 basic_preference = VALUES(basic_preference),
#                 romance_preference = VALUES(romance_preference),
#                 rofan_preference = VALUES(rofan_preference),
#                 fantasy_preference = VALUES(fantasy_preference),
#                 historical_preferencecol = VALUES(historical_preferencecol)
#         """, [
#             user_id,
#             model_preferences.get("basic", ""),
#             model_preferences.get("romance", ""),
#             model_preferences.get("rofan", ""),
#             model_preferences.get("fantasy", ""),
#             model_preferences.get("historical", ""),
#         ])

#     logger.info(f"사용자 {user_id}의 선호 작품 분석 완료")
#     return JsonResponse({"message": "사용자 선호 분석이 완료되었습니다."})

# @login_required
# def feedback_update_view(request):
#     if request.method == "POST":
#         user = request.user

#         recommended_works = RecommendedWork.objects.filter(account_user=user)
#         update_count = 0  

#         for work in recommended_works:
#             feedback_key = f"rating_{work.recommended_id}"
#             delete_key = f"delete_{work.recommended_id}"

#             feedback_value = request.POST.get(feedback_key, None)
#             delete_value = request.POST.get(delete_key, None)

#             logger.info(f"작품 {work.recommended_id} - 받은 별점: {feedback_value}, 삭제 여부: {delete_value}")

#             if feedback_value is not None:
#                 work.feedback = feedback_value
#                 update_count += 1

#             if delete_value is not None:
#                 work.recommended_date = None
#                 update_count += 1

#             work.save()

#         logger.info(f"총 {update_count}개 항목 업데이트 완료.")

#         # 별점 저장 후 LLM 분석 실행
#         logger.info("LLM 분석 실행 시작")
#         analyze_and_store_user_preferences(request)  
#         logger.info("LLM 분석 실행 완료")

#         return redirect("wishlist:main")

#     else:
#         logger.warning("잘못된 요청: POST가 아님")
#         return HttpResponseBadRequest("잘못된 요청입니다.")
