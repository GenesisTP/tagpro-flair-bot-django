from django.core.management.base import NoArgsCommand
from tagpro_flair_bot.models import TagProUser as User


class Command(NoArgsCommand):
    help = """
    For some reason, python-social-auth creates users with screwed up usernames
    sometimes.  This clears out these users allowing them to use the app.
    """
    def handle(self, **options):
        for user in User.objects.all():
            User.objects.exclude(id=user.id).filter(
                username__startswith=user.username[:15]).delete()
