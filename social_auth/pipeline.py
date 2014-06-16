import string
import random
from django.conf import settings

def gen_token():
    token_override = getattr(settings, 'TAGPRO_AUTH_TOKEN_OVERRIDE', None)
    if token_override is not None:
        return token_override
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))

def set_token(strategy, details, user=None, *args, **kwargs):
    request = kwargs.get('request')
    request.session['tagpro_token'] = gen_token()

def deauth_tagpro(*args, **kwargs):
    request = kwargs.get('request')
    if 'tp_authenticated' in request.session:
        del request.session['tp_authenticated']
    if 'tp_profile' in request.session:
        del request.session['tp_profile']
    if 'available_flair' in request.session:
        del request.session['available_flair']
    if 'current_flair' in request.session:
        del request.session['current_flair']
