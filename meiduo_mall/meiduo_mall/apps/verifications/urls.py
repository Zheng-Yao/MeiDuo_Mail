from django.conf.urls import url

from meiduo_mall.apps.verifications import views

urlpatterns = [
    url(r'image_code/(?P<image_code_id>.+)/$', views.ImageCodeView.as_view()),
    url(r'sms_codes/(?P<moblie>1[3,9]\d{9})/$', views.SMSImageCode.as_view()),
]
