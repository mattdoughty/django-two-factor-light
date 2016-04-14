from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied


class TwoFactorBackend(ModelBackend):

    def authenticate(self, username=None, password=None, token=None, user=None, **kwargs):
        if token is None:
            # The user hasn't given us a token yet, so try the ModelBackend
            return None

        if not any([username, password, user]):
            # Must supply either a username + password or a user object.
            return None

        if username and password:
            user = super(TwoFactorBackend, self).authenticate(username, password)

        if user.verify_token(token):
            return user
