from django.conf.urls import url
from .views import *
from configure_rules.views import get_rule_names, audit_log, analytics,\
	rule_constants, rule_percentges
from django.views.generic import TemplateView

urlpatterns = [
	url(r'^default_rule/$',default_rule),
	url(r'^get_redis_rules/$',get_redis_rules),
	url(r'^get_redis_rule_parameters/$',get_redis_rule_parameters),
	url(r'save_rules_to_redis/$',save_rules_to_redis),
	url(r'get_list_of_sids/$',get_list_of_sids),
	url(r'get_rule_names/$',get_rule_names),
	url(r'audit_log/$',audit_log),
	url(r'^audit_log/page(?P<page>[0-9]+)/$', audit_log),
	url(r'rule_constants/$',rule_constants),
	url(r'^rule_constants/page(?P<page>[0-9]+)/$', rule_constants),
	url(r'rule_percentages/$',rule_percentges),
	url(r'^rule_percentages/page(?P<page>[0-9]+)/$', rule_percentges),
	url(r'^analytics/', analytics)
]
