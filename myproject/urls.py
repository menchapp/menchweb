from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'beta', 'hello.views.beta'),
    url(r'^$', 'hello.views.home'),
)
