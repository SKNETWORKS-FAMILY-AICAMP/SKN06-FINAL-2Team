from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('user_information/', views.user_information, name='user_information'),
    path('edit_information/', views.edit_information, name='edit_information'),
    path('edit_pwd/', views.edit_pwd, name='edit_pwd'),
    path('delete/', views.user_delete, name='delete'),
    path('preset_preference/',views.preset_preference,name='preset_preference')
]

