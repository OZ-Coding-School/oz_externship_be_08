from django.urls import path
from apps.users.views.user import SignupView

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
]