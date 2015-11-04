import string
import random
from django.conf import settings

def gen_token():
    token_override = getattr(settings, 'TAGPRO_AUTH_TOKEN_OVERRIDE', None)
    if token_override is not None:
        return token_override
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))

def set_token(strategy, details, user=None, *args, **kwargs):
    strategy.request.session['tagpro_token'] = gen_token()

def deauth_tagpro(*args, **kwargs):
    request = kwargs.get('strategy').request
    if 'tp_authenticated' in request.session:
        del request.session['tp_authenticated']
    if 'tp_server' in request.session:
        del request.session['tp_server']
    if 'tp_profile_id' in request.session:
        del request.session['tp_profile_id']
    if 'available_flair' in request.session:
        del request.session['available_flair']
    if 'current_flair' in request.session:
        del request.session['current_flair']
