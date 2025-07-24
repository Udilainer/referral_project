import time
from typing import Any, Dict, cast

from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token

from .serializers import (
    PhoneNumberSerializer,
    VerifyCodeSerializer,
    UserSerializer,
    UserProfileSerializer,
    ActivateInviteCodeSerializer,
)
from .utils import (
    generate_auth_code,
    cache_auth_code,
    verify_auth_code,
    generate_invite_code,
)

User = get_user_model()


class RequestAuthCodeView(APIView):
    """Send (simulate) a 4-digit code to the given phone number."""
    permission_classes: list = []

    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = cast(Dict[str, Any], serializer.validated_data)
        phone_number = data["phone_number"]

        code = generate_auth_code()
        cache_auth_code(phone_number, code)

        time.sleep(1.5)

        return Response(
            {
                "success": True,
                "message": "Verification code sent to your phone number.",
                "dev_code": code,          # <-- remove in production
            },
            status=status.HTTP_200_OK,
        )


class VerifyAuthCodeView(APIView):
    """Verify the code and return (or create) a user + token."""
    permission_classes: list = []

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = cast(Dict[str, Any], serializer.validated_data)
        phone_number = data["phone_number"]
        code = data["code"]

        if not verify_auth_code(phone_number, code):
            return Response(
                {"error": "Invalid or expired verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(phone_number=phone_number)

        if created:
            invite_code = generate_invite_code()
            while User.objects.filter(invite_code=invite_code).exists():
                invite_code = generate_invite_code()
            setattr(user, "invite_code", invite_code)
            user.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    """Retrieve or update the authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserProfileSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ActivateInviteCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invite_code = cast(Dict[str, Any], serializer.validated_data)["invite_code"]
        user = request.user

        if getattr(user, "activated_invite_code", None):
            return Response(
                {"error": "You have already activated an invite code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            referrer = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid invite code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if referrer.pk == user.pk:
            return Response(
                {"error": "You cannot use your own invite code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.activated_invite_code = referrer
        user.save()

        return Response(
            {
                "message": "Invite code activated successfully.",
                "profile": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
