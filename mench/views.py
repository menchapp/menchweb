import json
import cgi
import datetime
from google.appengine.api import users
from django import http
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect 
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
  data = json.loads(request.body)

  year, month, day = data['endDate'].split('-')
  end_date = datetime.date(int(year), int(month), int(day))

  rfp = Rfp(user=user.user_id(),
            title=data['title'],
            subtitle=data['subtitle'],
            prize=int(data['prize']),
            endDate=end_date,
            details=data['details'],
            terms=data['terms'],
            intendedUse=data['intendedUse'],
            duration=data['duration'],
            territory=data['territory'],
            exclusivity=data['exclusivity'],
            hashtag=data['hashtag'])  
  rfp.put()
  return HttpResponse(blobstore.create_upload_url('/upload-rfp-photo/' 
                                                  + str(rfp.key.id())))  

def save_profile(request):
  user = users.get_current_user()
  if user == None:
    return HttpResponse("User not logged in.")  
  if request.method != 'POST':
    return HttpResponse("Add RFP only accepts POSTs")  
  print request.body
  data = json.loads(request.body)

  profile = Profile(brand="",
                 user=user.user_id(),
                 name=data['name'],
                 email=data['email'],
                 phone=data['phone'],
                 instagram=data['instagram'],
                 location=data['location'],
                 about=data['description'])

  profile.put()
  return HttpResponse("Success!")  

@ensure_csrf_cookie
def browse_projects(request):
  user = users.get_current_user()
  if user:
    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('/'),
      'logged_in': True
    }, autoescape=False)
  else:
    context = Context({
      'user_name': "",
      'login_url': users.create_login_url('/'),
      'logout_url': "",
      'logged_in': False
    }, autoescape=False)
  template = loader.get_template('browse-projects.html')
  return HttpResponse(template.render(context))  

@ensure_csrf_cookie
def my_projects(request):

  # if profile_query.count() > 0:
  #   profile = profile_query.fetch()
  #   blob_key = profile[0].to_dict()['blob_key']
  #   profile_url = images.get_serving_url(blob_key)
  # else:
  #   profile_url = ""

  if request.GET.__contains__("key"):  
    rfp_img_key = request.GET.__getitem__("key")
    rfp_img_url = images.get_serving_url(rfp_img_key)
  else:
    rfp_img_url = ""

  if request.GET.__contains__("rfp_key"):  
    rfp_img_upload_key = request.GET.__getitem__("rfp_key")
    rfp_img_upload_url = blobstore.create_upload_url('/upload-rfp-photo/%s' % rfp_img_upload_key)
  else:
    rfp_img_upload_url = ""

  user = users.get_current_user()
  if user:
    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('/'),
      'logged_in': True,
      'rfp_img_url': rfp_img_url,
      'rfp_img_upload_url': rfp_img_upload_url
    }, autoescape=False)
  else:
    return HttpResponseRedirect('/browse-projects.html')
  
  template = loader.get_template('my-projects.html')
  return HttpResponse(template.render(context))  

@ensure_csrf_cookie
def my_profile(request):
  user = users.get_current_user()
  if user:
    profile_query = UserPhoto.query(UserPhoto.user == user.user_id())
    if profile_query.count() > 0:
      profile = profile_query.fetch()
      profile_url = images.get_serving_url(profile[0].to_dict()['blob_key'])
    elif request.GET.__contains__("key"):  
      profile_url = images.get_serving_url(request.GET.__getitem__("key"))
    else:
      profile_url = "" 

    profile_query = Profile.query(Profile.user == user.user_id())
    if profile_query.count() > 0:
      profile = profile_query.fetch()
      profile_info = json.dumps(profile[0].to_dict())
    else:
      profile_info = None

    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('/'),
      'logged_in': True,
      'profile_url': profile_url,
      'profile_info': profile_info,
      'profile_upload_url' : blobstore.create_upload_url('/upload-profile-photo.html')
    }, autoescape=False)
    template = loader.get_template('my-profile.html')
  else:
    context = Context({
      'user_name': "",
      'login_url': users.create_login_url('/'),
      'logout_url': "",
      'logged_in': False
    }, autoescape=False)
    template = loader.get_template('browse-projects.html')
  return HttpResponse(template.render(context))  

def test(request):
  upload_url = blobstore.create_upload_url('/upload-rfp-photo/12345')

  # profile_query = UserPhoto.query(UserPhoto.user == users.get_current_user().user_id())
  # profile = profile_query.fetch()
  # print profile[0].to_dict()['blob_key']
  profile_query = RfpPhoto.query(RfpPhoto.rfp_key == '12345')
  profile = profile_query.fetch()

  if profile_query.count() > 0:
    profile = profile_query.fetch()
    blob_key = profile[0].to_dict()['blob_key']
    profile_url = images.get_serving_url(blob_key)
  else:
    profile_url = ""

  template = loader.get_template('test.html')
  # # Context is a normal Python dictionary whose keys can be accessed in the template index.html
  context = Context({
    'url': upload_url,
    'profile_url': profile_url
  })
  context.update(csrf(request))
  return HttpResponse(template.render(context))

def profile_photo_upload_handler(request):
  image = request.FILES['file']
  image_key = image.blobstore_info.key()
  user_photo = UserPhoto(user=users.get_current_user().user_id(),
                         blob_key=image_key)
  user_photo.put()
  return HttpResponseRedirect('/my-profile.html?key='+str(image_key))

def rfp_photo_upload_handler(request, rfp_key):
  image = request.FILES['file']
  image_key = image.blobstore_info.key()
  rfp_photo = RfpPhoto(rfp_key=rfp_key,
                       blob_key=image_key)
  rfp_photo.put()
  return HttpResponseRedirect('/my-projects.html?key=%s&rfp=%s' % (str(image_key), rfp_key))

