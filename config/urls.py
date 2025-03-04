from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path("account/", include("account.urls")),
    path("basic_chatbot/", include("basic_chatbot.urls")),
    path("romance_chatbot/", include("romance_chatbot.urls")),
    path("rofan_chatbot/", include("rofan_chatbot.urls")),
    path("hero_chatbot/", include("hero_chatbot.urls")),
    path("historical_chatbot/", include("historical_chatbot.urls")),
    path("", TemplateView.as_view(template_name="basic_chatbot.html"), name="basic_chatbot"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)