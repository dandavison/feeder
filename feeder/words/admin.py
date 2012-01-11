from django.contrib import admin

from words.models import Feed, Entry, Item


class FeedAdmin(admin.ModelAdmin):
    list_display = ('url',)


class EntryAdmin(admin.ModelAdmin):
    list_display = ('feed', 'pub_time',)


class ItemAdmin(admin.ModelAdmin):

    def entry__pub_time(self, obj):
        return obj.entry.pub_time

    def entry__feed__link(self, obj):
        return '<a href=%s>%s</a>' % ((obj.entry.feed.url,) * 2)
    entry__feed__link.allow_tags = True

    list_display = ('entry__feed__link', 'entry__pub_time', 'truncated_value',)
    list_filter = ('entry__pub_time',)
    ordering = ('-entry__pub_time',)
    search_fields = ('value',)


admin.site.register(Feed, FeedAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Item, ItemAdmin)
