from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response,render,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from xena import local_settings
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.


@csrf_protect
def user_login(request):
        context = RequestContext(request)
        if(request.method == "POST"):
                email = request.POST.get('email')
                password = request.POST.get('password')
                user = authenticate(username=email, password=password)
                if user is not None:
                        login(request, user)
                        return HttpResponseRedirect('/default_rule')
#                         return render(request,'default_rule.html')
                else:
                        messages.error(request,'Invalid Credentials')
                return render(request,'login.html')
        return render(request,'login.html')

def user_logout(request):
    logout(request)
    messages.success(request,"Successfully logged out")
    return redirect('/')

#persistent cookie
"""def set_cookie(response, key, value, days_expire=7):
    max_age = days_expire * 24 * 60 * 60

    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires,
                        domain=SESSION_COOKIE_DOMAIN,
                        secure=None)

	#delete cookie on expire and logout
def delete_cookie(response, key):
    response.delete_cookie(key)
"""