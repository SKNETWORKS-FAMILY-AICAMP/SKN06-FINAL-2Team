from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


# User 모델
class User(AbstractUser):

    name = models.CharField(verbose_name="이름", max_length=30, null=False)
    username = models.CharField(
        verbose_name="닉네임", max_length=30, null=False, unique=True
    )
    email = models.CharField(verbose_name="이메일", max_length=50, null=False)
    birthday = models.DateField(verbose_name="생년월일", null=False)
    real_age = models.IntegerField(verbose_name="만 나이", blank=True)
    gender = models.CharField(verbose_name="성별", max_length=30, null=False)

    def calculate_age(self):
        today = date.today()
        return (
            today.year
            - self.birthday.year
            - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        )

    def save(self, *args, **kwargs):
        self.real_age = self.calculate_age()
        super().save(*args, **kwargs)


class Preset(models.Model):
    mapping_id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="presets", db_column="account_id"
    )
    persona_type = models.TextField(verbose_name="사용자 취향 설명")


class PresetContents(models.Model):
    content_id = models.BigIntegerField(primary_key=True, verbose_name="콘텐츠 ID")
    title = models.CharField(max_length=255, verbose_name="제목")
    type = models.CharField(
        max_length=20,
        choices=[("웹툰", "웹툰"), ("웹소설", "웹소설")],
        verbose_name="타입",
    )
    platform = models.CharField(max_length=50, verbose_name="플랫폼")
    genre = models.CharField(max_length=50, verbose_name="장르")
    keywords = models.TextField(verbose_name="키워드")
    synopsis = models.TextField(verbose_name="시놉시스")
    thumbnail = models.URLField(verbose_name="썸네일 URL")
