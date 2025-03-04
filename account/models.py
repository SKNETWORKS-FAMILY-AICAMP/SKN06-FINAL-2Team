from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# User 모델
class User(AbstractUser):
    # Field 정의 - table 컬럼
    name = models.CharField(
        verbose_name="이름",
        max_length=30,
        null=False  
    )
    username = models.CharField(
        verbose_name="닉네임",
        max_length=30,
        null=False  
    )
    email = models.CharField(
        verbose_name="이메일",
        max_length=50,
        null=False  
    )
    birthday = models.DateField(
        verbose_name="생년월일",
        null=False
    )
    gender = models.CharField(
        verbose_name="성별",
        max_length=30,  
        null=False
    )

    def real_age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __str__(self):
        return f"이름: {self.name}, 나이:만 {self.real_age()}세, 성별:{self.gender}"
