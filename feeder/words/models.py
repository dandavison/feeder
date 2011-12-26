from django.db import models
from django.db import settings


class Item(models.Model):
    entry = models.ForeignKey('Entry')
    value = models.TextField()


class Entry(models.Model):
    feed = models.ForeignKey('Feed')
    pub_time = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'entries'


class Feed(models.Model):
    url = models.URLField()

    def __unicode__(self):
        return self.url
