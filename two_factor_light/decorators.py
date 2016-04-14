from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django.utils.six.moves.urllib.parse import urlparse


TWO_FACTOR_LOGIN_URL = getattr(settings, 'TWO_FACTOR_LOGIN_URL', settings.LOGIN_URL)
TWO_FACTOR_SETUP_URL = getattr(settings, 'TWO_FACTOR_SETUP_URL', None)


def full_login_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None, two_factor_login_url=None,
                        two_factor_setup_url=None):
    """
    Decorator for views that checks that the user is logged in with 2FA, if applicable.

    Redirects to TWO_FACTOR_LOGIN_URL if logged in but not with 2FA.
    Redirects to TWO_FACTOR_SETUP_URL if logged in but hasn't yet setup 2FA.
    Redirects to LOGIN_URL if not logged in at all.
    """
    def decorator(request, *args, **kwargs):
        if (request.user.is_authenticated() and
                (request.session[BACKEND_SESSION_KEY] == "two_factor_light.backends.TwoFactorBackend" or
                    not request.user.two_factor_required
                 )):
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated():
            # If user isn't authenticated, do the same as login_required - redirect to login
            resolved_redirect_url = resolve_url(login_url or settings.LOGIN_URL)
        elif request.user.two_factor_enabled:
            # If the user has two factor auth, redirect to two factor login url
            resolved_redirect_url = resolve_url(two_factor_login_url or TWO_FACTOR_LOGIN_URL)
        else:
            # The user hasn't setup two factor auth yet, so redirect to setup url
            resolved_redirect_url = resolve_url(two_factor_setup_url or TWO_FACTOR_SETUP_URL)

        path = request.build_absolute_uri()
        redirect_scheme, redirect_netloc = urlparse(resolved_redirect_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if ((not redirect_scheme or redirect_scheme == current_scheme) and
                (not redirect_netloc or redirect_netloc == current_netloc)):
            path = request.get_full_path()
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            path, resolved_redirect_url, redirect_field_name
        )
    return decorator
