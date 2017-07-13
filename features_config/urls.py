from django.conf.urls import url
from .views import *
from features_config.views import save_feature_to_redis, get_feature_names

urlpatterns = [
        url(r'^list_features/$', list_features),
        url(r'^list_features/page(?P<page>[0-9]+)/$', list_features),
        url(r'^save_feature_to_redis/$',save_feature_to_redis),
        url(r'get_feature_names',get_feature_names)
       ]