from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response,render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from xena import local_settings
from shared.redis_connection import get_connection
import json
import re
import MySQLdb
from shared.constants import *
from models import *
from login.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime
from configure_rules.models import auditModel
from .forms import *
# Create your views here.

@login_required
@csrf_protect
def default_rule(request):
	if request.user.is_authenticated:
		return render(request,'default_rule.htm')
	
	

def get_con_and_rules():
	r = get_connection('default')
	rules = ""
	if r is None:
		print "Redis Con failed" #todo should render some exception page here
	if(r.exists(Z_G_RULES)):
		rules = r.zrange(Z_G_RULES,0,-1,withscores=True)
		return r,rules
	else:
		return r, rules


def get_con_and_sid_rules(key_sid):
	r = get_connection('default')
	rules = ""
	if r is None:
		print "Redis Con failed" #todo should render some exception page here
	if(r.exists(key_sid)):
		rules = r.zrange(key_sid,0,-1,withscores=True)
		#rules = [r for list(r) in rules]
		return rules
	else:	
		return rules
	
			

@csrf_exempt
def get_redis_rules(request):
	
	if(request.method == "POST"):
		data = json.loads(request.body)
		sid = data['sid']		
		r,g_rules = get_con_and_rules()

		# append false to all rules in global rules, used to diff private and global
		g_mark_r = [list(g_rule) for g_rule in g_rules]
		for obj in g_mark_r:
			obj.append('false')
		if sid != 0 :
			key_sid = Z_SID_RULE_PREFIX+str(sid)
			sid_rules = get_con_and_sid_rules(key_sid)
			if len(sid_rules) != 0:
				sid_mark_r = [list(sid_rule) for sid_rule in sid_rules]
				for obj in sid_mark_r:
					obj.append('true')
				for g_rule_obj in g_mark_r[0:]:				
					g_rule = g_rule_obj[0]
					g_rule_name = g_rule.split(':')[0]
					for sid_rule_obj in sid_mark_r[0:]:
						sid_rule = sid_rule_obj[0]
						sid_rule_name = sid_rule.split(':')[0]
						if(g_rule_name == sid_rule_name):
							g_mark_r.remove(g_rule_obj)
				for obj in g_mark_r:
					sid_mark_r.append(obj)
				sid_mark_r.sort(key=lambda x: x[1])

				return HttpResponse(json.dumps(sid_mark_r),content_type = 'application/json')	
			return HttpResponse(json.dumps(g_mark_r),content_type = 'application/json')
		else :
			return HttpResponse(json.dumps(g_mark_r),content_type = 'application/json')


@csrf_exempt
def get_redis_rule_parameters(request):
	if(request.method == "POST"):
		r = get_connection('default')
		if r is None:
			print "Redis Con failed" #todo should render some exception page here	
		features = r.hgetall(K_HASH_FEATURES)
		constants = r.hgetall('H:G_RULES_CONSTANT')
		pct_const = r.hgetall('H:G:RULES_PERC')
		return HttpResponse(json.dumps({'features':features,'constants':constants,'pct_const':pct_const}),content_type = 'application/json')


