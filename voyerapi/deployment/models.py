from jsonfield import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

# LEXERS = [item for item in get_all_lexers() if item[1]]
# LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
# STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class CanvasContent(models.Model):
    username = models.TextField()
    cards = JSONField()
    deployed = models.BooleanField(default=False)
    build_uuid = models.TextField(default='notSet')
    build_prog = models.IntegerField(default=0)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    # class Meta:
    #     ordering = ('username',)
