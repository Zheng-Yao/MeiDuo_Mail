from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
# 导入jwt实现的登陆视图功能

from . import views

urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^user/$', views.UserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token, name='authorizations'),
]