@csrf_exempt
def save_rules_to_redis(request):
	if(request.method == "POST"):
		rule_str = ""
		form_data = json.loads(request.body)
		rule = form_data['data']
		old_vals = form_data['old']
		new_vals = form_data['new']
		sid = int(form_data['sid'])
		rule_name = rule['rule_name']
		score = rule['score']	
		timestamp = datetime.datetime.utcnow().strftime('%d %b-%Y %H:%M:%S')
		user = User.objects.get(username=request.user)
		rule_str +=rule_name+':'+str(rule['status'])+':'+str(rule['mode'])+':'+str(rule['break_on_match'])+':'+rule['key_strategy']+':'+str(rule['rc_auto'])+':'+rule['response_code']+':'+str(rule['reason_code'])+':'+rule['ttl']+':{'
	
		for cond in rule['condition_type_detail']:
			if cond['type'] == '0':
				if(cond['val_param'] == 'true'):
					bool_val = 1
				else:
					bool_val =0
				rule_str += '('+cond['feature_lhs']+'|'+cond['type']+'|'+cond['operator']+'|'+str(bool_val)+')'	
			elif cond['type'] == '1':
				rule_str += '('+cond['feature_lhs']+'|'+cond['type']+'|'+cond['operator']+'|'+cond['val_param']+')'
			elif cond['type'] == '2':
				rule_str += '('+cond['feature_lhs']+'|'+cond['type']+'|'+cond['operator']+'|'+cond['val_param']+'|'+cond['feature_rhs']+')'
			elif cond['type'] == '3' or cond['type'] == '5' or cond['type'] == '6':
				if cond['type'] == '6':
					if(cond['operator'] == 'contains'):
						cond['operator']= '??'
					else:
						cond['operator']= '$#'
				rule_str += '('+cond['feature_lhs']+'|'+cond['type']+'|'+cond['operator']+'|'+cond['feature_rhs']+')'
			elif cond['type'] == '4':
				if(cond['operator'] == 'sismember'):
					cond['operator']= '?#'
				else:
					cond['operator']= '?$'
				rule_str += '('+cond['feature_lhs']+'|'+cond['type']+'|'+cond['operator']+'|'+cond['pattern_string']+')'
		
		rule_str +='}'

		# add and between conditions
		if len(rule['condition_type_detail']) > 1:
			rule_str = re.sub(r'\)\(',')&(',rule_str)
		
		r,g_rules = get_con_and_rules()

		if (sid == 0):
			# if rulename already exists delete and add, else just add
			for rule_obj in g_rules:
				rule = rule_obj[0]
				rule_score = rule_obj[1]
				if re.search(rule_name+r':',rule):
					r.zrem(Z_G_RULES,rule)
					r.zadd(Z_G_RULES,score,rule_str)
					r.incrby(K_G_RULE_TABLE_V,amount=1)
					if(len(old_vals) != 0):
						obj = auditModel.objects.create(modified_by=user,name=rule_name,old_fields=old_vals,new_fields=new_vals,modified_on=timestamp)
						obj.save()
					return HttpResponse(True)
			r.zadd(Z_G_RULES,score,rule_str)
			r.incrby(K_G_RULE_TABLE_V,amount=1)
			return HttpResponse(True)
		else:
			
			key_sid = Z_SID_RULE_PREFIX+str(sid)
			version_sid = K_SID_TABLE_V_PREFIX+str(sid)
			sid_rules = get_con_and_sid_rules(key_sid)

			"""# if rule str is same as global then dont add it to private 
			for g_rule_obj in g_rules:
				g_rule = g_rule_obj[0]
				g_rule_score = g_rule_obj[1]
				if(rule_str == g_rule):
					print rule_str
					return HttpResponse(False)"""

			# if editing already existing rule delete and add
			for rule_obj in sid_rules:
				sid_rule = rule_obj[0]
				sid_rule_score = rule_obj[1]
				if re.search(rule_name+r':',sid_rule):
					r.zrem(key_sid,sid_rule)
					r.zadd(key_sid,score,rule_str)
					r.hincrby(version_sid,K_SID_TABLE_V_FIELD,amount=1)
					if(len(old_vals) != 0):
						obj = auditModel.objects.create(modified_by=user,name=str(sid)+':'+rule_name,old_fields=old_vals,new_fields=new_vals,modified_on=timestamp)
						obj.save()
					return HttpResponse(True)

			# if editing a global rule save it to private
			for g_rule_obj in g_rules:
				g_rule = g_rule_obj[0]
				g_rule_score = g_rule_obj[0]
				if re.search(rule_name+r':',g_rule) and rule_name != '':
					
					r.zadd(key_sid,score,rule_str)
					r.hincrby(version_sid,K_SID_TABLE_V_FIELD,amount=1)
					if(len(old_vals) != 0):
						obj = auditModel.objects.create(modified_by=user,name=str(sid)+':'+rule_name,old_fields=old_vals,new_fields=new_vals,modified_on=timestamp)
						obj.save()
					return HttpResponse(True)

			# if rule is completely new
			r.zadd(key_sid,score,rule_str)
			r.hincrby(version_sid,K_SID_TABLE_V_FIELD,amount=1)
			return HttpResponse(True)
	
