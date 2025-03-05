from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings


urlpatterns = [
    path('account/', include('account.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)