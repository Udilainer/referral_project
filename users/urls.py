from django.urls import path

from .views import (
    RequestAuthCodeView,
    VerifyAuthCodeView,
    UserProfileView,
)

app_name = "users"

urlpatterns = [
    path("auth/request-code/", RequestAuthCodeView.as_view(), name="request-auth-code"),
    path("auth/verify-code/", VerifyAuthCodeView.as_view(), name="verify-auth-code"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]
