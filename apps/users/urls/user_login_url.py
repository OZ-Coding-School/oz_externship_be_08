from django.urls import path

from apps.users.views.user_login_view import LoginView, LogoutView, TokenRefreshView

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("me/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
