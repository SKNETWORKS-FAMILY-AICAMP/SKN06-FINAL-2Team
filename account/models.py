from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# User 모델
class User(AbstractUser):

    name = models.CharField(
        verbose_name="이름",
        max_length=30,
        null=False  
    )
    username = models.CharField(
        verbose_name="닉네임",
        max_length=30,
        null=False,
        unique=True  
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
    real_age= models.IntegerField(
        verbose_name="만 나이",
        blank=True
    ) 
    gender = models.CharField(
        verbose_name="성별",
        max_length=30,  
        null=False
    )

    def calculate_age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def save(self, *args, **kwargs):
        self.real_age = self.calculate_age()  
        super().save(*args, **kwargs)



