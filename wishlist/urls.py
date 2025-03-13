from django.urls import path
from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.wishlist_total_view, name="main"),
    path("update/", views.feedback_update_view, name="feedback_update"),
    path("user_preference/", views.analyze_and_store_user_preferences, name="user_preference"),
]

