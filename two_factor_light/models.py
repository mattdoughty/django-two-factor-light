import base64
import time
from os import urandom

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from urllib import quote, urlencode

from .oath import TOTP


TWO_FACTOR_TOLERANCE = getattr(settings, 'TWO_FACTOR_TOLERANCE', 1)
TWO_FACTOR_ISSUER = getattr(settings, 'TWO_FACTOR_ISSUER', 'Django App')


class AbstractTwoFactorUser(models.Model):

    class Meta:
        abstract = True

    two_factor_required = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=16, default=lambda: base64.b32encode(urandom(8)))
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

    @property
    def setup_url(self):
        issuer = TWO_FACTOR_ISSUER.encode('utf-8')

        label = quote(b': '.join([issuer, self.two_factor_custom_name]))

        query = [
            ('secret', self.two_factor_secret),
            ('issuer', issuer),
        ]

        return 'otpauth://totp/{}?{}'.format(label, urlencode(query))



class TwoFactorUser(AbstractTwoFactorUser, AbstractUser):
    class Meta:
        swappable = "AUTH_USER_MODEL"
