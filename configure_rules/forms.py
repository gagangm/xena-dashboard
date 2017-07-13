from django import forms
from django.forms.widgets import Select
from shared.constants import *

class ConstantForm(forms.Form):
        constant_name = forms.CharField(required=True)
        constant_value = forms.IntegerField(required=True)
        
class PercentForm(forms.Form):
        percent_name = forms.CharField(required=True)
        percent_value = forms.IntegerField(required=True)
