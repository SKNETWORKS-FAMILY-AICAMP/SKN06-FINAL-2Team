from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('detail/', views.user_detail, name='detail'),
    path('update/', views.user_update, name='update'),
    path('delete/', views.user_delete, name='delete'),
    path("", TemplateView.as_view(template_name="signup.html"), name="home"),  # account/ 요청 시 실행할 뷰 함수
]

