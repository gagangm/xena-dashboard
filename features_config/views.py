from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from .forms import FeaturesForm
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django import forms
from shared.redis_connection import get_connection
import json,re
from django.contrib.auth.decorators import login_required
from shared.constants import *

@login_required
@csrf_exempt
def list_features(request):
	r=get_connection('default')
	features = r.hgetall(K_HASH_FEATURES)
	features_json = parse_redis_features(features)
	page = request.GET.get('page',1)
	paginator        = Paginator(features_json, 10)
	try:
		features_list = paginator.page(page)
	except PageNotAnInteger:
		features_list = paginator.page(page)
	except EmptyPage:
		features_list = paginator.page(paginator.num_pages)
	
	return render(request,'features.html',{'is_authenticated' : 'true','features_json':features_list})


def parse_redis_features(features):
	features_json = []
	for feature_name,feature_def in features.items(): 				
		feature_type = re.match(r'(\w+)\(',feature_def).group(1)
		if feature_type in FEATURE_WITH_FIELDS: 
			split_def = re.match(r'\w+\((\w+[._]?\w+),(.*)\)',feature_def)
			feature_obj = {'feature_name': feature_name,
							'feature_type': feature_type,
							'on_field':split_def.group(1),
							'query_str':split_def.group(2)
							};
			features_json.append(feature_obj)
		else:
			query_str = re.match(r'\w+\((.*)\)',feature_def).group(1)
			feature_obj = {'feature_name': feature_name,
							'feature_type': feature_type,
							'on_field':'Not Applicable',
							'query_str':query_str
							};
			features_json.append(feature_obj)
	return features_json
	
@csrf_exempt
def save_feature_to_redis(request):
	
	if request.method=="POST":
		r=get_connection('default')
		formdata = json.loads(request.body)
		if  formdata['feature_type'] in FEATURE_WITH_FIELDS:
			feature_def = formdata['feature_type']+'('+formdata['feature_onfield']+','+formdata['query_str']+')'
		elif len(formdata) == 3:
			feature_def = formdata['feature_type']+'('+formdata['query_str']+')'
		else:
			feature_def = formdata['feature_type']+'({"'+formdata['req_key']+'":'+formdata['req_value']+'})'
		# write feature to redis
		r.hset(K_HASH_FEATURES,formdata['feature_name'],feature_def)
		r.incrby(K_VTABLE_FEATURES,amount=1)
		return HttpResponse(True)
	
	
def get_feature_names(request):
	if(request.method=="GET"):
		name = request.GET.get('name')
		r = get_connection('default')
		feature_names = r.hkeys(K_HASH_FEATURES)
		for f in feature_names:
			if(f == name):
				return HttpResponse('true')
			
		return HttpResponse('false')
			
		

		
	
	
		
		
		
		
