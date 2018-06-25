import random
from _testcapi import raise_exception

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.apps.verifications import serializers
from meiduo_mall.apps.verifications.constants import MAX_TIME_IMAGE_CODE, SMS_TIME, TMP_ID, SEND_SMS_TIME
from meiduo_mall.apps.verifications.serializers import ImageCodeCheckSerializer
from meiduo_mall.libs.captcha.captcha import captcha

# 图片验证码
from meiduo_mall.libs.yuntongxun.sms import CCP


class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        """获取图片验证码"""
        text, image = captcha.generate_captcha()
        # 获取redis连接对象
        redis_conn = get_redis_connection('Image_code')
        # 存储在redis中
        redis_conn.setex('img_%s' % image_code_id, MAX_TIME_IMAGE_CODE, text)
        print(redis_conn)
        return HttpResponse(image, content_type='images/jpg')


# GET/sms_codes/?\{moblie}/?image_code_id=xxxx&image_code_text=xxxx
# 短信验证
class SMSImageCode(GenericAPIView):
    """
        检查图片验证码
        检查是否在60s内有发送记录
        生成短信验证码
        保存短信验证码与发送记录
        发送短信
    """
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, moblie):
        print('ceshi', request.query_params)
        serializer1 = self.get_serializer(data=request.query_params)
        # serializer1 = ImageCodeCheckSerializer(data=request.query_params)
        # 这种方式无法在序列化器validate中用self.context['xx'].kwargs['xx']
        serializer1.is_valid(raise_exception=True)
        # 随机生成6位手机验证码
        moblie_code = '%06d' % random.randint(0, 999999)
        # 验证完毕，进行redis批量操作,提高redis执行效率
        redis_conn = get_redis_connection('Image_code')
        p1 = redis_conn.pipeline()
        p1.setex('send_flag_%s' % moblie, SEND_SMS_TIME, 1)
        p1.setex('sms_%s' % moblie, SMS_TIME, moblie_code)
        p1.execute()
        # ccp = CCP()
        # time = str(SMS_TIME / 60)
        # ccp.send_template_sms(moblie, [moblie_code, time], TMP_ID)
        print('发送验证码', moblie_code)
        return Response({'message': 'OK'}, status.HTTP_200_OK)
