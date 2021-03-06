from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'feeder.views.home', name='home'),
    # url(r'^feeder/', include('feeder.foo.urls')),

    url(r'^$', 'words.views.home'),
    url(r'^wordsets/$', 'words.views.frequent_wordsets'),
    url(r'^new_wordsets/$', 'words.views.new_wordsets'),
    url(r'^items/$', 'words.views.matching_items'),

    url(r'^scraper/$', 'scraper.views.scraper'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
