from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from jsonfield import JSONField
import collections

class auditModel(models.Model):
    name = models.CharField(max_length=16)
    old_fields = JSONField(blank=True,load_kwargs={'object_pairs_hook': collections.OrderedDict})
    new_fields = JSONField(blank=True,load_kwargs={'object_pairs_hook': collections.OrderedDict})
    modified_by = models.ForeignKey(User,null=False,related_name='rule_modified_by')
    modified_on = models.DateTimeField(auto_now=True,null=True)