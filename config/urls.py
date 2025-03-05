from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings


urlpatterns = [
    path('account/', include('account.urls')),

]

