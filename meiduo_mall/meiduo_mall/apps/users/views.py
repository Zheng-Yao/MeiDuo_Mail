from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import CreateUserSerializer


class UsernameCountView(APIView):
    """检查用户是否存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'count': count,
            'username': username
        }
        return Response(data)


class MobileCountView(APIView):
    """检查手机号码是否已经注册"""

    def get(self, request, mobile):
        count = User.objects.filter(moblie=mobile).count()
        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data)


class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer
