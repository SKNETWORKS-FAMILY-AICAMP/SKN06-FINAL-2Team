from django.db import models
from django.conf import settings


# class RecommendedWork(models.Model):
#     recommended_id = models.AutoField(primary_key=True)
#     account_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     content_id = models.IntegerField()
#     recommended_model = models.CharField(max_length=50)
#     recommended_date = models.DateTimeField(auto_now_add=True, null=True)
#     feedback = models.IntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.account_user.username} - {self.content_id} ({self.recommended_model})"
