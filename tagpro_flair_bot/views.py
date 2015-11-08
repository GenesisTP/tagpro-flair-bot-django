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

import logging
logger = logging.getLogger(__name__)


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
        return context


def parse_wiki_tables(request):
    """
    Parse the TagPro wiki to retrieve its flair data.
    """
    global FLAIR_DATA, FLAIR, FLAIR_BY_POSITION, USER_BY_REDDIT, USER_BY_TAGPRO, SPECIAL_FLAIR_DATA, SPECIAL_FLAIR, USER_FLAIR_DATA
    page = reddit_api.get_wiki_page(settings.REDDIT_MOD_SUBREDDIT, 'flair/flairbot')
    
    tables = []
    for section in page.content_md.split('-|-\r\n')[1:]:
        table = []
        for row in section.split('\r\n\r\n')[0].split('\r\n'):
            table.append(tuple(cell.strip() for cell in row.split('|')))
        tables.append(table)
    
    FLAIR_DATA, SPECIAL_FLAIR_DATA, USER_DATA, USER_FLAIR_DATA = tables
    
    FLAIR = dict((k, {'position': p, 'title': t}) for k, t, p in FLAIR_DATA)
    FLAIR_BY_POSITION = dict((p, {'id': k, 'title': t}) for k, t, p in FLAIR_DATA)
    
    SPECIAL_FLAIR = dict((k, {'position': p, 'size': s, 'title': t}) for k, t, p, s in SPECIAL_FLAIR_DATA)
    
    USER_BY_REDDIT = dict((r, {'name': k, 'tagpro': t}) for k, r, t in USER_DATA)
    USER_BY_TAGPRO = dict((t, {'name': k, 'reddit': r}) for k, r, t in USER_DATA)
    
    request.session['flair_data'] = FLAIR_DATA
    request.session['special_flair_data'] = SPECIAL_FLAIR_DATA


def parse_available_flair(html_soup):
    """
    Helper function which pulls the active flairs from the parsed HTML of a
    user's profile page.
    """
    flair_table = html_soup.findAll('table')[4]
    rows = flair_table.findAll('tr')
    flairs = []
    for row in rows:
        icon = row.find('div')
        if icon and row.get("class", "") != "fade":
            position = str(icon['style'][len('background-position: '):])
            try:
                flairs.append(FLAIR_BY_POSITION[position]['id'])
            except KeyError:
                logger.warn("New flair at position %(position)s",
                    extra={'position': position, 'row': row})
    return flairs

def get_available_special_flair(request):
    """
    Retrieve all special flair available to a user.
    """
    user = None
    if request.session['tp_profile_id'] in USER_BY_TAGPRO.keys():
        user = USER_BY_TAGPRO[request.session['tp_profile_id']]['name']
    elif request.user.username in USER_BY_REDDIT.keys():
        user = USER_BY_REDDIT[request.user.username]['name']
    flairs = []
    for name, flair in USER_FLAIR_DATA:
        if name == user:
            flairs.append(flair)
    return flairs


def get_special_flair_img():
    """
    Use the subreddit's flair sprite to create special flairs.
    """
    sub = reddit_api.get_subreddit(settings.REDDIT_MOD_SUBREDDIT)
    style = sub.get_stylesheet()
    for image in style.get('images'):
        if image['name'] == 'flair':
            return image['url']


def parse_tagpro_url(url):
    """
    Parse the profile id to get the profile from a trusted domain like
    tagpro-origin.koalabeast.com.
    """
    base, path = urlparse(url).netloc, urlparse(url).path
    
    # /profile/555.../ to a list of path elements, without any empty strings
    # so, id = ['profile', 'id'][1]
    tagpro_server = filter(None, filter(None, base.split('.'))[0].split('-'))[1]
    tagpro_profile_id = filter(None, path.split('/'))[1]
    return tagpro_server, tagpro_profile_id


def get_tagpro_profile(server, profile_id):
    """
    Retrieve the TagPro profile associated with the given `profile_id`
    after parsing it.
    """
    profile_url = "http://tagpro-{domain}.koalabeast.com/profile/{id}/".format(
        domain=server,
        id=profile_id)
    response = requests.get(profile_url)
    return response


def auth_tagpro(request):
    """
    Verify that the user owns the specified TagPro profile.
    """
    token = request.session.get('tagpro_token')
    try:
        profile_url = request.POST.get('profile_url')
        server, profile_id = parse_tagpro_url(profile_url)
        response = get_tagpro_profile(server, profile_id)
    except:
        messages.error(request, "Please enter a valid TagPro profile URL.")
        return redirect_home()
    parsed = BeautifulSoup(response.text)
    tagpro_name = parsed.title.getString()[len("TagPro Ball: "):]
    if tagpro_name.replace(' ', '') == token.replace(' ', ''):
        parse_wiki_tables(request)
        request.session['tp_authenticated'] = True
        request.session['tp_server'] = server
        request.session['tp_profile_id'] = profile_id
        request.session['current_flair'] = get_current_flair(request)
        request.session['available_flair'] = parse_available_flair(parsed)
        request.session['available_special_flair'] = get_available_special_flair(request)
        request.session['special_flair_img'] = get_special_flair_img()
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
    if not request.session.get('tp_authenticated'):
        messages.error(request, "You have not authenticated your TagPro account!")
        return redirect_home()
    try:
        server = request.session['tp_server']
        profile_id = request.session['tp_profile_id']
        response = get_tagpro_profile(server, profile_id)
    except:
        messages.error(request, "Unable to retrieve flair. Please check your TagPro URL.")
        return redirect_home()
    parsed = BeautifulSoup(response.text)
    parse_wiki_tables(request)
    request.session['available_flair'] = parse_available_flair(parsed)
    request.session['available_special_flair'] = get_available_special_flair(request)
    request.session['special_flair_img'] = get_special_flair_img()
    return redirect_home()


def get_current_flair(request):
    return reddit_api.get_flair(
        settings.REDDIT_MOD_SUBREDDIT, request.user.username) or {}

def set_flair(request):
    """
    Set the user's flair for the subreddit.
    """
    flair = request.POST.get('flair', None)
    if ((
            'available_flair' in request.session and 
            flair in request.session['available_flair'] and 
            flair in FLAIR.keys()
        ) or (
            'available_special_flair' in request.session and 
            flair in request.session['available_special_flair'] and 
            flair in SPECIAL_FLAIR.keys()
        )):
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
