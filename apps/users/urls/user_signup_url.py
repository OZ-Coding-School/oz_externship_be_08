from django.urls import path

from apps.users.views.user_signup_view import SignupView

urlpatterns = [
    path("signup", SignupView.as_view(), name="signup"),
]
