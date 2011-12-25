from django.db import models
from django.db import settings

from feeder_cli import parse


class ItemManager(models.Manager):

    def dump_wordsets(self, fp, **filter_kwargs):
        """
        Format suitable as input to Christian Borgelt's frequent
        pattern mining programs.
        http://borgelt.net/fpm.html
        """
        print 'Searching for items matching:'
        for kwarg in filter_kwargs.items():
            print '\t%s: %s' % kwarg
        
        items = self.filter(**filter_kwargs)
        print 'Got %d items' % items.count()
        for item in items:
            words = set(parse(item.value)) - settings.COMMON_WORDS
            # TODO: the file object that is passed in should know how
            # to do the necessary encoding
            fp.write((' '.join(words) + '\n').encode('utf-8'))


class Item(models.Model):
    entry = models.ForeignKey('Entry')
    value = models.TextField()

    objects = ItemManager()


class Entry(models.Model):
    feed = models.ForeignKey('Feed')
    pub_time = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'entries'


class Feed(models.Model):
    url = models.URLField()
