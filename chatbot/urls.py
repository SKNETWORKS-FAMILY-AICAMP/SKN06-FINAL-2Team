from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("basic_chatbot_na/", views.basic_chatbot_na_view, name="basic_chatbot_na"),
    path("basic_chatbot/", views.basic_chatbot_view, name="basic_chatbot"),
    path("romance_chatbot/", views.romance_chatbot_view, name="romance_chatbot"),
    path("rofan_chatbot/", views.rofan_chatbot_view, name="rofan_chatbot"),
    path("fantasy_chatbot/", views.fantasy_chatbot_view, name="fantasy_chatbot"),
    path(
        "historical_chatbot/", views.historical_chatbot_view, name="historical_chatbot"
    ),
]
