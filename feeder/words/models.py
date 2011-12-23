from django.db import models
from django.db import settings

from feeder_cli import parse


class ItemManager(models.Manager):

    def dump_wordsets(self, fp):
        """
        Format suitable as input to Christian Borgelt's frequent
        pattern mining programs.
        http://borgelt.net/fpm.html
        """
        for item in self.all():
            words = set(parse(item.value)) - settings.COMMON_WORDS
            fp.write(' '.join(words) + '\n')


class Item(models.Model):
    entry = models.ForeignKey('Entry')
    value = models.TextField()

    objects = ItemManager()


class Entry(models.Model):
    feed = models.ForeignKey('Feed')
    pub_time = models.DateTimeField()


class Feed(models.Model):
    url = models.URLField()
