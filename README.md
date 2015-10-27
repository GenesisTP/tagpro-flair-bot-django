/r/TagPro Flair Bot
===================

This is a Django project to allow users to assign their own Reddit flair based
on what they have earned with their TagPro profile.

# Development

To do anything, you need to go into your [Reddit apps] and create a new web app for development and Heroku.  Your app in development should have the `redirect_uri` set to `http://localhost:5000/complete/reddit/`.  When you have a Heroku instance, the host should be that Heroku instance's name instead of localhost:port. If you decide to run locally on a different port don't forget to change it in your Reddit app.  If you want to support SSL on Heroku, you need to create a separate web app on Reddit for that too (because `https://...` is a different string than `http://...`).

## Heroku

To deploy to Heroku you'll need to install the [Heroku client], and then run `heroku login` followed by `heroku create` (in this directory).  From then on you can `git push heroku` to deploy.

[Heroku client]: https://toolbelt.heroku.com/

## Local development

To make it easy, install the Heroku CLI above if you haven't.

Set up your Python virtual environment and dependencies

```
virtualenv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

Set up the database

```
./manage.py syncdb --settings=tagpro_flair_bot.settings.development
```

Make a copy of `.env.sample` and call it `.env`, and fill in those settings with your stuff.

### Run it locally
```
heroku local dev -e .env

# If you want to use a different port:
heroku local dev -e .env -p 8000

# If you set all the environment in .env yourself you can also do
./manage.py runserver
```

# Environment
The following *environmental variables* need to be set to run the app:

* ``SOCIAL_AUTH_REDDIT_KEY`` and ``SOCIAL_AUTH_REDDIT_SECRET``
    * Obtained through Reddit. You must create an app in your
    [Reddit preferences](https://ssl.reddit.com/prefs/apps/).
* ``SOCIAL_AUTH_REDDIT_KEY_SECURE`` and ``SOCIAL_AUTH_REDDIT_SECRET_SECURE``
    * If you want to support SSL, create a second app with a https://
    `redirect_uri`, and set these to this app's key/secret.
* ``REDDIT_MOD_SUBREDDIT``
    * Subreddit flairs are assigned for.
* ``REDDIT_MOD_USERNAME``
    * Username of the user the bot uses to assign the flair. Must be a
    moderator of ``REDDIT_MOD_SUBREDDIT``.
* ``REDDIT_MOD_PASSWORD``
    * Reddit password for ``REDDIT_MOD_USERNAME``.
* ``RAVEN_PUBLIC_KEY``, ``RAVEN_PRIVATE_KEY``, ``RAVEN_PROJECT_ID``
    * If you're running your own instance and you want error reporting through
    Sentry, set these to what Sentry provides for your DSN. The format is
    ``https://RAVEN_PUBLIC_KEY:RAVEN_PRIVATE_KEY@app.getsentry.com/RAVEN_PROJECT_ID``


# Authentication

## Reddit

Reddit authentication is managed with Reddit's own OAuth2 API.  A new user in
the app is created with their Reddit username when they authenticate through 
Reddit.

## TagPro

Right now TagPro authentication is a bit hacky.  After a user authenticates with
Reddit, they are assigned a 12-character token.  To prove they own a profile,
they change their name to this token and supply the app with their profile URL.
The app decides that the user owns the profile if the name of the user on the
profile matches the generated token.

In the future this hack could be avoided if there was a TagPro-blessed way of
confirming that a user owns a TagPro profile. One option discussed with Lucky
was an API key available on your profile only when logged in which you could
supply to apps. Then there would be a URL on TagPro the app would post the key
to which would return whether the key was valid for the profile or not.