from django.db import models


class Item(models.Model):
    entry = models.ForeignKey('Entry')
    value = models.TextField()
    pass


class Entry(models.Model):
    feed = models.ForeignKey('Feed')
    pub_time = models.DateTimeField()


class Feed(models.Model):
    url = models.URLField()
