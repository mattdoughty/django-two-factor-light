import base64
import time

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .oath import TOTP


TWO_FACTOR_TOLERANCE = getattr(settings, 'TWO_FACTOR_TOLERANCE', 1)


class AbstractTwoFactorUser(models.Model):

    class Meta:
        abstract = True

    two_factor_required = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=16, blank=True, null=True)
    two_factor_custom_name = models.CharField(max_length=50)

    def secret_clean(self):
        return base64.b32decode(self.two_factor_secret)

    def verify_token(self, token):
        try:
            token = int(token)
        except ValueError:
            return False

        totp = TOTP(self.secret_clean())
        totp.time = time.time()

        for offset in range(-TWO_FACTOR_TOLERANCE, TWO_FACTOR_TOLERANCE + 1):
            totp.drift = offset
            if totp.token() == token:
                return True

        return False


class TwoFactorUser(AbstractTwoFactorUser, AbstractUser):
    class Meta:
        swappable = "AUTH_USER_MODEL"
