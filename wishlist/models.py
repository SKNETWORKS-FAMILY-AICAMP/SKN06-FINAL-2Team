from django.db import models
from django.conf import settings


from django.db import models


class Contents(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="콘텐츠 ID")
    type = models.CharField(
        max_length=20,
        choices=[("웹툰", "웹툰"), ("웹소설", "웹소설")],
        verbose_name="타입",
    )
    platform = models.CharField(
        max_length=50,
        choices=[
            ("네이버웹툰", "네이버웹툰"),
            ("네이버시리즈", "네이버시리즈"),
            ("카카오웹툰", "카카오웹툰"),
            ("카카오페이지", "카카오페이지"),
        ],
        verbose_name="플랫폼",
    )
    title = models.CharField(max_length=255, verbose_name="제목")
    status = models.CharField(
        max_length=20,
        choices=[("연재", "연재"), ("완결", "완결"), ("휴재", "휴재")],
        verbose_name="연재 상태",
    )
    update_days = models.CharField(
        max_length=37, null=True, blank=True, verbose_name="연재 요일"
    )
    thumbnail = models.URLField(verbose_name="썸네일 URL")
    genre = models.CharField(max_length=50, verbose_name="장르")
    views = models.BigIntegerField(null=True, blank=True, verbose_name="조회수")
    rating = models.FloatField(null=True, blank=True, verbose_name="평점")
    likes = models.BigIntegerField(null=True, blank=True, verbose_name="좋아요 수")
    synopsis = models.TextField(verbose_name="작품 소개")
    keywords = models.TextField(verbose_name="키워드")
    author = models.CharField(
        max_length=255, verbose_name="작가", null=True, blank=True
    )
    illustrator = models.CharField(
        max_length=255, verbose_name="일러스트레이터", null=True, blank=True
    )
    original = models.CharField(
        max_length=255, verbose_name="원작 제목", null=True, blank=True
    )
    age_rating = models.CharField(max_length=20, verbose_name="연령 등급")
    price = models.CharField(max_length=50, verbose_name="가격", null=True, blank=True)
    url = models.URLField(verbose_name="작품 URL")
    episode = models.IntegerField(null=True, blank=True, verbose_name="총 회차")
    comments = models.IntegerField(null=True, blank=True, verbose_name="댓글 수")
    recent_comments_count = models.IntegerField(
        null=True, blank=True, verbose_name="최근 댓글 수"
    )
    first_episode = models.DateField(null=True, blank=True, verbose_name="첫 연재일")
    score = models.FloatField(null=True, blank=True, verbose_name="인기도")


class RecommendedWork(models.Model):
    recommended_id = models.AutoField(primary_key=True)
    account_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_id = models.BigIntegerField()
    recommended_model = models.CharField(max_length=50)
    recommended_date = models.DateTimeField(auto_now_add=True, null=True)
    feedback = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.account_user.username} - {self.content_id} ({self.recommended_model})"


class UserPreference(models.Model):
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    basic_preference = models.TextField(null=True, blank=True)
    romance_preference = models.TextField(null=True, blank=True)
    rofan_preference = models.TextField(null=True, blank=True)
    fantasy_preference = models.TextField(null=True, blank=True)
    historical_preference = models.TextField(null=True, blank=True)
