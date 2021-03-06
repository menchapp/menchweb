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

# TODOS
# - dont get user_id until we're sure user is defined
# - update profile instead of creating new entry

def home(request):
  return http.HttpResponse('Hello World!')

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

#########################################################
# Helpers
#########################################################

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

class DatetimeEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif isinstance(obj, datetime.date):
      return obj.strftime('%Y-%m-%d')
    # Let the base class default method raise the TypeError
    return json.JSONEncoder.default(self, obj)  

#########################################################
# RFPs
#########################################################

def get_my_rfp(request):
  user = users.get_current_user()
  if user:
    rfp_query = Rfp.query(Rfp.user == user.user_id())
    if rfp_query.count() > 0:
      rfps = rfp_query.fetch()
      rfps_dict = [rfp.to_dict() for rfp in rfps]
      return HttpResponse(json.dumps({'rfps': rfps_dict}, cls=DatetimeEncoder), content_type="application/json")
  return HttpResponse(json.dumps({'rfps': None}), content_type="application/json")

def get_rfp(request):
  user = users.get_current_user()
  if user:
    rfp_query = Rfp.query(Rfp.user != user.user_id())
  else: 
    rfp_query = Rfp.query()
  if rfp_query.count() > 0:
    rfps = rfp_query.fetch()
    rfps_dict = [rfp.to_dict() for rfp in rfps]
    return HttpResponse(json.dumps({'rfps': rfps_dict}, cls=DatetimeEncoder), content_type="application/json")
  return HttpResponse(json.dumps({'rfps': None}), content_type="application/json")

def rfp(request, rfp_key):
  user = users.get_current_user()
  print rfp_key

  if user:
    rfp = Rfp.get_by_id(int(rfp_key))
    mine = False
    if rfp:
      rfp_info = json.dumps(rfp.to_dict(), cls=DatetimeEncoder)
      if rfp.to_dict()['user'] == user.user_id():
        mine = True
    else:
      rfp_info = None

    submission_img_url = ""
    submission_id = ""

    if not mine: # if this RFP was not created by the current user.
      submission_query = Submission.query(Submission.user == user.user_id())
      if submission_query.count() > 0:
        submissions = submission_query.fetch()
        for s in submissions:
          s_dict = s.to_dict()
          if s_dict['rfp_key'] == rfp_key:
            submission_img_url = images.get_serving_url(s_dict['blob_key'])
            submission_id = s_dict['id']
      if request.GET.__contains__("key"):  
        submission_img_url = images.get_serving_url(request.GET.__getitem__("key"))
      if request.GET.__contains__("sid"):  
        submission_id = request.GET.__getitem__("sid")

    context = Context({
      'user_name': user.nickname(),
      'login_url': "",
      'logout_url': users.create_logout_url('/'),
      'logged_in': True,
      'rfp_info': rfp_info,
      'mine' : mine,
      'submission_id' : submission_id,
      'submission_img_url' : submission_img_url,
      'submission_img_upload_url': blobstore.create_upload_url('/upload-rfp-submission/%s' % rfp_key)
    }, autoescape=False)
    template = loader.get_template('rfp.html')
    return HttpResponse(template.render(context))  
  return HttpResponseRedirect('/browse-projects.html')

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
            userName=data['userName'],
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
  return HttpResponse(
    json.dumps({'url':  blobstore.create_upload_url('/upload-rfp-photo/%s' % str(rfp.key.id()))}), content_type="application/json")

#########################################################
# Submissions
#########################################################

def delete_submission(request, id):
  if users.get_current_user():
    user_id = users.get_current_user().user_id()
  else:
    return HttpResponse(content='Login required', content_type=None, status=401)

  if request.method == 'POST':
    submission = Submission.get_by_id(int(id))
    if submission and submission.to_dict()['user'] == user_id:
      submission.key.delete()
      return HttpResponse('Success')
  return HttpResponse(content='Request failed', content_type=None, status=401)

def get_submissions(request, rfp_key):
  user = users.get_current_user()
  if user:
    rfp = Rfp.get_by_id(int(rfp_key))
    if rfp:
      #rfp_info = json.dumps(rfp.to_dict(), cls=DatetimeEncoder)
      if rfp.to_dict()['user'] != user.user_id():
        return HttpResponse(json.dumps({'submissions': None}), content_type="application/json")

    submission_query = Submission.query(Submission.rfp_key == rfp_key)
    if submission_query.count() > 0:
      submissions = submission_query.fetch()
      submission_img_urls = []
      for s in submissions:
        submission_img_urls.append({
          'url': images.get_serving_url(s.to_dict()['blob_key']),
          'user': s.to_dict()['user'],
          'id': s.to_dict()['id'],
          'liked': False
        })
    return HttpResponse(json.dumps({'submissions': submission_img_urls}), content_type="application/json")
  return HttpResponse(json.dumps({'submissions': None}), content_type="application/json")

