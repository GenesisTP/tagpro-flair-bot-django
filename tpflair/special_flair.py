import praw
from django.conf import settings

reddit_api = praw.Reddit(user_agent=settings.BOT_USER_AGENT)
reddit_api.login(username=settings.REDDIT_MOD_USERNAME, password=settings.REDDIT_MOD_PASSWORD)
page = reddit_api.get_wiki_page(settings.REDDIT_MOD_SUBREDDIT, 'flair/userlist')

tables = []
for section in page.content_md.split('-|-\r\n')[1:]:
    table = []
    for row in section.split('\r\n\r\n')[0].split('\r\n'):
        table.append(tuple(cell.strip() for cell in row.split('|')))
    tables.append(table)

USER_DATA, SPECIAL_FLAIR_DATA, USER_FLAIR_DATA = tables

USER_BY_REDDIT = dict((r, {'name': k, 'tagpro': t}) for k, r, t in USER_DATA)
USER_BY_TAGPRO = dict((t, {'name': k, 'reddit': r}) for k, r, t in USER_DATA)

SPECIAL_FLAIR = dict((k, {'position': p, 'size': s, 'title': t}) for k, t, p, s in SPECIAL_FLAIR_DATA)
