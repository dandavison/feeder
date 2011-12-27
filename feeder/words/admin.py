from django.contrib import admin

from words.models import Feed, Entry, Item


class FeedAdmin(admin.ModelAdmin):
    list_display = ('url',)


class EntryAdmin(admin.ModelAdmin):
    list_display = ('feed', 'pub_time',)


class ItemAdmin(admin.ModelAdmin):

    def entry__pub_time(self, obj):
        return obj.entry.pub_time

    list_display = ('entry', 'entry__pub_time', 'truncated_value',)
    list_filter = ('entry__pub_time',)
    ordering = ('-entry__pub_time',)
    search_fields = ('value',)


admin.site.register(Feed, FeedAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Item, ItemAdmin)
