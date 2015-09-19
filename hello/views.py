from django import http
from django.shortcuts import render_to_response
from django.template import Context, loader

def home(request):
	return http.HttpResponse('Hello World!')

def beta(request):
	return render_to_response('beta.html')
