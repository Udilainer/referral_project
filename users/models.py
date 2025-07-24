from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = None

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        help_text="User's phone number (main identifier)"
    )

    invite_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        unique=True,
        help_text="User's own invite code that others can use"
    )

    activated_invite_code = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals',
        help_text="The invite code this user activated (referrer)"
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.phone_number
