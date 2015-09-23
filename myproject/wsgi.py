"""
WSGI config for myproject project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "myproject.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers

class ServeVideoHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, photo_key):
    if not blobstore.get(photo_key):
      self.error(404)
    else:
      img = images.get_serving_url(photo_key) + "=s100"
      # img.resize(width=80, height=100)
      # img.im_feeling_lucky()
      # thumbnail = img.execute_transforms(output_encoding=images.JPEG)

      # self.response.headers['Content-Type'] = 'image/jpeg'
      self.response.out.write(img)
      #self.send_blob(photo_key)
    
downloader_handler = webapp.WSGIApplication([('/view/([A-Za-z0-9\-\=_]+)', ServeVideoHandler),], debug=True)
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
