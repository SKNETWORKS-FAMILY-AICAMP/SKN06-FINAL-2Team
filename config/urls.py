from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings
from django.http import HttpResponse


urlpatterns = [
    # path(
    #     "", TemplateView.as_view(template_name="framework/homepage.html"), name="home"
    # ),
    # path("account/", include("account.urls")),
    # path("chatbot/", include("chatbot.urls")),
    # path("wishlist/", include("wishlist.urls")),
]
