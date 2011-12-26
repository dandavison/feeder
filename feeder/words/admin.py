from django.contrib import admin
from words.models import Feed, Entry, Item


class FeedAdmin(admin.ModelAdmin):
    list_display = ('url',)


class EntryAdmin(admin.ModelAdmin):
    list_display = ('feed', 'pub_time',)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('entry', 'value',)


admin.site.register(Feed, FeedAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Item, ItemAdmin)
