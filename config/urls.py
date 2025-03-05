from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings
from django.http import HttpResponse



# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path('account/', include('account.urls')),

# ]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path("", TemplateView.as_view(template_name="account/signup.html"), name="signup"),

]

