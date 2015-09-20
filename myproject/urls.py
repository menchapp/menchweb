from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'beta', 'hello.views.beta'),
    url(r'test', 'hello.views.test'),    
    url(r'^$', 'hello.views.home'),
)
