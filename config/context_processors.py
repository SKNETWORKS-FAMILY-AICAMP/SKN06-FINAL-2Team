from wishlist.models import RecommendedWork, Contents


def recommended_works_context(request):
    """
    최근 15개의 추천된 작품을 wishlist_contents에서 찾아서 제공
    """
    if request.user.is_authenticated:
        recommended_works = RecommendedWork.objects.filter(
            account_user=request.user
        ).order_by("-recommended_date")[:15]

        # recommended_works에서 content_id만 가져오기
        content_ids = [work.content_id for work in recommended_works]

        # content_ids에 해당하는 콘텐츠 정보를 wishlist_contents에서 가져오기
        contents = Contents.objects.filter(id__in=content_ids).values(
            "id", "title", "thumbnail", "url", "keywords"
        )

        recommendations = list(contents)  # QuerySet을 리스트로 변환

    else:
        recommendations = []

    return {"recommendations": recommendations}  # ✅ 모든 템플릿에서 사용 가능
