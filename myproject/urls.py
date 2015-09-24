from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'beta', 'mench.views.beta'),
    url(r'my-projects.html', 'mench.views.my_projects'),
    url(r'browse-projects.html', 'mench.views.browse_projects'),
    url(r'my-profile.html', 'mench.views.my_profile'),    
    url(r'test', 'mench.views.test'),  
    url(r'add-rfp.html', 'mench.views.add_rfp'),    
    url(r'upload-profile-photo.html', 'mench.views.profile_photo_upload_handler'),    
    url(r'upload-rfp-photo/(?P<rfp_key>[0-9]+)', 'mench.views.rfp_photo_upload_handler'),        
    url(r'save-user-profile.html', 'mench.views.save_profile'),    
    url(r'^$', 'mench.views.browse_projects'),
)
