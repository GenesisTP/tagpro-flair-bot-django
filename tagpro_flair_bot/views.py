from BeautifulSoup import BeautifulSoup
import json
import praw
import requests
from urlparse import urlparse
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from social_auth.pipeline import deauth_tagpro as deauth_tagpro_pipeline
from tpflair.flair import FLAIR_DATA, FLAIR, FLAIR_BY_POSITION


reddit_api = praw.Reddit(user_agent=settings.BOT_USER_AGENT)
reddit_api.config.decode_html_entities = True
reddit_api.login(username=settings.REDDIT_MOD_USERNAME, password=settings.REDDIT_MOD_PASSWORD)

def redirect_home():
    return redirect(reverse('home'))

def json_response(data):
    return HttpResponse(json.dumps(data), content_type="application/json")


class HomeView(TemplateView):
    template_name = "home.html"
    
    def get_context_data(self):
        context = super(HomeView, self).get_context_data()
        context.update({'FLAIR_DATA': FLAIR_DATA})
        return context


def parse_available_flair(html_soup):
    """
    Helper function which pulls the active flairs from the parsed HTML of a
    user's profile page.
    """
    flair_table = html_soup.findAll('table')[2]
    rows = flair_table.findAll('tr')
    flairs = []
    for row in rows:
        icon = row.find('div')
        if icon and row.get("class", "") != "fade":
            position = str(icon['style'][len('background-position: '):])
            try:
                flairs.append(FLAIR_BY_POSITION[position]['id'])
            except KeyError:
                pass
    return flairs


def clean_tagpro_url(url):
    """
    Create our own URL by parsing the profile id and getting the profile from
    a trusted domain like tagpro-origin.koalabeast.com.
    """
    path = urlparse(url).path
    
    # /profile/555.../ to a list of path elements, without any empty strings
    # so, id = ['profile', 'id'][1]
    tagpro_profile_id = filter(None, path.split('/'))[1]
    return "http://{domain}/profile/{id}/".format(
        domain=settings.TAGPRO_PROFILE_DOMAIN,
        id=tagpro_profile_id)


def get_tagpro_profile(profile_url):
    """
    Retrieve the TagPro profile associated with the given `profile_url`
    after cleaning it.
    """
    cleaned_url = clean_tagpro_url(profile_url)
    response = requests.get(cleaned_url)
    return response


def auth_tagpro(request):
    """
    Verify that the user owns the specified TagPro profile.
    """
    token = request.session.get('tagpro_token')
    try:
        profile_url = request.POST.get('profile_url')
        response = get_tagpro_profile(profile_url)
    except:
        messages.error(request, "Please enter a valid TagPro profile URL.")
        return redirect_home()
    parsed = BeautifulSoup(response.text)
    tagpro_name = parsed.title.getString()[len("TagPro Ball: "):]
    if tagpro_name.replace(' ', '') == token:
        request.session['tp_authenticated'] = True
        request.session['tp_profile'] = profile_url
        request.session['current_flair'] = get_current_flair(request)
        request.session['available_flair'] = parse_available_flair(parsed)
    else:
        messages.error(request, "Your name doesn't match the token!")
    return redirect_home()


def deauth_tagpro(request):
    """
    Unlink the session from the specified TagPro profile.
    """
    deauth_tagpro_pipeline(request=request)
    return redirect_home()


def refresh_flair(request):
    """
    Refresh the flair available from the linked TagPro account.
    """
    if not request.session['tp_authenticated']:
        messages.error(request, "You have not authenticated your TagPro account!")
        return redirect_home()
    try:
        profile_url = request.session['tp_profile']
        response = get_tagpro_profile(profile_url)
    except:
        messages.error(request, "Unable to retrieve flair, please check your TagPro URL.")
        return redirect_home()
    parsed = BeautifulSoup(response.text)
    request.session['available_flair'] = parse_available_flair(parsed)
    return redirect_home()


def get_current_flair(request):
    return reddit_api.get_flair(
        settings.REDDIT_MOD_SUBREDDIT, request.user.username) or {}

def set_flair(request):
    """
    Set the user's flair for the subreddit.
    """
    flair = request.POST.get('flair', None)
    if (
            'available_flair' in request.session and 
            flair in request.session['available_flair'] and 
            flair in FLAIR.keys()):
        request.session['current_flair'] = request.session['current_flair'] or get_current_flair(request)
        flair_text = request.session['current_flair'].get('flair_text', '')
        reddit_api.set_flair(
            settings.REDDIT_MOD_SUBREDDIT,
            request.user.username,
            flair_css_class=flair, flair_text=flair_text)
        request.session['current_flair']['flair_css_class'] = flair
        if request.is_ajax():
            return json_response({'success': True})
        else:
            messages.success(request, "Flair set!")
    else:
        error = "Sorry, you can't have that flair :("
        if request.is_ajax():
            return json_response({'success': False, 'error': error})
        messages.error(request, error)
    return redirect_home()
