from django.urls import include, path

app_name = "users"

urlpatterns = [
    path("", include("apps.users.urls.auth_email_url")),
    path("", include("apps.users.urls.social_url")),
    # withdrawal_urls를 enrollment_url보다 먼저 include:
    # WithdrawalView(UserInfoView 상속)가 'me' 경로를 우선 매칭하여
    # GET/PATCH/DELETE 모두 처리. enrollment_url의 UserInfoView는 도달하지 않음.
    path("", include("apps.users.urls.withdrawal_urls")),
    path("", include("apps.users.urls.profile_image_urls")),
    path("", include("apps.users.urls.auth_sms_url")),
    path("", include("apps.users.urls.user_signup_url")),
    path("", include("apps.users.urls.user_login_url")),
]
