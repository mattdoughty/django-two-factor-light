from django.contrib.auth import BACKEND_SESSION_KEY
from django.core.exceptions import PermissionDenied


def full_login_required(function):
    def decorator(request, *args, **kwargs):
        if request.user.is_authenticated() and request.session[BACKEND_SESSION_KEY] == "two_factor_light.backends.TwoFactorBackend":
            return function(request, *args, **kwargs)
        raise PermissionDenied()
    
    return decorator
