from django.conf.urls import patterns, include, url
from views import *
from dinero import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home),
    url(r'^getEntries/$', getEntries),
    url(r'^newEntry/$', newEntry),
    url(r'^allEntries/$', allEntries),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.STATIC_ROOT}),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', logout_view),
)
