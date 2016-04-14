# Django Two Factor Light

Two Factor authentication for Django. Inspired by [django-two-factor-auth](https://github.com/Bouke/django-two-factor-auth) but intended to be a lot lighter. You can use as much or as little of it as you like and the only dependency is Django itself. Currently only supports TOTP auth, like Google/Microsoft Authenticator. Currently in development, so don't use in production yet!


## Installation

`pip install git+https://github.com/mattdoughty/django-two-factor-light`

## Setup

1. Add `two_factor_light` to `settings.INSTALLED_APPS`
1. Change `settings.AUTHENTICATION_BACKENDS` to:
   ````
   AUTHENTICATION_BACKENDS = (
       'two_factor_light.backends.TwoFactorBackend',
       'django.contrib.auth.backends.ModelBackend',
   )
   ````
1. Make your user model inherit from `AbstractTwoFactorUser` or set `settings.AUTH_USER_MODEL` to `two_factor.TwoFactorUser`
1. Set `settings.TWO_FACTOR_SETUP_URL` and `settings.TWO_FACTOR_LOGIN_URL`

## Usage

### Decorators

Protect any views that require two factor auth with `two_factor_light.decorators.full_login_required`. Note that this will permit users who are not required to use two factor auth.

Views that require only password login (for example views that actually setup the two factor auth) can use the `login_required` decorator from django.contrib.auth as normal.


### Views

You are responsible for writing views to handle the logging in of users and setting up two factor auth.

#### Two factor setup view
By default, the user has a secret key defined when created, so all you need to do is display this to the user with instructions and set `two_factor_enabled` to `True`. You may want to generate a QR code using the `setup_url` User property.

#### Two factor log in view
You can authenticate the user with username, password and token in one call, if you just want one login form. Or, you can authenticate the user with a token as a second step after authenticating with username and password.

Basic example of the second step view of a two step approach:
````
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse


@login_required
def two_factor_login(request):
    if request.POST:
        user = authenticate(user=request.user, token=request.POST.get('token'))
        if user:
             login(request, user)
             return HttpResponseRedirect(request.GET.get('next'))
    return TemplateResponse(request, 'two_factor_login.html')
````