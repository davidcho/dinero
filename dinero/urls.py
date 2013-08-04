from django.conf.urls import patterns, include, url
from views import *
from dinero import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home),
    url(r'^getEntries/$', getEntries),
    url(r'^newEntry/$', newEntry),

    # url(r'^ajaxexample$', main),
    # url(r'^ajaxexample_json$', ajax),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # static files for all pages
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.STATIC_ROOT}),
)