#########################################################
# Purchase
#########################################################

def purchase(request):
  user = users.get_current_user()
  if user == None:
    return HttpResponse("User not logged in.")  
  if request.method != 'POST':
    return HttpResponse("Purchase only accepts POSTs")  

  data = json.loads(request.body)
  rfp = Rfp.get_by_id(data['rfp'])
  if rfp:
    if rfp.to_dict()['user'] != user.user_id():
      return HttpResponse("Can only purchase photos for RFPs you created", content_type=None, status=401)

  purchase = Purchase(rfp_id=str(data['rfp']),
                 submission_id=str(data['submission']),
                 user_id=str(data['user']))

  purchase.put()
  return HttpResponse("Success!")  

#########################################################
# User profiles
#########################################################

def save_profile(request):
  user = users.get_current_user()
  if user == None:
    return HttpResponse("User not logged in.")  
  if request.method != 'POST':
    return HttpResponse("Add RFP only accepts POSTs")  
  print request.body
  data = json.loads(request.body)

  profile = Profile.query(Profile.user == user.user_id())
  if profile.count() > 0:
    profile.fetch()[0].key.delete()

  profile = Profile(brand="",
                 user=user.user_id(),
                 name=data['name'],
                 email=data['email'],
                 phone=data['phone'],
                 instagram=data['instagram'],
                 location=data['location'],
                 website=data['website'],
                 about=data['about'])

  profile.put()
  return HttpResponse("Success!")  

def profile(request, user_id):
  user = users.get_current_user()
  if user == None:
    return HttpResponse("User not logged in.")  

  profile_query = Profile.query(Profile.user == user_id)
  if profile_query.count() > 0:
    profile = profile_query.fetch()  
    profile_info = json.dumps(profile[0].to_dict())
  else:
    profile_info = None
  img_query = UserPhoto.query(UserPhoto.user == user_id)
  if img_query.count() > 0:
    img = img_query.fetch()  
    img_url = images.get_serving_url(img[0].to_dict()['blob_key'])
  else:
    img_url = None

  context = Context({
    'user_name': user.nickname(),
    'login_url': "",
    'logout_url': users.create_logout_url('/'),
    'logged_in': True,
    'profile_url' : img_url,
    'profile_info': profile_info
  }, autoescape=False)
  template = loader.get_template('profile.html')
  return HttpResponse(template.render(context))  

@ensure_csrf_cookie
def my_profile(request):
  user = users.get_current_user()
  if user:
    if request.GET.__contains__("key"):  
      profile_url = images.get_serving_url(request.GET.__getitem__("key"))
    else: 
      profile_query = UserPhoto.query(UserPhoto.user == user.user_id())
      if profile_query.count() > 0:
        profile = profile_query.fetch()
        profile_url = images.get_serving_url(profile[0].to_dict()['blob_key'])
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

#########################################################
# Photo handlers
#########################################################

def profile_photo_upload_handler(request):
  image = request.FILES['file']
  image_key = image.blobstore_info.key()
  user_id = users.get_current_user().user_id()

  profile_photo_query = UserPhoto.query(UserPhoto.user == user_id)
  if profile_photo_query.count() > 0:
    profile_photo = profile_photo_query.fetch()
    profile_photo[0].key.delete()

  user_photo = UserPhoto(user=user_id,
                         blob_key=image_key)
  user_photo.put()
  return HttpResponseRedirect('/my-profile.html?key='+str(image_key))

def submission_photo_upload_handler(request, rfp_key):
  user_id = users.get_current_user().user_id()
  image = request.FILES['file']
  image_key = image.blobstore_info.key()

  submission_query = Submission.query(Submission.user == user_id)
  if submission_query.count() > 0:
    submission = submission_query.fetch()
    submission[0].blob_key = image_key
    submission[0].put()
  else:
    submission = Submission(user=user_id,
                          rfp_key=rfp_key,
                          blob_key=image_key)
    submission.put()
  return HttpResponseRedirect('/rfp/%s?key=%s&sid=%d' % (rfp_key, str(image_key), submission.key.id()))

def rfp_photo_upload_handler(request, rfp_key):
  image = request.FILES['file']
  image_key = image.blobstore_info.key()
  rfp_photo = RfpPhoto(rfp_key=rfp_key,
                       blob_key=image_key)
  rfp_photo.put()
  return HttpResponseRedirect('/my-projects.html?key=%s&rfp=%s' % (str(image_key), rfp_key))


#########################################################
# Main pages
#########################################################

@ensure_csrf_cookie
def home(request):
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
  template = loader.get_template('home.html')
  return HttpResponse(template.render(context))  

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


