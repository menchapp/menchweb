import cgi
from google.appengine.api import users
from django import http
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import Context, loader 
from django.core.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from models import *

from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers


from djangoappengine import storage
class BlobstoreFileUploadHandler(storage.BlobstoreFileUploadHandler):
  """Handler that adds blob key info to the file object."""

  def new_file(self, field_name, *args, **kwargs):
    # We need to re-process the POST data to get the blobkey info.
    meta = self.request.META
    meta['wsgi.input'].seek(0)
    fields = cgi.FieldStorage(meta['wsgi.input'], environ=meta)
    if field_name in fields:
        current_field = fields[field_name]
        self.content_type_extra = current_field.type_options
    super(BlobstoreFileUploadHandler, self).new_file(field_name,
                                                     *args, **kwargs)


def home(request):
	return http.HttpResponse('Hello World!')

def add_rfp(request):
  user = users.get_current_user()
  if user == None:
    return HttpResponse("User not logged in.")  
  if request.method != 'POST':
    return HttpResponse("Add RFP only accepts POSTs")  
  print request.body
  return HttpResponse("Success!")  

@ensure_csrf_cookie
def browse_projects(request):
  user = users.get_current_user()
  if user:
    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('beta'),
      'logged_in': True
    }, autoescape=False)
  else:
    context = Context({
      'user_name': "",
      'login_url': users.create_login_url('beta'),
      'logout_url': "",
      'logged_in': False
    }, autoescape=False)
  template = loader.get_template('browse-projects.html')
  return HttpResponse(template.render(context))  

@ensure_csrf_cookie
def my_projects(request):
  user = users.get_current_user()
  if user:
    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('beta'),
      'logged_in': True
    }, autoescape=False)
  else:
    context = Context({
      'user_name': "",
      'login_url': users.create_login_url('beta'),
      'logout_url': "",
      'logged_in': False
    }, autoescape=False)
  template = loader.get_template('my-projects.html')
  return HttpResponse(template.render(context))  

@ensure_csrf_cookie
def my_profile(request):
  user = users.get_current_user()
  if user:
    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('beta'),
      'logged_in': True
    }, autoescape=False)
  else:
    context = Context({
      'user_name': "",
      'login_url': users.create_login_url('beta'),
      'logout_url': "",
      'logged_in': False
    }, autoescape=False)
  template = loader.get_template('my-profile.html')
  return HttpResponse(template.render(context))  


def beta(request):
  user = users.get_current_user()
  if user:
    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('beta'),
      'logged_in': True
    }, autoescape=False)
  else:
    context = Context({
      'user_name': "",
      'login_url': users.create_login_url('beta'),
      'logout_url': "",
      'logged_in': False
    }, autoescape=False)

  template = loader.get_template('my-projects.html')
  return HttpResponse(template.render(context))  


def test(request):
  upload_url = blobstore.create_upload_url('/upload-photo.html')
  # The method must be "POST" and enctype must be set to "multipart/form-data".
  # user = users.get_current_user()
  # if user:
  #   name = user.nickname()
  #   login_url = users.create_logout_url('/')
  #   greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
  #              (user.nickname(), users.create_logout_url('/')))
  # else:
  #   name = "friend"
  #   login_url = users.create_login_url('/')
  #   greeting = ('<a href="%s">Sign in or register</a>.' %
  #               users.create_login_url('/'))

  profile_query = UserPhoto.query(UserPhoto.user == users.get_current_user().user_id())
  profile = profile_query.fetch()
  print profile[0].to_dict()['blob_key']

  template = loader.get_template('test.html')
  # # Context is a normal Python dictionary whose keys can be accessed in the template index.html
  context = Context({
    'url': upload_url,
    'profile_url': images.get_serving_url(profile[0].to_dict()['blob_key'])
  })
  context.update(csrf(request))
  return HttpResponse(template.render(context))

def photo_upload_handler(request):
  image = request.FILES['file']
  image_key = image.blobstore_info.key()
  user_photo = UserPhoto(user=users.get_current_user().user_id(),
                         blob_key=image_key)
  user_photo.put()
  return HttpResponse('Success upload!')

