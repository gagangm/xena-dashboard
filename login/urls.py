from django.conf.urls import url
from django.contrib import admin
from login.views import *

urlpatterns = [
	url(r'^$', user_login),
	url(r'^user_logout/$',user_logout)
]
