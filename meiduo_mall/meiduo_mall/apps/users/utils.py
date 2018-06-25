import re
from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
        自定义jwt认证成功返回数据
        :param token: 生成的token令牌
        :param user: 前面验证通过以后得到的用户模型对象
        :param request: 本次用户提交请求信息
        :return: json，前端希望提供的数据
        """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
       根据帐号获取user对象
       :param account: 账号，可以是用户名，也可以是手机号
       :return: User对象 或者 None
    """
    try:
        if re.match(r'1[3-9]\d{9}', account):
            user = User.objects.get(moblie=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    return user


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
