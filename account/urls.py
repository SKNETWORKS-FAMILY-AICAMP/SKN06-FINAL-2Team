from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('detail/', views.user_detail, name='detail'),
    path('update/', views.user_update, name='update'),
    path('delete/', views.user_delete, name='delete'),
]

