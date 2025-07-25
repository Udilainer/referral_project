from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from typing import TypeVar

UserType = TypeVar("UserType", bound="User")


class UserManager(BaseUserManager[UserType]):
    use_in_migrations = True

    def _create_user(self, phone_number: str, password: str | None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be set")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, phone_number: str, password: str | None = None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(
        self, phone_number: str, password: str | None = None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = None

    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        unique=True,
        help_text=_("User's mobile phone number (international format)"),
    )

    invite_code = models.CharField(
        _("invite code"),
        max_length=6,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Unique 6-character code this user can give to others"),
    )
    activated_invite_code = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        help_text=_("User whose invite code this user has activated"),
    )

    objects: UserManager["User"] = UserManager()
    REQUIRED_FIELDS: list[str] = []

    # Attach the custom manager
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = "users"

    def __str__(self) -> str:
        return self.phone_number