@csrf_exempt 
def get_list_of_sids(request):
	#sids = []
	if request.method == "GET":
	
		db = MySQLdb.connect("104.154.25.198","ssuser","jnvskjvnksdvnslczfdszv","prod-mysql-db")
		cursor = db.cursor()
		query = "select internal_sid,site_url from subscriber where status=1;"
		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		rec_list = []
		default_table = {
			"Key" : "Global Rule Table",
			"Value" : 0
		}
		rec_list.append(default_table)
		for result in results:
			rec_obj = {"Key":str(result[0])+' '+result[1],"Value":result[0]}
			rec_list.append(rec_obj)
		return HttpResponse(json.dumps(rec_list),content_type = 'application/json')
	
	
def get_rule_names(request):
	if(request.method == "GET"):
		rulename = request.GET.get('name')
		sid = int(request.GET.get('sid'))
		r = get_connection('default')
		if(sid == 0):
			rules = r.zrange(Z_G_RULES,0,-1,withscores=False)
		else:
			key_sid = Z_SID_RULE_PREFIX+str(sid)
			rules = r.zrange(key_sid,0,-1,withscores=False)
		
		#get rule name
		for rule in rules:
			rule_name = rule.split(':')[0]
			if rule_name == rulename:
				return HttpResponse('true')
			
		return HttpResponse('false')

@login_required
@csrf_exempt
def audit_log(request):
	page = request.GET.get('page',1)
	audit_data = auditModel.objects.all().order_by('-modified_on')
	audit_data = [{'name':record.name,'user':record.modified_by,\
					'old_value':json.dumps(record.old_fields),
					'new_value':json.dumps(record.new_fields),'timestamp':record.modified_on} for record in audit_data]
	paginator        = Paginator(audit_data, 5)
	try:
		audit_data = paginator.page(page)
	except PageNotAnInteger:
		audit_data = paginator.page(page)
	except EmptyPage:
		audit_data = paginator.page(paginator.num_pages)
	return render(request,'audit_log.html',{'data':audit_data})


@login_required
@csrf_exempt
def analytics(request):
	return render(request,'analytics.html')


@login_required
@csrf_exempt
def rule_constants(request):
	form = ConstantForm()
	r=get_connection('default')
	constants = r.hgetall(K_HASH_CONSTANT)
	constants = parse_dict(constants)
	print "constants",constants
	page = request.GET.get('page',1)
	paginator        = Paginator(constants, 10)
	try:
		constants = paginator.page(page)
	except PageNotAnInteger:
		constants = paginator.page(page)
	except EmptyPage:
		constants = paginator.page(paginator.num_pages)
	if request.method == "POST":
		form = ConstantForm(data=request.POST)
		if form.is_valid():
			name = form.cleaned_data['constant_name']
			value = int(form.cleaned_data['constant_value'])
			r.hset(K_HASH_CONSTANT,name,value)
			r.incrby(K_VTABLE_CONSTANT,amount=1)
			return HttpResponseRedirect('/rule_constants/')
			
		
	return render(request,'constants.html',{'is_authenticated' : 'true','form':form,'constants':constants})


@login_required
@csrf_exempt
def rule_percentges(request):
	form = PercentForm()
	r=get_connection('default')
	percents = r.hgetall(K_HASH_PERC)
	percents = parse_dict(percents)
	print "percentss",percents
	page = request.GET.get('page',1)
	paginator        = Paginator(percents, 10)
	try:
		percents = paginator.page(page)
	except PageNotAnInteger:
		percents = paginator.page(page)
	except EmptyPage:
		percents = paginator.page(paginator.num_pages)
		
	if request.method == "POST":
		form = PercentForm(data=request.POST)
		if form.is_valid():
			name = form.cleaned_data['percent_name']
			value = int(form.cleaned_data['percent_value'])
			r.hset(K_HASH_PERC,name,value)
			r.incrby(K_VTABLE_PERC,amount=1)
			return HttpResponseRedirect('/rule_percentages/')
			
		
	return render(request,'percents.html',{'is_authenticated' : 'true','form':form,'percents':percents})


def parse_dict(obj):
	vals_list = []
	for k,v in obj.iteritems():
		val_obj = {
						'name':k,
						'value':v
					};
		vals_list.append(val_obj)
	return vals_list
	
	



