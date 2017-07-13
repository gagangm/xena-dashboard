from django import forms
from django.forms.widgets import Select
from shared.constants import *

class FeaturesForm(forms.Form):
	feature_name = forms.CharField(required=True)
	feature_type = forms.ChoiceField(choices=feature_type,widget=Select,required=True)
	on_field = forms.ChoiceField(choices=type_on_fields,widget=Select,required=False)
	query_str = forms.CharField(required=False)
	plain_str = forms.CharField(required=False)
	