from django.db import models
from django.db import settings
from django.template.defaultfilters import truncatewords


class Item(models.Model):
    entry = models.ForeignKey('Entry')
    value = models.TextField()

    def truncated_value(self, arg=30):
        return truncatewords(self.value, arg)


class Entry(models.Model):
    feed = models.ForeignKey('Feed')
    pub_time = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'entries'

    def __unicode__(self):
        return self.feed.url


class Feed(models.Model):
    url = models.URLField()

    def __unicode__(self):
        return self.url
