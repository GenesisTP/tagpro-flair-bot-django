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
    keys = [
        'tp_authenticated',
        'tp_server',
        'tp_profile_id',
        'flair_data',
        'available_flair',
        'special_flair_data',
        'available_special_flair',
        'special_flair_img',
        'current_flair',
    ]
    for key in keys:
        if key in request.session:
            del request.session[key]
