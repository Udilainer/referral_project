from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneNumberSerializer(serializers.Serializer):
    """Serializer for phone number input validation."""
    phone_number = serializers.CharField(
        max_length=15,
        min_length=10,
        required=True,
        help_text="Phone number for authentication"
    )

    def validate_phone_number(self, value):
        """Validate phone number format."""
        cleaned = value.replace(" ", "").replace("-", "")

        if not (
            cleaned.isdigit() or
            (cleaned.startswith('+') and cleaned[1:].isdigit())
        ):
            raise serializers.ValidationError(
                "Phone number must contain only digits and optional + prefix"
            )

        return value


class VerifyCodeSerializer(serializers.Serializer):
    """Serializer for code verification."""
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        help_text="Phone number used for authentication"
    )
    code = serializers.CharField(
        max_length=4,
        min_length=4,
        required=True,
        help_text="4-digit verification code"
    )

    def validate_code(self, value):
        """Ensure code is 4 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Basic user data serializer."""
    activated_invite_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'invite_code', 'activated_invite_code']
        read_only_fields = ['id', 'invite_code']

    def get_activated_invite_code(self, obj):
        """Return the phone number of the user whose invite code was activated."""
        if obj.activated_invite_code:
            return obj.activated_invite_code.phone_number
        return None


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for showing referred users."""
    class Meta:
        model = User
        fields = ['phone_number']
        read_only_fields = ['phone_number']


class UserProfileSerializer(UserSerializer):
    """Extended user profile serializer with referrals."""
    referrals = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['referrals']

    def get_referrals(self, obj):
        """Get list of users who activated this user's invite code."""
        referrals = User.objects.filter(activated_invite_code=obj)
        return ReferralSerializer(referrals, many=True).data


class ActivateInviteCodeSerializer(serializers.Serializer):
    """Serializer for invite code activation."""
    invite_code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6-character invite code to activate"
    )

    def validate_invite_code(self, value):
        """Validate invite code format and existence."""

        if not value.isalnum() or not value.isupper():
            raise serializers.ValidationError(
                "Invite code must contain only uppercase letters and digits"
            )

        if not User.objects.filter(invite_code=value).exists():
            raise serializers.ValidationError("Invalid invite code")

        return value
