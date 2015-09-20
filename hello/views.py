from google.appengine.api import users
from django import http
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import Context, loader 

def home(request):
	return http.HttpResponse('Hello World!')

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

  template = loader.get_template('beta.html')
  return HttpResponse(template.render(context))  

def test(request):
  user = users.get_current_user()
  if user:
    name = user.nickname()
    login_url = users.create_logout_url('/')
    greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
               (user.nickname(), users.create_logout_url('/')))
  else:
    name = "friend"
    login_url = users.create_login_url('/')
    greeting = ('<a href="%s">Sign in or register</a>.' %
                users.create_login_url('/'))

  template = loader.get_template('test.html')
  # Context is a normal Python dictionary whose keys can be accessed in the template index.html
  context = Context({
    'test': login_url,
    'name': name
  })
  return HttpResponse(template.render(context))
