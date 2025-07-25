from __future__ import annotations
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create_user(self, phone_number: str, password: str | None, **extra):
        if not phone_number:
            raise ValueError("Phone number must be set")
        user = self.model(phone_number=phone_number, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra)

    def create_superuser(self, phone_number: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)

        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra)


class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        null=True,
        unique=False,
        help_text=_("Not used for authentication; kept for compatibility."),
    )

    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        unique=True,
        help_text=_("Primary identifier."),
    )

    invite_code = models.CharField(
        _("invite code"),
        max_length=6,
        unique=True,
        null=True,
        blank=True,
        help_text=_("User's own 6-char invite code."),
    )
    activated_invite_code = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        help_text=_("Referrer whose code was activated."),
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS: list[str] = []

    objects: "UserManager" = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = "users"

    def __str__(self) -> str:
        return self.phone_number
